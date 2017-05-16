from channels.routing import route, include
import handlers

routes = [
  route("chat-connect", handlers.connect),
  route("chat-disconnect", handlers.disconnect),
  route("chat-receive", handlers.receive),
  route("chat-send", handlers.send),
]
