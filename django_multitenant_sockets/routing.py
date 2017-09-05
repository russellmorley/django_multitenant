
from . import consumers
from channels.routing import route

routes = [
  route("websocket.connect", consumers.connect),
  route("websocket.disconnect", consumers.disconnect),
  route("websocket.receive", consumers.receive),
]
