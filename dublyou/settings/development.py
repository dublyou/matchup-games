# -*- coding: utf-8 -*-
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_variable('DATABASE_NAME'),
        'USER': get_env_variable('DATABASE_USER'),
        'PASSWORD': get_env_variable('DATABASE_PASSWORD'),
        'HOST': '',
        'PORT': '',
    }
}

# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/tmp/emails'

ADMINS = [('Josh', 'jgriffin@matchup-games.com')]
DEFAULT_FROM_EMAIL = 'jgriffin@matchup-games.com'
SERVER_EMAIL = 'jgriffin@matchup-games.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_HOST_USER = 'jgriffin@matchup-games.com'
EMAIL_HOST_PASSWORD = 'bkzevu0i0rwv'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

