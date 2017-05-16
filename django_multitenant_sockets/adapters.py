import logging
logger = logging.getLogger(__name__)

class PermissionsAdapter(object):
  @staticmethod
  def has_role(user, role):
    logger.debug('has_role({}, {}) called'.format(user.username, role))
    return True

  @staticmethod
  def has_permission(user, permission):
    logger.debug('has_permission({}, {}) called'.format(user.username, permission))
    return True

  SUPERADMIN_ROLE_NAME = 'superadmin'

  PRACTICEADMIN_ROLE_NAME = 'practiceadmin'
