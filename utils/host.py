# Copyright David Abrahams 2008. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from boost_consulting import settings

def hostname(request = None):
    if request == None:
        try:
            return settings.hostname
        except AttributeError:
            return 'localhost:8000'
    else:
        server_name = request.META['SERVER_NAME']
        server_port = request.META['SERVER_PORT']
        if not server_port or server_port == '80':
            return server_name
        else:
            return server_name+':'+server_port
