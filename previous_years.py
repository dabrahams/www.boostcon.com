# Copyright David Abrahams 2008. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from boost_consulting.pages.models import build_page, PageWriter
from conference.models import Conference
import os

fields = dict([(x,'') for x in PageWriter.docinfo_fields])

def generate(root_url):
    """Creates Pages for everything but the most recent edition of a conference.

This is a page generator appropriate for use with boost_consulting.pages.models.generators
"""
    
    result = []
    for c in Conference.objects.order_by('-start')[1:9999]:
        print '*** generating page for:', c
        year = str(c.start.year)

        result.append(
            build_page(parts={'title':year,'meta':'','fragment':''}, data=fields, url=root_url+'/'+year))

    return result
