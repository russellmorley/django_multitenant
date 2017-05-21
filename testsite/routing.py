from channels.routing import route, route_class, include
import django_multitenant_sockets.routing as multitenant_sockets_routing

from django_multitenant_sockets.generic import consumers as genericconsumers
import consumers

'''
For commented settings.MULTITENANT_SOCKETS_CONSUMERS = [
{
    "stream": "test",
    "consumer": "test",
    "consumer_key_is_consumer_route_prefix": True,
  },
]
'''
test_routes = [
  route("test-connect", consumers.connect),
  route("test-disconnect", consumers.disconnect),
  route("test-receive", consumers.receive),
  route("test-send", consumers.send),
]

combined_routes = multitenant_sockets_routing.routes + test_routes
routes = [
  include(combined_routes, path = r"^/multitenantsocket"),
  route_class(genericconsumers.MultitenantDemultiplexer, path=r"^/genericmultitenantsocket/"),
]
