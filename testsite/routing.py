from channels.routing import route, include
import django_multitenant_sockets.routing as multitenant_sockets_routing
import django_multitenant_sockets.chat.routing as chat_routing


combined_routes = multitenant_sockets_routing.routes + chat_routing.routes

routes = [
  include(combined_routes, path = r"^/multitenantsocket"),
]
