import os

DEBUG = False
if os.environ.get('BOOSTCON_SITE_CONTEXT') == 'boostcon':
    
    # So our ReST translation code can find the source files with relative
    # paths.
    os.chdir('/usr/local/www/apache22/boostcon/src/boost_consulting/')

    DATABASE_ENGINE = 'postgresql'
    DATABASE_NAME = 'boostcon.db'
    DATABASE_USER = 'boostcon'
    DATABASE_PASSWORD = 'crtplib'
    MEDIA_URL = 'http://www.boostcon.com:8081/site-media'
    serve_media = False
    
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
