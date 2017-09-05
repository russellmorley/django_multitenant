
import logging
import uuid

from ..channel import MultitenantOrg
from ..channel import MultitenantOrgGroup
from ..channel import MultitenantPublicGroup
from ..channel import MultitenantUser
from ..decorators import connect
from ..decorators import disconnect
from ..decorators import disconnect_if_http_logged_out
from ..decorators import get_user_org_pk
from channels.auth import http_session_user
from channels.generic.websockets import JsonWebsocketConsumer
from channels.generic.websockets import WebsocketDemultiplexer
from channels.generic.websockets import WebsocketMultiplexer
from django.utils import six
from django.utils.module_loading import import_string
from rest_framework import status

logger = logging.getLogger(__name__)

from django.utils.decorators import method_decorator

http_session_user_m = method_decorator(http_session_user)


class MultitenantJsonWebsocketConsumer(JsonWebsocketConsumer):

  http_user = True
  strict_ordering = True

  disconnect_on_logged_out = True

  @http_session_user_m
  @connect()
  def connect(self, message, multiplexer, **kwargs):
    logger.debug("[CONNECT] message:{} stream:{} kwargs:{}".format(message.content, multiplexer.stream, kwargs))
    self.connect_impl(message, multiplexer, **kwargs)

  def connect_impl(self, message, multiplexer, **kwargs):
    pass

  @disconnect()
  def disconnect(self, message, multiplexer, **kwargs):
    logger.debug("[DISCONNECT] message:{} stream:{} kwargs:{}".format(message.content, multiplexer.stream, kwargs))
    self.disconnect_impl(message, multiplexer, **kwargs)

  def disconnect_impl(self, message, multiplexer, **kwargs):
    pass

  @http_session_user_m
  def raw_receive(self, message, **kwargs):
    logger.debug("[RAW_RECEIVE] message:{} kwargs:{}".format(message.content, kwargs))
    kwargs["user"] = message.user
    raw_receive = super(MultitenantJsonWebsocketConsumer, self).raw_receive
    if self.disconnect_on_logged_out:
      raw_receive = disconnect_if_http_logged_out()(raw_receive)
    raw_receive(message, **kwargs)

  def receive(self, content, multiplexer, **kwargs):
    logger.debug("[RECEIVE] content:{} stream:{} kwargs:{}".format(content, multiplexer.stream, kwargs))
    op = content.pop("op", None)
    for_org = content.pop("for_org", None)
    user = kwargs.pop("user", None)
    if op == "connect":
      client = content.get("client", {}) or {}
      id = client.get("id")
      reply_channel = client.get("reply_channel")
      if reply_channel and self.message.reply_channel.name != reply_channel:
        orgid = get_user_org_pk(self.message.user)
        if orgid is not None:
          MultitenantUser(self.message.user.pk, orgid).discard(reply_channel)
          MultitenantOrg(orgid).discard(reply_channel)
      multiplexer.send(op, {
        "status": status.HTTP_200_OK,
        "client": {
          "id": id or uuid.uuid4().hex,
          "reply_channel": self.message.reply_channel.name
        }
      })
    self.receive_impl(user, op, for_org, content, multiplexer, **kwargs)


  def receive_impl(self, op, for_org, data_dict, multiplexer, **kwargs):
    pass


class MultiTenantMultiplexer(WebsocketMultiplexer):

  def send(self, op, data_dict):
    logger.debug("[MULTIPLEXER SEND]: stream:{}, op:{}, data_dict:{}".format(self.stream, op, data_dict))
    data_dict["op"] = op
    super(MultiTenantMultiplexer, self).send(data_dict)


class MultitenantDemultiplexer(WebsocketDemultiplexer):

  multiplexer_class = MultiTenantMultiplexer

  @classmethod
  def for_consumers(cls, consumers_dict={}):
    cls.consumers = {key: import_string(value) if isinstance(value, six.string_types) else value
      for key, value in consumers_dict.items()
    }
    return cls

  @classmethod
  def send_to_channel(cls, stream, channel, op, data_dict):
    multiplexer = cls.multiplexer_class(stream, channel)
    multiplexer.send(op, data_dict)
    return True

  @classmethod
  def send_to_user(cls, stream, user, op, data_dict):
    orgid = get_user_org_pk(user)
    group = MultitenantUser(user.pk, orgid)
    if group.exists():
      # can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = cls.multiplexer_class(stream, group)
      multiplexer.send(op, data_dict)
      return True
    return False

  @classmethod
  def send_to_org(cls, stream, orgid, op, data_dict):
    group = MultitenantOrg(orgid)
    if group.exists():
      # can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = cls.multiplexer_class(stream, group)
      multiplexer.send(op, data_dict)
      return True
    return False

  @classmethod
  def send_to_public_group(cls, stream, public_group_name, op, data_dict):
    group = MultitenantPublicGroup(public_group_name)
    if group.exists():
      # can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = cls.multiplexer_class(stream, group)
      multiplexer.send(op, data_dict)
      return True
    return False

  @classmethod
  def send_to_org_group(cls, stream, org_group_name, orgid, op, data_dict):
    group = MultitenantOrgGroup(org_group_name, orgid)
    if group.exists():
      # can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = cls.multiplexer_class(stream, group)
      multiplexer.send(op, data_dict)
      return True
    return False
