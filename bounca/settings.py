import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


CONFIG_FILE_NAME = '/etc/bounca/main.ini'


from configparser import RawConfigParser
config = RawConfigParser()

if os.path.exists(CONFIG_FILE_NAME):
    DEBUG = False
    config.read(CONFIG_FILE_NAME)
else:
    DEBUG = True    
    config.read(BASE_DIR+CONFIG_FILE_NAME)

       






DATABASES = {
    'default': {
        'NAME': config.get('database', 'DATABASE_NAME'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': config.get('database', 'DATABASE_USER'),
        'PASSWORD': config.get('database', 'DATABASE_PASSWORD'),
        'HOST': config.get('database', 'DATABASE_HOST'),
        'PORT': '5432'
    } 
}

import sys
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': config.get('database', 'DATABASE_NAME')
    }


ADMINS = (
    ('bounca', config.get('email', 'ADMIN_MAIL')),
)

MANAGERS = ADMINS

EMAIL_HOST=config.get('email','EMAIL_HOST')
DEFAULT_FROM_EMAIL=config.get('email', 'FROM_MAIL')
SERVER_EMAIL=config.get('email', 'FROM_MAIL')

SITE_NAME = "bounca" 

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

ALLOWED_HOSTS = ["*"]

# Application definition






# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('secrets', 'SECRET_KEY')


INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    #3rd party libraries
    'rest_framework',
    'djangular',
    'django_countries',

    
    #BounCA
    'bounca.x509_pki',
    'bounca.app_settings',
    'bounca.certificate_engine',
    'bounca.main',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bounca.urls'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend', 'rest_framework.filters.OrderingFilter', 'rest_framework.filters.SearchFilter', ),
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

#GRAPPELLI_INDEX_DASHBOARD = 'x509_pki.dashboard.CustomIndexDashboard'
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




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'media/static/')

STATIC_URL = '/static/'

CA_ROOT = os.path.join(BASE_DIR, 'pki/')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false']
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
             'formatter': 'simple'
#            'filters': ['require_debug_true']

        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # Useless messages mostly about spiders
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}
#TODO Logging INFO not working
#http://www.webforefront.com/django/setupdjangologging.html
import logging
logger = logging.getLogger(__name__)

logger.error("error-FUBAR")
logger.info("info-FUBAR")
logger.debug("debug-FUBAR")
logger.critical("critical-FUBAR")
logger.warning("warning-FUBAR")
