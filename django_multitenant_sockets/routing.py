from channels.routing import route, include
import consumers

routes = [
  route("websocket.connect", consumers.connect),
  route("websocket.disconnect", consumers.disconnect),
  route("websocket.receive", consumers.receive),
]
