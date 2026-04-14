from .settings import *

DEBUG = False

SECRET_KEY = 'x9$k2m!f@3q7w#r5v8z&j1n4p6t0u2y-markazlar-prod-2026'

ALLOWED_HOSTS = ['markaz.madaniyhayot.uz', 'markazlar.madaniyhayot.uz', 'localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = ['https://markaz.madaniyhayot.uz', 'http://markaz.madaniyhayot.uz', 'https://markazlar.madaniyhayot.uz', 'http://markazlar.madaniyhayot.uz']

CORS_ALLOWED_ORIGINS = [
    'https://markaz.madaniyhayot.uz',
    'http://markaz.madaniyhayot.uz',
    'https://markazlar.madaniyhayot.uz',
    'http://markazlar.madaniyhayot.uz',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/markaz/markazlar_map/back/data/db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
