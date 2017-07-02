from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from rest_framework import exceptions
from .decorators import user_org_fk_attr_name

class Group(models.Model):
  name = models.CharField(max_length=256)
  members = models.ManyToManyField(settings.AUTH_USER_MODEL)

  class Meta:
    abstract = True

  def save(self, *args, **kwargs):
    fieldname = self.uniquewith_fieldname()
    if fieldname is not None:
      field = getattr(self, fieldname)
      if type(self).objects.filter(**{'name': self.name, fieldname: int(field)}).count() > 0:
        raise exceptions.ValidationError('The combination of name and {} must be unique.'.format(fieldname))
    elif type(self).objects.filter(**{'name': self.name}).count() > 0:
      raise exceptions.ValidationError('Name must be unique.')
    super(Group, self).save(*args, **kwargs)

  def uniquewith_fieldname(self):
    return None

  def __str__(self):
    return 'Name: {}'.format( self.name)


@python_2_unicode_compatible
class PublicGroup(Group):
  def __str__(self):
    return super(OrgGroup, self).__str__()

@python_2_unicode_compatible
class OrgGroup(Group):
  org = models.PositiveIntegerField(unique=True)

  def uniquewith_fieldname(self):
    return 'org'

  def __str__(self):
    return 'Org id: {}; {}'.format(self.org, super(OrgGroup, self).__str__())

@receiver(m2m_changed, sender=OrgGroup.members.through, dispatch_uid="org_group_members_changed")
def org_group_members_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
  if action == 'pre_add':
    '''
    only add members who are members of same org
    '''
    filter = user_org_fk_attr_name + '_pk'
    pk_set.intersection_update(
      set(model.objects.filter(**{filter: instance.org}).values_list('pk', flat=True))
    )

