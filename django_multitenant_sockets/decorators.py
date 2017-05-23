from functools import wraps
from django.conf import settings
from django.utils.module_loading import import_string
from .channel import MultitenantUser, MultitenantOrg

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

if hasattr(settings, 'MULTITENANT_SOCKETS_USER_GET_ORG_PK_METHOD_NAME'):
  get_org_pk_method_name = getattr(settings, 'MULTITENANT_SOCKETS_USER_GET_ORG_PK_METHOD_NAME')
else:
  get_org_pk_method_name = 'org_pk'

def get_user_org_pk(user):
  get_org_pk_method = getattr(user, get_org_pk_method_name)
  return get_org_pk_method()

def connect():
  def dec(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      message = None
      #find the message parameter.
      for arg in args:
        if (
          hasattr(arg, '__class__') and 
          '{}.{}'.format(arg.__class__.__module__, arg.__class__.__name__) == 'channels.message.Message'
        ):
          message = arg
          break 
      if message is not None:
        try:
          # user must be authenticated already
          if message.user.is_authenticated():
            orgid = get_user_org_pk(message.user)
            MultitenantUser(message.user.pk, orgid).add(message.reply_channel)
            if orgid is not None:
              #add user's reply_channel to user's group
              MultitenantOrg(orgid).add(message.reply_channel)
            #add user's reply_channel to org
            message.reply_channel.send({'accept': True})
            return f(*args, **kwargs)
          else:
            message.reply_channel.send({'close': True})
            return
        except Exception:
          message.reply_channel.send({'close': True})
          return
      else:
        message.reply_channel.send({'close': True})
        return
    return wrapper
  return dec

def disconnect():
  def dec(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      message = None
      #find the message parameter.
      for arg in args:
        if (
          hasattr(arg, '__class__') and 
          '{}.{}'.format(arg.__class__.__module__, arg.__class__.__name__) == 'channels.message.Message'
        ):
          message = arg
          break 
      if message is not None:
        orgid = get_user_org_pk(message.user)
        multitenant_user = MultitenantUser(message.user.pk, orgid)
        #for cases where connect() did not add reply channel
        if message.reply_channel.name in multitenant_user.get_channels():
          ret_val = f(*args, **kwargs)
          #remove user's reply_channel from user's group
          MultitenantUser(message.user.pk, orgid).discard(message.reply_channel)
          if orgid is not None:
            #remove user's reply_channel from org
            MultitenantOrg(orgid).discard(message.reply_channel)
          return ret_val
      return
    return wrapper
  return dec


def has_permission_and_org(permission_to_msgtype_for_org):
  def dec(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      import pdb; pdb.set_trace()
      message = None
      for arg in args:
        if (
          hasattr(arg, '__class__') and 
          '{}.{}'.format(arg.__class__.__module__, arg.__class__.__name__) == 'channels.message.Message'
        ):
          message = arg
          break 
      if message is not None:
        user = message.user
        org = message.content.get('org', None)
        msgtype = message.content.get('msgtype', None)
        if is_authorized(user, org, msgtype, permission_to_msgtype_for_org):
          return f(*args, **kwargs) 
        else:
          send_error(message, 'not authorized')
          return
      else:
        send_error(message, '')
        return
    return wrapper
  return dec

def is_authorized(user, org, msgtype, permission_to_msgtype_for_org):
  if user.is_authenticated():
    user_org = get_user_org_pk(user)
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
