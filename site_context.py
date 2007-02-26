import os

DEBUG = False
try:
    uname = os.uname()
except AttributeError:
    uname = 5 * (None,)
    
if uname[1] == 'boost-consulting.com':
    
    # So our ReST translation code can find the source files with relative
    # paths.
    os.chdir('/usr/local/www/apache22/boostcon/src/boost_consulting/')

    DATABASE_ENGINE = 'postgresql'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = 'boostcon'
    DATABASE_PASSWORD = 'crtplib'
    MEDIA_URL = 'http://www.boostcon.com:8081/site-media'
    serve_media = False

    # URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
    # trailing slash.
    # Examples: "http://foo.com/media/", "/media/".
    ADMIN_MEDIA_PREFIX = 'http://boostcon.com:8081/admin-media/'
    
    #
    # Add an elif cases here to support your environment
    #
else: # default settings work for my local development server
    DATABASE_ENGINE = 'postgresql'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = ''
    DATABASE_PASSWORD = ''
    MEDIA_URL = '/site-media'
    serve_media = True
    DEBUG = True

    # URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
    # trailing slash.
    # Examples: "http://foo.com/media/", "/media/".
    ADMIN_MEDIA_PREFIX = '/media/'
    
