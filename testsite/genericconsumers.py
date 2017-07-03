from django_multitenant_sockets.generic.consumers import MultitenantJsonWebsocketConsumer
from django_multitenant_sockets.decorators import has_permission_and_org, disconnect_if_http_logged_out

import logging
logger = logging.getLogger(__name__)


class TestMultitenantJsonWebsocketConsumer(MultitenantJsonWebsocketConsumer):
  #disconnect_if_http_logged_out = False

  def connect_impl(self, message, multiplexer, **kwargs):
    logger.debug('connect_impl')

  def disconnect_impl(self, message, multiplexer, **kwargs):
    logger.debug('disconnect_impl')
  
  @has_permission_and_org({'do_stuff': 'do_stuff_permission'})
  def receive_impl(self, user, op, for_org, data_dict, multiplexer, **kwargs):
    logger.debug('receive: user_id: {}, op:{}, for_org:{}, data_dict:{}'.format(user.pk, op, for_org, data_dict))
    # Simple echo
    multiplexer.send(op, data_dict)

