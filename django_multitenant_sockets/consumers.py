from channels import Channel
from channels.auth import channel_session_user, channel_session_user_from_http
from .decorators import can_connect
from django.conf import settings
from django.utils.module_loading import import_string
import logging
import json

logger = logging.getLogger(__name__)

if hasattr(settings,'MULTITENANT_SOCKETS_CONSUMERS'):
  consumer_dicts = settings.MULTITENANT_SOCKETS_CONSUMERS
else:
  consumer_dicts = []

@channel_session_user_from_http
@can_connect()
def connect(message):
  logger.debug('connect')
  for consumer_dict in consumer_dicts:
    if (
      consumer_dict.get('consumer_key_is_consumer_route_prefix', None) is not None and 
      consumer_dict.get('consumer_key_is_consumer_route_prefix')
    ):
      Channel('{}-connect'.format(consumer_dict['consumer'])).send(message.content)
    else:
      import_string('{}.{}'.format(consumer_dict['consumer'], 'connect'))(message)

@channel_session_user
def disconnect(message):
  for consumer_dict in reversed(consumer_dicts):
    if (
      consumer_dict.get('consumer_key_is_consumer_route_prefix', None) is not None and 
      consumer_dict.get('consumer_key_is_consumer_route_prefix')
    ):
      Channel('{}-disconnect'.format(consumer_dict['consumer'])).send(message.content)
    else:
      import_string('{}.{}'.format(consumer_dict['consumer'], 'disconnect'))(message)
  logger.debug('disconnect')

@channel_session_user
def receive(message):
  logger.debug('receive: {}'.format(vars(message)))

  text = message.content.get('text', None)
  if text is not None:
    text_dict = json.loads(text)
    stream = text_dict.get('stream', None) 
    if stream is not None:
      filtered_consumer_dicts = filter(lambda consumer_dict: consumer_dict['stream'] == stream, consumer_dicts)
      for consumer_dict in filtered_consumer_dicts:
        if (
          consumer_dict.get('consumer_key_is_consumer_route_prefix', None) is not None and 
          consumer_dict.get('consumer_key_is_consumer_route_prefix')
        ):
          Channel('{}-receive'.format(consumer_dict['consumer'])).send(message.content)
        else:
          import_string('{}.{}'.format(consumer_dict['consumer'], 'receive'))(message)
