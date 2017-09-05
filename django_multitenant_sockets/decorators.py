from __future__ import absolute_import
import json
import logging

from .channel import MultitenantOrg
from .channel import MultitenantOrgGroup
from .channel import MultitenantPublicGroup
from .channel import MultitenantUser
from channels.generic.base import BaseConsumer
from channels.message import Message
from copy import copy
from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string
from functools import wraps


# Special permissions
NOBODY = "NOBODY"
PRACTICE_ADMIN_ONLY = "PRACTICE_ADMIN_ONLY"
SUPER_ADMIN_ONLY = "SUPER_ADMIN_ONLY"

logger = logging.getLogger(__name__)


adapter_module = import_string(
  getattr(settings, "MULTITENANT_SOCKETS_PERMISSIONS_ADAPTER", "django_multitenant_sockets.adapters.PermissionsAdapter")
)

MULTITENANT_SOCKETS_USER_ORG_FK_ATTR_NAME = getattr(settings, "MULTITENANT_SOCKETS_USER_ORG_FK_ATTR_NAME", "org")


def send_error(message, error_message):
  # daphne does not appear to support key "error".
  message.reply_channel.send({
    "text": "ERROR: {}".format(error_message),
  })


def get_user_org_pk(user):
  user_org = getattr(user, MULTITENANT_SOCKETS_USER_ORG_FK_ATTR_NAME, None)
  if user_org is not None:
    return user_org.pk
  else:
    return None


