import sys
import os
DEBUG = False

uname = os.popen('uname -a').read()

# For some reason checking uname is not enough to identify the server running on
# boost-consulting.com.  It occasionally falls through and decides that I'm on
# my local development server.
if 'boostpro.com' in uname:
    # So our ReST translation code can find the source files with relative
    # paths.
    
    DATABASE_ENGINE = 'postgresql_psycopg2'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = 'boostcon'
    DATABASE_PASSWORD = 'crtplib'

    serve_media = 'runserver' in sys.argv
    if serve_media:
        ADMIN_MEDIA_PREFIX = '/admin-media/'
    hostname = 'boostcon.com'

    # Needed so that Django doesn't insert explicit boostcon.fcgi
    # elements into the URLs
    FORCE_SCRIPT_NAME = '' 

    #
    # Add an elif case here to support your environment
    #

elif 'daniel-desktop' in uname:
    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = ''
    DATABASE_PASSWORD = ''
    DEBUG = True

    serve_media = True

elif 'Jimbo' in uname:
    DATABASE_ENGINE = 'postgresql_psycopg2'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = 'jim'
    DATABASE_PASSWORD = 'jim'
    serve_media = True
    DEBUG = True
    ADMIN_MEDIA_PREFIX = '/media/'
    EMAIL_HOST='smtp.charter.net'
    GOOGLE_MERCHANT_ID =  '766162824246335'
    GOOGLE_MERCHANT_KEY = 'QvnSBCdQJvB8xRKgBO52JA'

else: # default settings work for my local development server
    DATABASE_ENGINE = 'postgresql_psycopg2'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = ''
    DATABASE_PASSWORD = ''
    serve_media = True
    DEBUG = True
    EMAIL_HOST='smtp.rcn.com'

    # URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
    # trailing slash.
    # Examples: "http://foo.com/media/", "/media/".
    ADMIN_MEDIA_PREFIX = '/media/'
    
