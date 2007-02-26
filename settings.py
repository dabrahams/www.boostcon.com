# Django settings for boost_consulting project.

ADMINS = (
    ('Dave Abrahams', 'dave@boost-consulting.com'),
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

#
# prepare settings that depend on where the project is being run.
#
from site_context import *

TEMPLATE_DEBUG = DEBUG

CACHE_BACKEND = 'locmem:///'

# A default for the view cache, etc.
CACHE_MIDDLEWARE_SECONDS = 60*10

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'US/Pacific'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = 'media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gh59=sq@9vj*9dc#n6oflm1^z-_llra(go&hy!n=zy+q8kwq4a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'utils.context_processors.media_url.media_url',
    
    # These are Django's defaults.  Too bad there's no way to just add to the
    # defaults without repeating them.
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n")

    
MIDDLEWARE_CLASSES = (
#    'django.middleware.cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'boost_consulting.urls'
APPEND_SLASH = False

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    'templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
#    'django.contrib.comments',

    'boost_consulting.news',
    'boost_consulting.pages',
#    'boost_consulting.program',
    'boost_consulting.conference',
)

