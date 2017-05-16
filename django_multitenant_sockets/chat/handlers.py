from ..decorators import has_permission_and_practice
import logging
import json

logger = logging.getLogger(__name__)

def connect(message):
  logger.debug('connect')

def disconnect(message):
  logger.debug('disconnect')

@has_permission_and_practice('chat_interact')
def receive(message):
  logger.debug('receive: {}'.format(vars(message)))
  message.reply_channel.send({'text': message.content['text']})
  #check authorization based on message.type and message.user.username[0].org_pk()

@has_permission_and_practice('chat_interact')
def send(message):
  pass
