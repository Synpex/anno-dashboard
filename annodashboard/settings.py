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
import sys
from pathlib import Path
import djongo

from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Determine the environment (local, production, etc.)
ENVIRONMENT = os.getenv('DJANGO_ENV', 'local')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&aacbf=n&fwpa@!ibc4rdj**4*_$vct48%&4xgh9l$^!_+j%17'

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == 'local':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['fal-1.upcode-dev.at', 'localhost', 'uat-anno-dashboard-route-anno-amsterdam.apps.ocp1-inholland.joran-bergfeld.com' ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages', # Django Storages
    'Core', # Django Tailwind - Dashboard Navigation
    'buildings', # Django App - Buildings
    'rest_framework', # Django REST Framework
    'stats', # Django App - Stats
    'users', # Django App - Users
    'drf_yasg', # Django REST Framework - Swagger
    'tailwind', # Django Tailwind
    'django_browser_reload', # Django Browser Reload
    'corsheaders', # Django CORS Headers
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
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

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

if ENVIRONMENT == 'local':
    # Use SQLite for local development and testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
        'buildings': {
            'ENGINE': 'djongo',
            'NAME': os.getenv('MONGO_DB_NAME'),
            'CLIENT': {
                'host': os.getenv('MONGO_DB_CONNECTION_STRING')
            },
            'TEST': {
                'NAME': 'buildings_test',
                'DEPENDENCIES': [],
            }
        },
    }
else:
    DATABASES = {
        'buildings': {
            'ENGINE': 'djongo',
            'NAME': os.getenv('MONGO_DB_NAME'),
            'CLIENT': {
                'host': os.getenv('MONGO_DB_CONNECTION_STRING')
            },
            'TEST': {
                'NAME': 'buildings_test',
                'DEPENDENCIES': [],
            }
        },
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('SQL_DB_NAME'),
            'USER': os.getenv('SQL_USER'),
            'PASSWORD': os.getenv('SQL_PASSWORD'),
            'HOST': os.getenv('SQL_HOST'),
            'PORT': os.getenv('SQL_PORT'),
            'TEST': {
                'ENGINE': 'django.db.backends.dummy',
            },
        },
    }


#region Azure Storage Variables

DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = os.getenv('AZURE_CONTAINER')
AZURE_SSL = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
#MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'node_modules'),
]

DATABASE_ROUTERS = ['annodashboard.router.NoMigrateRouter']

SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Or another valid session engine


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

# Redirect to 'login' page if not authenticated
LOGIN_URL = 'login'

# Set redirection to dashboard after login
LOGIN_REDIRECT_URL = 'buildings'


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'
DEFAULT_TIME_ZONE = timezone.get_fixed_timezone(60)  # 60 minutes ahead of UTC for GMT+1


USE_I18N = True

USE_TZ = True




# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'


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
   # 'DEFAULT_AUTHENTICATION_CLASSES': [
   #     'annodashboard.authenticate.APIKeyAuthentication',
   # ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# API Configuration
MY_API_KEY = os.environ.get('MY_DJANGO_API_KEY')
BAG_API_BASE_URL = os.getenv('BAG_API_BASE_URL')
BAG_API_KEY = os.getenv('BAG_API_KEY')

MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoicG51YW0iLCJhIjoiY2xxM3R1dDB6MDAzazJrbG9oa3VyeWd3OSJ9.czZwXxAxPv4CRxe-E0_SPQ'
