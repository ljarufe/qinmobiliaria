# Django settings for QInmobiliaria project.

import sys
from os.path import dirname
BASEDIR = dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#Change to true before deploying into production
ENABLE_SSL = True

site_name = 'inmobiliaria.quimerahg.com'
LOGIN_URL = '/'

EMAIL_HOST = 'smtp.quimerahg.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'pchavez@quimerahg.com'
EMAIL_HOST_PASSWORD= '40298646'
# EMAIL_HOST_USER = 'info@quimerainmobiliaria.com'
# EMAIL_HOST_PASSWORD = 'infoquimera'

# POSTMARK_API_KEY    = '277e0595-6b40-4e44-a643-7d28b48ffe70'
# POSTMARK_SENDER     = 'info@quimerainmobiliaria.com'
# POSTMARK_TEST_MODE  = False
#EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'pchavez@quimerahg.com' #'info@quimerainmobiliaria.com'
SENDER_NAME = 'Quimera Inmobiliaria' #variable para el hack en send_html_mail
SERVER_EMAIL = DEFAULT_FROM_EMAIL

SESSION_EXPIRE_AT_BROWSER_CLOSE=True

FACEBOOK_API_ID = "323885717625180"

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
   ('giussepi', 'giussepexy@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'qinmobiliaria',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': '12345',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Lima'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-pe'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '%s/public/media/' % BASEDIR

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '%s/public/static/' % BASEDIR

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# TinyMCE configuration
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align': "left",
    'skin': "o2k7",
    "file_browser_callback" : "CustomFileBrowser",
}
TINYMCE_FILEBROWSER = False
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = True

# Additional locations of static files
STATICFILES_DIRS = (
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_99p(o*$^0&gem#=ty43y-%zvhrgh@sa4n8ye*d-qu0%y%_ty%'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'zinnia.context_processors.version',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'qinmobiliaria.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/templates' % BASEDIR
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'sorl.thumbnail',
    'tagging',
    'mptt',
    'zinnia',
    'admin',
    'common',
    'portal',
    'proyectos',
    'usuarios',
    'tinymce',
    'watermarker',
    'south', #comentar south antes de sincronizar, asi al correr install.py no habran porblemas
    #'django_extensions',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

try:
   if sys.argv[1] == 'test':
#    if True:
        GEO_SUPPORT = False
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': ':memory',
                'USER': '',                      # Not used with sqlite3.
                'PASSWORD': '',                  # Not used with sqlite3.
                'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
                'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
                }
            }
except IndexError:
    print "Creating and Installing custom groups and Permissions..."

AUTH_PROFILE_MODULE = 'usuarios.Cliente'
