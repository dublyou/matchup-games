# -*- coding: utf-8 -*-
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['www.matchup-games.com', 'matchup-games.com', 'matchup-games.com:8001']

ADMINS = [('Josh', 'jgriffin@matchup-games.com')]
DEFAULT_FROM_EMAIL = 'jgriffin@matchup-games.com'
SERVER_EMAIL = 'jgriffin@matchup-games.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_HOST_USER = 'jgriffin@matchup-games.com'
EMAIL_HOST_PASSWORD = 'bkzevu0i0rwv'
EMAIL_PORT = 587 
EMAIL_USE_TLS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_variable('DATABASE_NAME'),
        'USER': get_env_variable('DATABASE_USER'),
        'PASSWORD': get_env_variable('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    }
}

STATIC_ROOT = "/webapps/dublyou/static/"

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

INVITATIONS_INVITATION_ONLY = True
