
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import logging
import uuid

from . import status
from channels.channel import Channel
from channels.channel import Group
from channels.generic.websockets import JsonWebsocketConsumer
from channels.generic.websockets import WebsocketDemultiplexer
from channels.generic.websockets import WebsocketMultiplexer
from channels.security.websockets import allowed_hosts_only
from collections import defaultdict


logger = logging.getLogger(__name__)


class TenantConsumer(JsonWebsocketConsumer):

  permission_mapping = defaultdict(lambda: True)

  tenant_accessor = None

  http_user = True

  def connection_groups(self, **kwargs):
    groups = []
    user = getattr(self.message, "user", None)
    if user and user.is_authenticated:
      for group_name, user_class in self.groups:
        if isinstance(user, user_class):
          try:
            group = group_name.format(user=user).replace("None", "#")
            self.message.channel_layer.channel_layer.valid_group_name(group)
            groups.append(group)
          except (AttributeError, KeyError, TypeError, ValueError) as e:
            logger.debug("Ignored group tpl={} user={} {}:{}".format(group_name, user, e.__class__.__name__, e.message))
    return groups

  def get_handler(self, message, **kwargs):
    handler = super(TenantConsumer, self).get_handler(message, **kwargs)
    if self.message.channel.name == "websocket.connect":
      handler = allowed_hosts_only(handler)
    return handler

  def receive(self, content, multiplexer, **kwargs):
    user = getattr(self.message, "user", None)
    logger.debug("[{}:{}@{}] (receive)".format(self.message.channel.name, multiplexer.stream, user))
    close = False
    if self.http_user and (not user or user.is_anonymous):
      content.update({"status": status.STATUS_407_AUTHENTICATION_REQUIRED})
      close = True
    else:
      tenant = self.tenant_requested(content, user)
      cmd = content["cmd"].replace(":", "_")
      receive_handler = "receive_{}".format(cmd.replace("-", "_"))
      if hasattr(self, receive_handler):
        perm = self.permission_mapping[cmd]
        if (perm is True) or (perm is not False and self.user_has_perm_for_tenant(user, perm, tenant)):
          try:
            content.update(getattr(self, receive_handler)(content, multiplexer, user, tenant, **kwargs))
          except Exception as e:
            content.update({
              "status": status.STATUS_400_BAD_REQUEST,
              "response": {
                "target": "*",
                "error": str(e)
              }
            })
        else:
          content.update({"status": status.STATUS_401_UNAUTHORIZED})
      else:
        content.update({"status": status.STATUS_404_NOT_FOUND})
    multiplexer.send(content, close=close)
    logger.debug("[{}:{}@{}] (receive+send) msg={}".format(
      self.message.channel.name,
      multiplexer.stream,
      user,
      json.dumps(content, indent=2, sort_keys=True)
    ))

  def receive_helo(self, content, multiplexer, user, tenant, **kwargs):
    client = content["request"]["client"]
    client_id = client["id"] if client else uuid.uuid4().hex
    client_reply_channel = client["reply_channel"] if client else None
    if client_reply_channel and (client_reply_channel != self.message.reply_channel.name):
      for group in self.connection_groups(**kwargs):
        Group(group, channel_layer=self.message.channel_layer).discard(client_reply_channel)
    return {
      "status": status.STATUS_200_OK,
      "response": {
        "target": "client:*",
        "client": {
          "id": client_id,
          "reply_channel": self.message.reply_channel.name
        }
      }
    }

  def tenant_requested(self, content, user):
    if "tenant" in content:
      return content["tenant"]
    if self.tenant_accessor and user and user.is_authenticated:
      accessor = getattr(user, self.tenant_accessor)
      if callable(accessor):
        return accessor()
      return accessor
    return None

  def user_has_perm_for_tenant(self, user, perm, tenant):
    return True


class TenantMultiplexer(WebsocketMultiplexer):

  def send(self, payload, close=False):
    msg = self.encode(self.stream, payload)
    if close:
      msg["close"] = True
    self.reply_channel.send(msg)


class TenantDemultiplexer(WebsocketDemultiplexer):

  multiplexer_class = TenantMultiplexer

  @classmethod
  def for_consumers(cls, consumers={}):
    cls.consumers = consumers
    return cls


def tenant_multiplexer(stream, reply_channel):
  return TenantMultiplexer(stream, Channel(reply_channel[:]))
