
SECRET_KEY = "cat"

INSTALLED_APPS = (
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.admin",
  "channels",
  "channels.delay",
  "django_multitenant_sockets",
  "tests",
)

DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.sqlite3",
  }
}

CHANNEL_LAYERS = {
  "default": {
    "BACKEND": "asgiref.inmemory.ChannelLayer",
    "ROUTING": [],
  }
}

MIDDLEWARE_CLASSES = []
