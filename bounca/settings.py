"""BounCA settings module"""

import os
import re
import sys
from django.utils.translation import ugettext_lazy as _
from yamlreader import yaml_load


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IS_UNITTEST = 'test' in sys.argv or any(['test' in arg for arg in sys.argv])
IS_COLLECT_STATIC = 'collectstatic' in sys.argv


def get_services_config(path, filename='services.yaml'):
    environment_specific = os.path.join(os.path.abspath(path), filename)
    config_files = []
    if os.path.exists(environment_specific):
        config_files.append(environment_specific)
    if not config_files:
        raise IOError("Couldn't find file"
                      "in any of the directories '{}'.".format(', '.join([environment_specific])))
    return yaml_load(config_files)


SERVICES = get_services_config(os.path.join(BASE_DIR, 'etc', 'bounca'))

SECRET_KEY = SERVICES['django']['secret_key']
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SERVICES['django']['debug']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': SERVICES['psql']['dbname'],
        'USER': SERVICES['psql']['username'],
        'PASSWORD': SERVICES['psql']['password'],
        'HOST': SERVICES['psql']['host'],
        'PORT': SERVICES['psql'].get('port', '5432'),

        # Keep and re-use database connections across requests.  Takes a TTL
        # in seconds, or 0 for "don't re-use connections," or None to re-use
        # connections forever.
        'CONN_MAX_AGE': 10,

        'TEST': {
            'NAME': SERVICES['psql']['dbname'] + '-test-' + str(os.getpid()),
            'CHARSET': 'UTF8',
        }
    }
}



ADMINS = (
    ('bounca', SERVICES['mail']['admin']),
)

MANAGERS = ADMINS
SITE_ID = 1
EMAIL_HOST = SERVICES['mail']['host']
DEFAULT_FROM_EMAIL = SERVICES['mail']['from']
SERVER_EMAIL = SERVICES['mail']['from']

SITE_NAME = "bounca"

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

ALLOWED_HOSTS = SERVICES['django']['hosts']

# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # 3rd party libraries
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'djng',
    'django_countries',
    'rest_framework_swagger',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',

    # BounCA
    'webapp.templatetags',
    'certificate_engine',
    'x509_pki',
    'api',
    'webapp',
]

MIDDLEWARE = [
    'djng.middleware.AngularUrlMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bounca.urls'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bounca.wsgi.application'

GRAPPELLI_ADMIN_TITLE = 'BounCA Admin'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

ACCOUNT_EMAIL_VERIFICATION = None


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'media/static/')

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    BASE_DIR + '/bounca/static',
)

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
#         },
#         'simple': {
#             'format': '%(levelname)s %(message)s'
#         },
#     },
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         },
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#     },
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#             'filters': ['require_debug_false']
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple',
#             'filters': ['require_debug_true']
#
#         },
#         'null': {
#             'level': 'DEBUG',
#             'class': 'logging.NullHandler',
#         }
#     },
#     'loggers': {
#         'django': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#             'propagate': True,
#         },
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#         # Useless messages mostly about spiders
#         'django.security.DisallowedHost': {
#             'handlers': ['null'],
#             'propagate': False,
#         },
#     }
# }

# Directory where all certificates are stores
CERTIFICATE_REPO_PATH = os.path.join(BASE_DIR, 'pki/')

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_HOST = "localhost"


if IS_UNITTEST:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    LANGUAGE_CODE = 'en-us'
