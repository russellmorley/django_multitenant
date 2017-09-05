from __future__ import absolute_import

from .models import Practice
from .models import User
from django.contrib import admin


admin.site.register(Practice)

admin.site.register(User)
