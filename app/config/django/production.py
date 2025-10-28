import os
from .base import *
from config.env import env

DEBUG = env.bool('DJANGO_DEBUG', default=False)

with open('/run/secrets/django_secret_key') as f:
    SECRET_KEY = f.read().strip()

with open('/run/secrets/postgres_password') as f:
    POSTGRES_PASSWORD = f.read().strip()

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB',default='saved_notams'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST':env('DATABASE_HOST'),
        'PORT':env('DATABASE_PORT'),
    }
}