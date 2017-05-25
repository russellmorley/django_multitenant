from __future__ import unicode_literals

import json

from django.test import override_settings
from django.contrib.auth import get_user_model

from channels import route_class
from channels.exceptions import SendNotAvailableOnDemultiplexer
from channels.generic import BaseConsumer, websockets
from channels.test import ChannelTestCase, Client, WSClient, apply_routes

class GenericTestCase(ChannelTestCase):
  pass