def connect():
  def dec(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      message = None
      # find the message parameter.
      for arg in args:
        if isinstance(arg, Message):
          message = arg
          break
      if message is not None:
        try:
          # user must be authenticated already
          if message.user.is_authenticated():
            orgid = get_user_org_pk(message.user)
            # add user"s reply_channel to user"s group
            MultitenantUser(message.user.pk, orgid).add(message.reply_channel)

            # Get all public groups the user is a member of and add user"s reply_channel to each public group
            PublicGroup = apps.get_model("django_multitenant_sockets.PublicGroup")
            public_groups = PublicGroup.objects.filter(members__id=message.user.pk)
            for public_group in public_groups:
              MultitenantPublicGroup(public_group.name).add(message.reply_channel)

            if orgid is not None:
              # add user"s reply_channel to org
              MultitenantOrg(orgid).add(message.reply_channel)

              # Get all org groups the user is a member of and add user"s reply_channel to each org group
              OrgGroup = apps.get_model("django_multitenant_sockets.OrgGroup")
              org_groups = OrgGroup.objects.filter(members__id=message.user.pk, org=orgid)
              for org_group in org_groups:
                MultitenantOrgGroup(org_group.name, orgid).add(message.reply_channel)

            message.reply_channel.send({"accept": True})
            return f(*args, **kwargs)
          else:
            message.reply_channel.send({"close": True})
            return
        except Exception:
          message.reply_channel.send({"close": True})
          return
      else:
        message.reply_channel.send({"close": True})
        return
    return wrapper
  return dec


def disconnect():
  def dec(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      message = None
      # find the message parameter.
      for arg in args:
        if (
          hasattr(arg, "__class__") and
          "{}.{}".format(arg.__class__.__module__, arg.__class__.__name__) == "channels.message.Message"
        ):
          message = arg
          break
      if message is not None:
        orgid = get_user_org_pk(message.user)
        multitenant_user = MultitenantUser(message.user.pk, orgid)
        # for cases where connect() did not add reply channel
        if message.reply_channel.name in multitenant_user.get_channels():
          ret_val = f(*args, **kwargs)
          # remove user"s reply_channel from user"s group
          MultitenantUser(message.user.pk, orgid).discard(message.reply_channel)

          # Get all public groups the user is a member of and discard user"s reply_channel to each public group
          PublicGroup = apps.get_model("django_multitenant_sockets.PublicGroup")
          public_groups = PublicGroup.objects.filter(members__id=message.user.pk)
          for public_group in public_groups:
            MultitenantPublicGroup(public_group.name).discard(message.reply_channel)

          if orgid is not None:
            # remove user"s reply_channel from org
            MultitenantOrg(orgid).discard(message.reply_channel)

            # Get all org groups the user is a member of and discard user"s reply_channel to each org group
            OrgGroup = apps.get_model("django_multitenant_sockets.OrgGroup")
            org_groups = OrgGroup.objects.filter(members__id=message.user.pk, org=orgid)
            for org_group in org_groups:
              MultitenantOrgGroup(org_group.name, orgid).discard(message.reply_channel)

          return ret_val
      return
    return wrapper
  return dec


def disconnect_if_http_logged_out():
  def dec(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      message = None
      # find the message parameter.
      for arg in args:
        if (
          hasattr(arg, "__class__") and
          "{}.{}".format(arg.__class__.__module__, arg.__class__.__name__) == "channels.message.Message"
        ):
          message = arg
          break
      if message is not None:
        if message.http_session.get("_auth_user_id", None) is None:
          if (
            hasattr(message, "user") and
            message.user is not None
          ):
            orgid = get_user_org_pk(message.user)
            multitenant_user = MultitenantUser(message.user.pk, orgid)

            # Get all public groups the user is a member of and discard user"s reply_channel to each public group
            PublicGroup = apps.get_model("django_multitenant_sockets.PublicGroup")
            public_groups = PublicGroup.objects.filter(members__id=message.user.pk)

            if orgid is not None:
              # Get all org groups the user is a member of and discard user"s reply_channel to each org group
              OrgGroup = apps.get_model("django_multitenant_sockets.OrgGroup")
              org_groups = OrgGroup.objects.filter(members__id=message.user.pk, org=orgid)

            channels = copy(multitenant_user.get_channels())
            for channel in channels:
              # remove channels from user
              multitenant_user.discard(channel)
              # remove each user channel from each public group
              for public_group in public_groups:
                MultitenantPublicGroup(public_group.name).discard(channel)

              if orgid is not None:
                # remove each user channel from org
                MultitenantOrg(orgid).discard(channel)
                # remove each user channel from each org group
                for org_group in org_groups:
                  MultitenantOrgGroup(org_group.name, orgid).discard(message.reply_channel)
              # close each user channel
              message.reply_channel.send({"close": True})
          return
        else:  # session _auth_user_id set
          return f(*args, **kwargs)
      return
    return wrapper
  return dec


def has_permission_and_org(op_to_permission_name_map):
  def dec(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      message = None
      for arg in args:
        if isinstance(arg, Message):
          message = arg
          break
        if isinstance(arg, BaseConsumer):
          message = arg.message
          break
      if message is not None:
        user = message.user
        text_dict = json.loads(message.content["text"])
        for_org = text_dict.get("for_org", None)
        op = text_dict.get("op", None)  # location for genericconsumer
        if op is None:
          payload = text_dict.get("payload", None)
          if payload is not None:
            op = payload.get("op", None)  # location for consumer
            for_org = payload.get("for_org", None)
        if op is None:  # require an op
          send_error(message, "no op provided")
          return
        else:
          permission_name = op_to_permission_name_map.get(op, None)
          if permission_name is None:
            send_error(message, "no permission for op")
            return
        if is_authorized(user, for_org, permission_name):
          return f(*args, **kwargs)
        else:
          send_error(message, "not authorized")
          return
      else:
        logger.error("has_permission_and_org called but couldn\"t find a message param")
        return
    return wrapper
  return dec


def is_authorized(user, for_org, permission_name):
  if user.is_authenticated():
    user_org = get_user_org_pk(user)
    if adapter_module.has_role(user, adapter_module.SUPERADMIN_ROLE_NAME):
      return True
    elif permission_name == SUPER_ADMIN_ONLY:
      return False
    elif ((for_org is not None) and (user_org == for_org)) or (for_org is None):
      if for_org and for_org.is_inactive:
        return False
      elif adapter_module.has_role(user, adapter_module.ORGADMIN_ROLE_NAME):
        return True
      elif permission_name == adapter_module.ORG_ADMIN_ONLY:
        return False
      elif adapter_module.has_permission(user, permission_name):
        return True
      else:
        return False
    else:
      return False
  else:
    return False
