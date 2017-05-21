"""
Django settings for testsite project.

Generated by 'django-admin startproject' using Django 1.8.17.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ws5ra+w07flc51g#g33j@s@4@$bd%sv=umvuqvhl1yd)j92iyo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',

    'authentication',
    'django_multitenant_sockets',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'testsite.urls'

AUTH_USER_MODEL = 'authentication.User'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'testsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static/app/dist/'),
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'PAGE_SIZE': 10,
}

CHANNEL_LAYERS = {
  'default': {
    'BACKEND': 'asgiref.inmemory.ChannelLayer',
    'ROUTING': 'testsite.routing.routes',
  },
}

LOGGING = {
  'version': 1,
  'handlers': {
    'console': {
      'level': 'DEBUG',
      'class': 'logging.StreamHandler',
      'formatter': 'full',
    },
  },
  'formatters': {
    'full': {
      'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
    },
  },
  'loggers': {
    'django_multitenant_sockets': {
      'handlers': ['console'],
      'level': 'DEBUG',
    },
    'testsite': {
      'handlers': ['console'],
      'level': 'DEBUG',
    },
  },
}

MULTITENANT_SOCKETS_PERMISSIONS_ADAPTER = "django_multitenant_sockets.adapters.PermissionsAdapter"

MULTITENANT_SOCKETS_USER_GET_ORG_PK_METHOD_NAME = 'org_pk'

MULTITENANT_SOCKETS_CONSUMERS = [
  {
    "stream": "test",
    "consumer": "testsite.consumers",
    "consumer_key_is_consumer_route_prefix": False,
  },
]
'''
{
  "stream": "test",
  "consumer": "test",
  "consumer_key_is_consumer_route_prefix": True,
},
'''
MULTITENANT_SOCKETS_GENERICCONSUMERS = {
  #stream_name: genericconsumer
  'test': 'testsite.genericconsumers.TestMultitenantJsonWebsocketConsumer',
  #"other": AnotherConsumer,
}
