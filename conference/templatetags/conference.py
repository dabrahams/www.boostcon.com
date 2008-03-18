# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django import template

register = template.Library()

@register.filter
def render_rst(rst,args):
    from utils.restructuredtext import html_parts
    if args != '':
        args=','+str(args)

    # This is a defensive programming hack.  We clearly didn't know whether we
    # were getting unicode or utf-8 strs before, so this makes sure we're in
    # unicode by the time we call html_parts without trying to do a decode on a
    # unicode string.  We need to figure out what's really going on here.
    if not isinstance(rst,unicode):
        rst = rst.decode('utf-8')
        
    return eval('html_parts(rst%s)' % args)['body']
