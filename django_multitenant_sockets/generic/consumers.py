from channels.generic.websockets import WebsocketDemultiplexer, WebsocketMultiplexer, JsonWebsocketConsumer, WebsocketConsumer
from django.conf import settings
import logging
from django.utils.module_loading import import_string
from ..decorators import (
  connect, disconnect, get_user_org_pk, 
  disconnect_if_http_logged_out as disconnect_if_http_logged_out_decorator
)
from ..channel import MultitenantUser, MultitenantOrg, MultitenantOrgGroup, MultitenantPublicGroup

logger = logging.getLogger(__name__)


class MultitenantJsonWebsocketConsumer(JsonWebsocketConsumer):
  #self.message, the Message object representing the message the consumer was called for.
  #self.kwargs, keyword arguments from the Routing
  #self.path is always set to the current URL path

  #set strict_ordering = True if we want it
  http_user_and_session = True #equivalent to auth.channel_and_http_session_user_from_http
  disconnect_if_http_logged_out = True

  @connect()
  def connect(self, message, multiplexer, **kwargs):
    logger.debug('connect')
    self.connect_impl(message, multiplexer, **kwargs)

  def connect_impl(self, message, multiplexer, **kwargs):
    pass

  @disconnect()
  def disconnect(self, message, multiplexer, **kwargs):
    logger.debug('disconnect')
    self.disconnect_impl(message, multiplexer, **kwargs)

  def disconnect_impl(self, message, multiplexer, **kwargs):
    pass
  
  def raw_receive(self, message, **kwargs):

    kwargs['user'] = message.user
    if self.disconnect_if_http_logged_out:
      disconnect_if_http_logged_out_decorator()(super(MultitenantJsonWebsocketConsumer, self).raw_receive)(message, **kwargs)
    else:
      super(MultitenantJsonWebsocketConsumer, self).raw_receive(message, **kwargs)

  def receive(self, content, multiplexer, **kwargs):
    logger.debug('receive: {}'.format(content))
    op = content.pop('op', None)
    for_org = content.pop('for_org', None)
    user = kwargs.pop('user', None)
    self.receive_impl(user, op, for_org, content, multiplexer, **kwargs)

  def receive_impl(self, op, for_org, data_dict, multiplexer, **kwargs):
    pass

class MultitenantMultiplexer(WebsocketMultiplexer):
  def send(self, op, data_dict):
    logger.debug('multiplexer send: stream:{}, op:{}, data_dict:{}'.format(self.stream, op, data_dict))
    data_dict['op'] = op
    super(MultitenantMultiplexer, self).send(data_dict)

class MultitenantDemultiplexer(WebsocketDemultiplexer):
  multiplexer_class = MultitenantMultiplexer

  #WebsocketConsumer.method_mapping["websocket.send"] = "raw_send"

  consumers = {}
  generic_consumers = settings.MULTITENANT_SOCKETS_GENERICCONSUMERS
  for key, val in generic_consumers.iteritems():
    consumers[key] = import_string(val)

  @classmethod
  def send_to_channel(cls, stream, channel, op, data_dict):
    multiplexer = cls.multiplexer_class(stream, channel)
    multiplexer.send(op, data_dict) 
    return True

  @classmethod
  def send_to_user(cls, stream, user, op, data_dict):
    org_pk = get_user_org_pk(user)
    group = MultitenantUser(message.user.pk, orgid)
    if group.exists():
      #can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = cls.multiplexer_class(stream, group)
      multiplexer.send(op, data_dict) 
      return True
    return False

  @classmethod
  def send_to_org(cls, stream, orgid, op, data_dict):
    group = MultitenantOrg(orgid)
    if group.exists():
      #can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = cls.multiplexer_class(stream, group)
      multiplexer.send(op, data_dict)
      return True
    return False

  @classmethod
  def send_to_public_group(cls, stream, public_group_name, op, data_dict):
    group = MultitenantPublicGroup(public_group_name)
    if group.exists():
      #can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = cls.multiplexer_class(stream, group)
      multiplexer.send(op, data_dict)
      return True
    return False

  @classmethod
  def send_to_org_group(cls, stream, org_group_name, orgid, op, data_dict):
    group = MultitenantOrgGroup(org_group_name, orgid)
    if group.exists():
      #can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = cls.multiplexer_class(stream, group)
      multiplexer.send(op, data_dict)
      return True
    return False
