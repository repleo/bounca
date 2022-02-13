"""BounCA settings module"""

import os
import sys

from yamlreader import yaml_load

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IS_UNITTEST = "test" in sys.argv or any(["test" in arg for arg in sys.argv])
IS_COLLECT_STATIC = "collectstatic" in sys.argv


def get_services_config(path, filename="services.yaml"):
    environment_specific = os.path.join(os.path.abspath(path), filename)
    config_files = []
    if os.path.exists("/etc/bounca/services.yaml"):
        config_files.append("/etc/bounca/services.yaml")
    if os.path.exists(environment_specific):
        config_files.append(environment_specific)
    if not config_files:
        raise IOError("Couldn't find file" "in any of the directories '{}'.".format(", ".join([environment_specific])))
    return yaml_load(config_files)


SERVICES = get_services_config(os.path.join(BASE_DIR, "etc", "bounca"))

SECRET_KEY = SERVICES["django"]["secret_key"]
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SERVICES["django"]["debug"]

KEY_ALGORITHM = SERVICES["certificate-engine"]["key_algorithm"].lower()
if KEY_ALGORITHM not in ["ed25519", "rsa"]:
    raise ValueError(f"Key algorithm {KEY_ALGORITHM} not supported")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": SERVICES["psql"]["dbname"],
        "USER": SERVICES["psql"]["username"],
        "PASSWORD": SERVICES["psql"]["password"],
        "HOST": SERVICES["psql"]["host"],
        "PORT": SERVICES["psql"].get("port", "5432"),
        # Keep and re-use database connections across requests.  Takes a TTL
        # in seconds, or 0 for "don't re-use connections," or None to re-use
        # connections forever.
        "CONN_MAX_AGE": 10,
        "TEST": {
            "NAME": SERVICES["psql"]["dbname"] + "-test-" + str(os.getpid()),
            "CHARSET": "UTF8",
        },
    }
}

ADMINS = (("bounca", SERVICES["mail"]["admin"]),)

MANAGERS = ADMINS

SITE_ID = 1
SITE_NAME = "BounCA PKI"

EMAIL_HOST = SERVICES["mail"]["host"]
if "username" in SERVICES["mail"] and SERVICES["mail"]["username"]:
    EMAIL_HOST_USER = SERVICES["mail"]["username"]
if "password" in SERVICES["mail"] and SERVICES["mail"]["password"]:
    EMAIL_HOST_PASSWORD = SERVICES["mail"]["password"]
if "connection" in SERVICES["mail"]:
    if SERVICES["mail"]["connection"].lower() == "tls":
        EMAIL_USE_TLS = True
        EMAIL_PORT = 587 if "port" not in SERVICES["mail"] else SERVICES["mail"]["port"]
    elif SERVICES["mail"]["connection"].lower() == "ssl":
        EMAIL_USE_SSL = True
        EMAIL_PORT = 465 if "port" not in SERVICES["mail"] else SERVICES["mail"]["port"]

DEFAULT_FROM_EMAIL = SERVICES["mail"]["from"]
SERVER_EMAIL = SERVICES["mail"]["from"]

TIME_ZONE = "Europe/Amsterdam"
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_L10N = True
USE_TZ = True

ALLOWED_HOSTS = SERVICES["django"]["hosts"]

# Application definition

INSTALLED_APPS = [
    "grappelli",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # 3rd party libraries
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_filters",
    "django_property_filter",
    "django_countries",
    "rest_framework_swagger",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    # BounCA
    "certificate_engine",
    "x509_pki",
    "api",
    "superuser_signup",
    "bounca",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bounca.urls"

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "api.filters.RelatedOrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "vuetifyforms.views.vue_exception_handler",
}

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "api.serializers.UserSerializer",
    "PASSWORD_RESET_SERIALIZER": "api.auth.serializers.PasswordResetSerializerFrontendHost",
}

ACCOUNT_ADAPTER = "api.auth.adapter.DefaultAccountAdapterFrontendHost"

ACCOUNT_EMAIL_VERIFICATION = None
if "email_verification" in SERVICES["registration"] and SERVICES["registration"]["email_verification"] in [
    "mandatory",
    "optional",
]:
    ACCOUNT_EMAIL_VERIFICATION = SERVICES["registration"]["email_verification"]
ACCOUNT_EMAIL_REQUIRED = ACCOUNT_EMAIL_VERIFICATION in ["mandatory", "optional"]
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["api/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

WSGI_APPLICATION = "bounca.wsgi.application"

if SERVICES.get("admin"):
    ADMIN = True if SERVICES.get("admin").get("enabled") else False
    GRAPPELLI_ADMIN_TITLE = "BounCA Admin"
    SUPERUSER_SIGNUP = True if SERVICES.get("admin").get("superuser_signup") else False
else:
    ADMIN = False
    SIGNUP_SUPERUSER = False

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators


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

STATIC_ROOT = os.path.join(BASE_DIR, "media/static/")

STATIC_URL = "/static/"

LOGGING: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s [%(asctime)s] %(name)s %(message)s",
        },
        "simple": {"format": "[%(asctime)s] %(message)s"},
    },
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "filename": "/var/log/bounca/bounca.log",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "D",
            "backupCount": 7,
            "formatter": "verbose",
        },
        "mail_admins": {"level": "ERROR", "class": "django.utils.log.AdminEmailHandler"},
    },
    "root": {
        "level": "ERROR",
        "handlers": ["file"],
    },
    "loggers": {},
}

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    LOGGING["handlers"]["file"]["filename"] = "./logs/bounca.log"
    LOGGING["root"]["level"] = "INFO"
    # https://stackoverflow.com/questions/65425681/django-get-request-error-500-strict-origin-when-cross-origin
    CORS_ORIGIN_ALLOW_ALL = True

if IS_UNITTEST:
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    LANGUAGE_CODE = "en-us"

IS_GENERATE_FRONTEND = "generate_forms" in sys.argv or any(["generate_forms" in arg for arg in sys.argv])

if IS_GENERATE_FRONTEND:
    CRISPY_TEMPLATE_PACK = "vuetify"
    INSTALLED_APPS += ["crispy_forms", "vuetifyforms"]
