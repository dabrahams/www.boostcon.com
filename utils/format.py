# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

def _12hr_time(t):
    return t.strftime(str(t.hour%12) + ':%M%p')
