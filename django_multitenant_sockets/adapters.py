import logging

logger = logging.getLogger(__name__)


class PermissionsAdapter(object):
  @staticmethod
  def has_role(user, role):
    logger.debug("has_role({}, {}) called".format(user.username, role))
    return True

  @staticmethod
  def has_permission(user, permission):
    logger.debug("has_permission({}, {}) called".format(user.username, permission))
    return True

  NOBODY = "NOBODY"

  ORGADMIN_ROLE_NAME = "orgadmin"

  ORG_ADMIN_ONLY = "ORG_ADMIN_ONLY"

  SUPERADMIN_ROLE_NAME = "superadmin"

  SUPER_ADMIN_ONLY = "SUPER_ADMIN_ONLY"
