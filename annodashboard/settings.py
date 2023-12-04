"""
Django settings for annodashboard project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os.path
import platform
from pathlib import Path
import djongo

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent





# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&aacbf=n&fwpa@!ibc4rdj**4*_$vct48%&4xgh9l$^!_+j%17'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['fal-1.upcode-dev.at', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Core',
    'buildings',
    'rest_framework',
    'users',
    'drf_yasg',
    'tailwind',
    'django_browser_reload',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = 'annodashboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'annodashboard.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

def get_env_variable(var_name):
    """Get the environment variable or return exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f'Set the {var_name} environment variable'
        raise ImproperlyConfigured(error_msg)


DATABASES = {
    'buildings': {
        'ENGINE': 'djongo',
        'NAME': os.getenv('COSMOS_DB_NAME'),
        'CLIENT': {
            'host': os.getenv('COSMOS_DB_CONNECTION_STRING')
        }
    },
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('AZURE_SQL_DB_NAME'),
        'USER': os.getenv('AZURE_SQL_USER'),
        'PASSWORD': os.getenv('AZURE_SQL_PASSWORD'),
        'HOST': os.getenv('AZURE_SQL_HOST'),
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'connection_timeout': 60,  # Adjust the timeout as needed
        }
    }
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DATABASE_ROUTERS = ['annodashboard.router.BuildingsRouter']  # Replace with the actual path to your BuildingsRouter class


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'

# Configuration Tailwind
TAILWIND_APP_NAME = 'Core'

if platform.system() == "Windows":
    NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"
else:
    NPM_BIN_PATH = "/usr/bin/npm"


# Internal IPs
INTERNAL_IPS = ['127.0.0.1',]

# Configuration for Tailwind CSS dists
TAILWIND_CSS_PATH = 'css/dist/styles.css'

REST_FRAMEWORK = {
    #'DEFAULT_AUTHENTICATION_CLASSES': [
    #    'annodashboard.authenticate.APIKeyAuthentication',
    #],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

MY_API_KEY = os.environ.get('MY_DJANGO_API_KEY')


