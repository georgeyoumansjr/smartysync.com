import os
import string

from django.contrib.messages import constants as messages_constants

import dj_database_url
from celery.schedules import crontab
from decouple import Csv, config
from pathlib import Path
import pytz

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CORE SETTINGS
# ==============================================================================
PROD = config('PROD', default=False, cast=bool)
# if not PROD:
from dotenv import load_dotenv
load_dotenv()


SECRET_KEY = config('SECRET_KEY', default=string.ascii_letters)

DEBUG = config('DEBUG', default=True, cast=bool)


ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', 
                       cast=Csv())

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',

    'debug_toolbar',
    'django_celery_beat',
    'crispy_forms',

    'colossus.apps.accounts',
    'colossus.apps.campaigns',
    'colossus.apps.core',
    'colossus.apps.templates',
    'colossus.apps.lists',
    'colossus.apps.notifications',
    'colossus.apps.subscribers',
    'colossus.apps.autocampaign'
]

SITE_ID = 1

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ROOT_URLCONF = 'colossus.urls'

WSGI_APPLICATION = 'colossus.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///%s' % os.path.join(BASE_DIR, 'db.sqlite3'))
    )
}

# Add timeout option if the database engine is SQLite
if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    DATABASES['default']['OPTIONS'] = {'timeout': 20}  # Timeout in seconds

INTERNAL_IPS = [
    '127.0.0.1',
]


# ==============================================================================
# MIDDLEWARE SETTINGS
# ==============================================================================

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'colossus.apps.accounts.middleware.UserTimezoneMiddleware',
]


# ==============================================================================
# TEMPLATES SETTINGS
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'colossus/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'colossus.apps.notifications.context_processors.notifications',
            ],
        },
    },
]

# ==============================================================================
# INTERNATIONALIZATION AND LOCALIZATION SETTINGS
# ==============================================================================

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('TIME_ZONE', default='America/New_York')

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('en-us', 'English'),
    ('pt-br', 'Portuguese'),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'colossus/locale'),
)

SESSION_COOKIE_AGE = 3600 # in seconds: 600 = 10min, 3600 = 1hr 

# ==============================================================================
# STATIC FILES SETTINGS
# ==============================================================================

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'colossus/static'),
]


# ==============================================================================
# MEDIA FILES SETTINGS
# ==============================================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/public')

PRIVATE_MEDIA_ROOT = os.path.join(BASE_DIR, 'media/private')


# ==============================================================================
# EMAIL SETTINGS
# ==============================================================================
EMAIL_SUBJECT_PREFIX = os.getenv('EMAIL_SUBJECT_PREFIX', '[GER WHOLESALE] ')

SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'coboaccess@gmail.com')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Ger Wholesale <coboaccess@gmail.com>')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # os.getenv('EMAIL_BACKEND')

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'coboaccess@gmail.com')
# print(EMAIL_HOST_USER)
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'fyrljfsrqmhqkzmd')
# print(EMAIL_HOST_PASSWORD)
if EMAIL_PORT == 465:
    EMAIL_USE_SSL = True
else:
    EMAIL_USE_TLS = True

    

# ==============================================================================
# AUTHENTICATION AND AUTHORIZATION SETTINGS
# ==============================================================================

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = 'campaigns:campaigns'


# ==============================================================================
# DJANGO CONTRIB APPS SETTINGS
# ==============================================================================

MESSAGE_TAGS = {
    messages_constants.DEBUG: 'alert-dark',
    messages_constants.INFO: 'alert-primary',
    messages_constants.SUCCESS: 'alert-success',
    messages_constants.WARNING: 'alert-warning',
    messages_constants.ERROR: 'alert-danger',
}

if DEBUG:
    MESSAGE_LEVEL = messages_constants.DEBUG
else:
    MESSAGE_LEVEL = messages_constants.INFO

GEOIP_PATH = os.path.join(BASE_DIR, 'bin/GeoLite2')


MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# ==============================================================================
# THIRD-PARTY APPS SETTINGS
# ==============================================================================

CRISPY_TEMPLATE_PACK = 'bootstrap4'

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379')

CELERY_BEAT_SCHEDULE = {
    'send-scheduled-campaigns': {
        'task': 'colossus.apps.campaigns.tasks.send_scheduled_campaigns_task',
        'schedule': 60.0
    },
    'clean-lists-hard-bounces': {
        'task': 'colossus.apps.lists.tasks.clean_lists_hard_bounces_task',
        'schedule': crontab(hour=12, minute=0)
    }
}

CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=True, cast=bool)


# ==============================================================================
# FIRST-PARTY APPS SETTINGS
# ==============================================================================

COLOSSUS_HTTPS_ONLY = config('COLOSSUS_HTTPS_ONLY', default=False, cast=bool)

MAILGUN_API_KEY = config('MAILGUN_API_KEY', default='')

MAILGUN_API_BASE_URL = config('MAILGUN_API_BASE_URL', default='')

# ==============================================================================
# LOGGING SETTINGS
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'info.log'),
            'formatter': 'console',
        },
        'sentry': {
            'level': 'INFO',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file', 'sentry'],
            'level': 'WARNING',
        },
        'colossus': {
            'handlers': ['console', 'file', 'sentry'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file', 'sentry'],
            'level': 'INFO',  # Set to DEBUG if you need more detailed logs
            'propagate': False,
        },
    }
}