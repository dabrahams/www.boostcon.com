# Django settings for boost_consulting project.

import os
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

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

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gh59=sq@9vj*9dc#n6oflm1^z-_llra(go&hy!n=zy+q8kwq4a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'utils.context_processors.media_url',

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

APPEND_SLASH = False

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    'templates',
    os.path.join(os.path.dirname(__file__), 'templates')
)

STOCKPHOTO_URL = '/community/photos'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',

    'boost_consulting.news',
    'boost_consulting.pages',
    'boost_consulting.conference',

    'stockphoto',
    
)

#
# SCT settings
#
SPH_SETTINGS = { 'wiki_rss_url' : '/feeds/community/wiki/',
                 'django096compatibility': True
                 }

LIB_PATH = os.path.join(ROOT_PATH, 'communitytools', 'sphenecoll')
sys.path.append(LIB_PATH)

TEMPLATE_DIRS += (    os.path.join(LIB_PATH, 'templates'),)
TEMPLATE_CONTEXT_PROCESSORS += (    'sphene.community.context_processors.navigation',)

MIDDLEWARE_CLASSES += (
    'sphene.community.middleware.ThreadLocals',
    'sphene.community.middleware.GroupMiddleware',
    'sphene.community.middleware.MultiHostMiddleware',
    'sphene.community.middleware.PermissionDeniedMiddleware',
)

ROOT_URLCONF = 'boost_consulting.urls'

INSTALLED_APPS += (
#    'djaptcha',
    'sphene.community',
    'sphene.sphboard',
    'sphene.sphwiki',
    'django.contrib.humanize',
)    

SPH_HOST_MIDDLEWARE_URLCONF_MAP = {
    '.*': { 'urlconf': 'boost_consulting.urls',
                        'params': { 'groupName': 'boostcon' }
                        },
}

FONT_PATH = '/usr/share/fonts/truetype/ttf-bitstream-vera/VeraBd.ttf'
FONT_SIZE = 16
