# Copyright David Abrahams 2006. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

import django.core.cache

class _eternal_cache:
    def set(self, key, value, timeout = None):
        if timeout is None:
            timeout = 7*24*60*60 # a week
            
        return django.core.cache.cache.set(key,value,timeout)

    def get(self, *args, **kw):
        return django.core.cache.cache.get(*args,**kw)

eternal_cache = _eternal_cache()
