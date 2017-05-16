from functools import wraps
from django.conf import settings
from django.utils.module_loading import import_string

#Special permissions
SUPER_ADMIN_ONLY = 'SUPER_ADMIN_ONLY'
PRACTICE_ADMIN_ONLY = 'PRACTICE_ADMIN_ONLY'
NOBODY = 'NOBODY'  #used for methods that aren't supported by view.

import logging
logger = logging.getLogger(__name__)

def send_error(message, error_message):
  message.reply_channel.send({
    "error": error_message,
  })

if hasattr(settings, 'MULTITENANT_SOCKETS_PERMISSIONS_ADAPTER'):
  adapter_module = import_string(settings.MULTITENANT_SOCKETS_PERMISSIONS_ADAPTER)
  has_role = adapter_module.has_role
  has_permission = adapter_module.has_permission
  SUPERADMIN_ROLE_NAME = adapter_module.SUPERADMIN_ROLE_NAME
  PRACTICEADMIN_ROLE_NAME = adapter_module.PRACTICEADMIN_ROLE_NAME
else:
  from .permissions_adapter import has_role, has_permission, SUPERADMIN_ROLE_NAME, PRACTICEADMIN_ROLE_NAME

def can_connect():
  def dec(f):
    @wraps(f)
    def wrapper(message):
      if message.user.is_authenticated():
        message.reply_channel.send({'accept': True})
        return f( message)
      else:
        message.reply_channel.send({'close': True})
        return
    return wrapper
  return dec


def has_permission_and_practice(permission_to_msgtype_for_org):
  def dec(f):
    @wraps(f)
    def wrapper(message):
      user = message.user
      org = message.content.get('org', None)
      msgtype = message.content.get('msgtype', None)
      if is_authorized(user, org, msgtype, permission_to_msgtype_for_org):
        return f(message) 
      else:
        send_error(message, 'not authorized')
        return
    return wrapper
  return dec

def is_authorized(user, org, msgtype, permission_to_msgtype_for_org):
  if user.is_authenticated():
    user_org = user.org_pk()
    if has_role(user, SUPERADMIN_ROLE_NAME):
      return True
    elif permission == SUPER_ADMIN_ONLY:
      return False
    elif ((org is not None) and (user_org == org)) or (org is None):
        if org and org.is_inactive:
            return False
        elif has_role(user, ORGADMIN_ROLE_NAME):
            return True
        elif permission == ORG_ADMIN_ONLY:
            return False
        elif has_permission(user, permission_to_msgtype_for_org):
            return True
        else:
            return False
    else:
        return False
  else:
    return False
