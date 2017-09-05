from channels import DEFAULT_CHANNEL_LAYER
from channels.channel import Group


class MultitenantGroup(Group):
  def __init__(self, name, alias=DEFAULT_CHANNEL_LAYER, channel_layer=None):
    return super(MultitenantGroup, self).__init__(name, alias, channel_layer)

  def exists(self):
    return True if self.channel_layer.group_channels(self.name) else False

  def get_channels(self):
    return self.channel_layer.group_channels(self.name)

  def get_name(self):
    return self.name

  def close_all(self):
    for channel in self.get_channels():
      channel.send({"close": True})


class MultitenantUser(MultitenantGroup):
  userid_template = "multitenant-userid_{}"
  userid_orgid_template = userid_template + "-orgid_{}"

  def __init__(self, userid, orgid, alias=DEFAULT_CHANNEL_LAYER, channel_layer=None):
    if orgid is not None:
      name = MultitenantUser.userid_orgid_template.format(userid, orgid)
    else:
      name = MultitenantUser.userid_template.format(userid, orgid)
    return super(MultitenantUser, self).__init__(name, alias, channel_layer)


class MultitenantOrg(MultitenantGroup):
  name_template = "multitenant-orgid_{}"

  def __init__(self, orgid, alias=DEFAULT_CHANNEL_LAYER, channel_layer=None):
    name = MultitenantOrg.name_template.format(orgid)
    return super(MultitenantOrg, self).__init__(name, alias, channel_layer)


class MultitenantOrgGroup(MultitenantGroup):
  template = "multitenant-org_group_name_{}-orgid_{}"

  def __init__(self, org_group_name, orgid, alias=DEFAULT_CHANNEL_LAYER, channel_layer=None):
    name = MultitenantOrgGroup.template.format(org_group_name, orgid)
    return super(MultitenantOrgGroup, self).__init__(name, alias, channel_layer)


class MultitenantPublicGroup(MultitenantGroup):
  template = "multitenant-public_group_name_{}"

  def __init__(self, public_group_name, alias=DEFAULT_CHANNEL_LAYER, channel_layer=None):
    name = MultitenantPublicGroup.template.format(public_group_name)
    return super(MultitenantPublicGroup, self).__init__(name, alias, channel_layer)
