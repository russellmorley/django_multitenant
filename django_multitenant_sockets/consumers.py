
import json
import logging

from .decorators import connect, disconnect
from channels import Channel
from channels.auth import channel_and_http_session_user_from_http
from channels.auth import channel_session_user
from django.conf import settings
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)
consumer_dicts = getattr(settings, "MULTITENANT_SOCKETS_CONSUMERS", [])


@channel_and_http_session_user_from_http
@connect()
def connect(message):
  logger.debug("connect")
  for consumer_dict in consumer_dicts:
    if (
      consumer_dict.get("consumer_key_is_consumer_route_prefix", None) is not None and
      consumer_dict.get("consumer_key_is_consumer_route_prefix")
    ):
      Channel("{}-connect".format(consumer_dict["consumer"])).send(message.content)
    else:
      import_string("{}.{}".format(consumer_dict["consumer"], "connect"))(message)


@channel_and_http_session_user_from_http
@channel_session_user
@disconnect()
def disconnect(message):
  for consumer_dict in reversed(consumer_dicts):
    if (
      consumer_dict.get("consumer_key_is_consumer_route_prefix", None) is not None and
      consumer_dict.get("consumer_key_is_consumer_route_prefix")
    ):
      Channel("{}-disconnect".format(consumer_dict["consumer"])).send(message.content)
    else:
      import_string("{}.{}".format(consumer_dict["consumer"], "disconnect"))(message)
  logger.debug("disconnect")


@channel_and_http_session_user_from_http
@channel_session_user
def receive(message):
  logger.debug("receive: {}".format(vars(message)))

  text = message.content.get("text", None)
  if text is not None:
    text_dict = json.loads(text)
    stream = text_dict.get("stream", None)
    # don"t convert as follows, similar to genericconsumer, because stream is lost.
    # payload_dict = text_dict.get("payload", None)
    # message.content["text"] = json.dumps(payload_dict, cls=DjangoJSONEncoder)
    if stream is not None:
      filtered_consumer_dicts = filter(lambda consumer_dict: consumer_dict["stream"] == stream, consumer_dicts)
      for consumer_dict in filtered_consumer_dicts:
        if (
          consumer_dict.get("consumer_key_is_consumer_route_prefix", None) is not None and
          consumer_dict.get("consumer_key_is_consumer_route_prefix")
        ):
          Channel("{}-receive".format(consumer_dict["consumer"])).send(message.content)
        else:
          import_string("{}.{}".format(consumer_dict["consumer"], "receive"))(message)
