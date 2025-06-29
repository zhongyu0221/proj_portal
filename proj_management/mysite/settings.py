"""
Django settings for t2d project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import configparser
import os
from pathlib import Path



# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = "config.ini"
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(BASE_DIR),
                         "config", CONFIG_FILE))
print(BASE_DIR)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG.get('keys', 'SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = CONFIG['deployment'].getboolean('debug')
WITH_DEBUG_TOOLBAR = CONFIG['deployment'].getboolean('with_debug_toolbar')

ALLOWED_HOSTS = CONFIG.get('deployment', 'allowed_hosts').split(",")

# Application definition
APPEND_SLASH = False


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
'widget_tweaks',
    'userprofiles',
    'project',
    'ledgers',

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# if WITH_DEBUG_TOOLBAR:
#     INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
#     INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': CONFIG['mysql']['ENGINE'],
        'NAME': CONFIG['mysql']['NAME'],
        'USER': CONFIG['mysql']['USER'],
        'PASSWORD': CONFIG['mysql']["PASSWORD"],
        'HOST': CONFIG['mysql']["HOST"],
        'PORT': CONFIG['mysql']["PORT"],
        'TEST': {}
    }
}



# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
MEDIA_URL = '/media/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
# STATIC_ROOT = CONFIG.get('static', 'STATIC_ROOT')
# MEDIA_ROOT = CONFIG.get('static', 'MEDIA_ROOT')
# FILE_UPLOAD_PERMISSIONS = 0o644
# FILE_UPLOAD_TEMP_DIR = os.path.join(MEDIA_ROOT, "tmp")
if DEBUG:
    STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static", "static-only")
    MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static", "media")
else:
    STATIC_ROOT = CONFIG.get('static', 'STATIC_ROOT')
    MEDIA_ROOT = CONFIG.get('static', 'MEDIA_ROOT')


LOGIN_REDIRECT_URL = '/home/'

# Fixtures location
FIXTURE_DIRS = (
    os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "fixtures"),
)




SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600



# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Allow Wing Pro to stop on exceptions and debug templates, when it is present
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'main_formatter': {
            'format': '%(levelname)s:%(name)s:[%(asctime)s] %(filename)s:%(lineno)d:%(message)s',
            # 'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'production_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '{0}/main.log'.format(CONFIG.get('logging', 'directory')),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 7,
            'formatter': 'main_formatter',
            'filters': ['require_debug_false'],
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '{0}/main_debug.log'.format(CONFIG.get('logging', 'directory')),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 7,
            'formatter': 'main_formatter',
            'filters': ['require_debug_true'],
        },
        'null': {
            "class": 'logging.NullHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['null', ],
        },
        'py.warnings': {
            'handlers': ['null', ],
        },
        '': {
            'handlers': ['console', 'production_file', 'debug_file'],
            'level': "DEBUG",
        },
    }
}


try:
    from . import wing_debug_support
    del wing_debug_support
except ImportError:
    if "WINGDB_ACTIVE" in os.environ:
        print("Failed to import debugger support for Wing Pro")

if "WINGDB_ACTIVE" in os.environ:
    DEBUG = True
    try:
        TEMPLATES[0]["OPTIONS"]["debug"] = True
    except Exception:
        TEMPLATE_DEBUG = True

CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS]

# # haystack search using elasticsearch
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch5_backend.Elasticsearch5SearchEngine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'haystack',
#     },
# }

