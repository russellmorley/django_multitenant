from channels import Channel
from channels.auth import channel_session_user, channel_session_user_from_http
from .decorators import can_connect
from django.conf import settings
from django.utils.module_loading import import_string
import logging
import json

logger = logging.getLogger(__name__)

if hasattr(settings,'MULTITENANT_SOCKETS_HANDLERS'):
  handler_dicts = settings.MULTITENANT_SOCKETS_HANDLERS
else:
  handler_dicts = []

@channel_session_user_from_http
@can_connect()
def connect(message):
  logger.debug('connect')
  for handler_dict in handler_dicts:
    if (
      handler_dict.get('handler_is_consumer_route_prefix', None) is not None and 
      handler_dict.get('handler_is_consumer_route_prefix')
    ):
      Channel('{}-connect'.format(handler_dict['handler'])).send(message.content)
    else:
      import_string(handler_dict['handler']).connect(message)

@channel_session_user
def disconnect(message):
  for handler_dict in reversed(handler_dicts):
    if (
      handler_dict.get('handler_is_consumer_route_prefix', None) is not None and 
      handler_dict.get('handler_is_consumer_route_prefix')
    ):
      Channel('{}-disconnect'.format(handler_dict['handler'])).send(message.content)
    else:
      import_string(handler_dict['handler']).disconnect(message)
  logger.debug('disconnect')

@channel_session_user
def receive(message):
  logger.debug('receive: {}'.format(vars(message)))

  text = message.content.get('text', None)
  if text is not None:
    text_dict = json.loads(text)
    msgtype = text_dict.get('msgtype', None) 
    if msgtype is not None:
      filtered_handler_dicts = filter(lambda handler_dict: handler_dict['msgtype'] == msgtype, handler_dicts)
      for handler_dict in filtered_handler_dicts:
        if (
          handler_dict.get('handler_is_consumer_route_prefix', None) is not None and 
          handler_dict.get('handler_is_consumer_route_prefix')
        ):
          Channel('{}-receive'.format(handler_dict['handler'])).send(message.content)
        else:
          import_string(handler_dict['handler']).receive(message)
