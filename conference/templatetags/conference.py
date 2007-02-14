# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django import template

register = template.Library()

from boost_consulting.conference.models import Presenter

class Presenters(template.Node):
    '''A renderer for the code template tag.'''
    
    def render(self, ctx):
        ctx['presenters'] = Presenter.objects.all()
        return ''

def presenters(parser, token):
    try:
        tag_name = token.split_contents()
    except ValueError, e:
        raise template.TemplateSyntaxError, "%r tag takes no arguments" % token.contents[0]
    return Presenters()

register.tag(presenters)

@register.filter
def render_rst(rst,args):
    from utils.restructuredtext import html_parts
    if args != '':
        args=','+str(args)
    return eval('html_parts(rst.decode("utf-8")%s)' % args)['body']
