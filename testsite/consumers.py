import logging

from django_multitenant_sockets.decorators import disconnect_if_http_logged_out
from django_multitenant_sockets.decorators import has_permission_and_org

logger = logging.getLogger(__name__)


def connect(message):
  logger.debug("connect")


def disconnect(message):
  logger.debug("disconnect")


@disconnect_if_http_logged_out()
@has_permission_and_org({"do_stuff": "do_stuff_permission"})
def receive(message):
  logger.debug("receive: {}".format(vars(message)))
  message.reply_channel.send({"text": message.content["text"]})
  # check authorization based on message.type and get_user_org_pk(message.user)


def send(message):
  pass
