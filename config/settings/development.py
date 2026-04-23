from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Show Swagger docs in development
SPECTACULAR_SETTINGS = {
    **SPECTACULAR_SETTINGS,
    'TITLE': 'Clean Architecture Django API (Development)',
}

# Looser CORS for local frontend dev
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
CORS_ALLOW_ALL_ORIGINS = True

# Log all SQL queries to console
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
