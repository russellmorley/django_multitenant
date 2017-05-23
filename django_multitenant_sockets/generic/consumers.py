from channels.generic.websockets import WebsocketDemultiplexer, WebsocketMultiplexer, JsonWebsocketConsumer, WebsocketConsumer
from django.conf import settings
import logging
from django.utils.module_loading import import_string
from ..decorators import connect, disconnect, get_user_org_pk
from ..channel import MultitenantUser, MultitenantOrg

logger = logging.getLogger(__name__)


class MultitenantJsonWebsocketConsumer(JsonWebsocketConsumer):
  #self.message, the Message object representing the message the consumer was called for.
  #self.kwargs, keyword arguments from the Routing
  #self.path is always set to the current URL path

  #set strict_ordering = True if we want it
  http_user = True #message.user same as request.user would be on a regular View
  channel_session_user = True #provide message.channel_session and message.user on the message object

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
  
  def receive(self, content, multiplexer, **kwargs):
    logger.debug('receive: {}'.format(content))
    op = content.pop('op', None)
    for_org = content.pop('for_org', None)
    self.receive_impl(op, for_org, content, multiplexer, **kwargs)

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
  def send_to_user(cls, stream, user, op, data_dict):
#    consumer_class = cls.consumers.get(stream, None)
#    if consumer_class is not None and getattr(consumer_class, 'send_to_user_impl', None) is not None:

    org_pk = get_user_org_pk(user)
    user_group = MultitenantUser(message.user.pk, orgid)
    if user_group.exists():
      #can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = self.multiplexer_class(stream, user_group)
      multiplexer.send(op, data_dict) 
      #consumer_class.send_impl(multiplexer, op, data_dict)
      return True
    return False

  @classmethod
  def send_to_org(cls, stream, orgid, op, data_dict):
    org_group = MultitenantOrg(orgid)
    if org_group.exists():
      #can use multiplexer by pretending reply_channel is a group since both have send() method
      # with same signature.
      multiplexer = self.multiplexer_class(stream, org_group)
      multiplexer.send(op, data_dict)
      return True
    return False
