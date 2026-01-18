"""
Development settings
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Enable Django Debug Toolbar for development
INSTALLED_APPS += [
    'django_extensions',
]

# Show SQL queries in console for debugging
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# Disable HTTPS requirement for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Email backend for development (prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery eager mode for synchronous testing
CELERY_TASK_ALWAYS_EAGER = False  # Set to True to test without Celery worker
CELERY_TASK_EAGER_PROPAGATES = True

# Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
