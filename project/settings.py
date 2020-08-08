"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import psycopg2.extensions
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR,'templates')
STAITC_DIR = os.path.join(BASE_DIR,'static')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7pnm5hto(j4s6$6%h5syxxmtt%4aprna5w0zi*kmyn5n5h^^u$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['djangoe-commercewebsite.herokuapp.com','127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'django.contrib.sites', 
    # ALL AUTH   
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ALLAUTH PROVIDERS
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'crispy_forms',
    'django_countries',
    'jquery',
    'mptt',
    'rest_framework',
    # SOCIAL OAUTH
    
]
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR,STAITC_DIR],
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

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<db name>',
        # 'DATABASE' : '',
        'USER' : '<user>',
        'PASSWORD' : '<password>',
        'HOST' : '127.0.0.1',
        'PORT' : '5432'
    },
    
}

import dj_database_url 
prod_db  =  dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(prod_db)


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [     
    'django.contrib.auth.backends.ModelBackend', 
    'allauth.account.auth_backends.AuthenticationBackend', 
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
 


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static_root')
CRISPY_TEMPLATE_PACK = 'bootstrap4'
STRIPE_SECRET_KEY = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media_root')

FORCE_SESSION_TO_ONE = False
FORCE_INACTIVE_USER_ENDSESSION= False

MAILCHIMP_API_KEY  = 'e67ca863bcbab21764b3b68cead9d4ff-us17'
MAILCHIMP_DATA_CENTER = "us17"
MAILCHIMP_EMAIL_LIST_ID = '685352d21c'

PROMO_CODE_LIST = [
    'ROBLOXROCKS500K',
    'WEAREROBLOX300',
    'ROBLOXROCKS500K',
    'ROBLOXIG500K',
    'MOTHRAUNLEASHED',
    'SPIDERMANONROBLOX',
    'ONEMILLIONCLUB',
    'FINDTHEKEYS',
    'JURASSICWORLD',
    'EBGAMESBLACKFRIDAY',
    'KINGOFTHESEAS'
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = '<email here>'
EMAIL_HOST_PASSWORD = '<email password>'
DEFAULT_FROM_EMAIL = 'Python ecommerce <email>'