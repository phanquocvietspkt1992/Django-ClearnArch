from .base import *

DEBUG = False

# Staging uses real hosts — set via env ALLOWED_HOSTS=staging.yourdomain.com
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Swagger visible in staging for QA testing
SPECTACULAR_SETTINGS = {
    **SPECTACULAR_SETTINGS,
    'TITLE': 'Clean Architecture Django API (Staging)',
}

# CORS — restrict to staging frontend domain
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# Security — not as strict as production but closer
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Structured logging for staging log aggregators
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
