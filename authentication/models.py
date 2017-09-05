from __future__ import unicode_literals

from django.contrib import auth
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Practice(models.Model):
  name = models.CharField(max_length=64, unique=True)

  def __str__(self):
    return "Name: {}".format(self.name)


@python_2_unicode_compatible
class User(auth.models.AbstractUser):
  practice = models.ForeignKey(Practice, null=True)

  def __str__(self):
    return "Username: {}".format(self.username)
