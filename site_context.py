import sys
import os
DEBUG = False

uname = os.popen('uname -a').read()

# For some reason checking uname is not enough to identify the server running on
# boost-consulting.com.  It occasionally falls through and decides that I'm on
# my local development server.
if 'boost-consulting.com' in uname:
    # So our ReST translation code can find the source files with relative
    # paths.
    
    DATABASE_ENGINE = 'postgresql_psycopg2'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = 'boostcon'
    DATABASE_PASSWORD = 'xxx'

    serve_media = 'runserver' in sys.argv
    if serve_media:
        ADMIN_MEDIA_PREFIX = '/admin-media/'
    
    #
    # Add an elif case here to support your environment
    #

elif 'daniel-desktop' in uname:
    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = ''
    DATABASE_PASSWORD = 'xxx'
    DEBUG = True

    serve_media = True

else: # default settings work for my local development server
    DATABASE_ENGINE = 'postgresql_psycopg2'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = ''
    DATABASE_PASSWORD = 'xxx'
    serve_media = True
    DEBUG = True
    EMAIL_HOST='smtp.rcn.com'

    # URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
    # trailing slash.
    # Examples: "http://foo.com/media/", "/media/".
    ADMIN_MEDIA_PREFIX = '/media/'
    
