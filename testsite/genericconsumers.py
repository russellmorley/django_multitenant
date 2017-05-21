from django_multitenant_sockets.generic.consumers import MultitenantJsonWebsocketConsumer
from django_multitenant_sockets.decorators import has_permission_and_org

import logging
logger = logging.getLogger(__name__)


class TestMultitenantJsonWebsocketConsumer(MultitenantJsonWebsocketConsumer):
  def connect_impl(self, message, multiplexer, **kwargs):
    logger.debug('connect_impl')

  def disconnect_impl(self, message, multiplexer, **kwargs):
    logger.debug('disconnect_impl')
  
  #@has_permission_and_org('test_stream_access')
  def receive_impl(self, op, for_org, data_dict, multiplexer, **kwargs):
    logger.debug('receive: op:{}, for_org:{}, data_dict:{}'.format(op, for_org, data_dict))
    # Simple echo
    multiplexer.send(op, data_dict)

