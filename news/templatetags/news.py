from django import template
from boost_consulting.news.models import *
from utils.restructuredtext import html_parts

register = template.Library()

#
# get_latest_news tag implementation
#
class LatestNewsNode(template.Node):
    def __init__(self, count):
        self.count = count

    def render(self, ctx):
        News._scan()
        ctx['news'] = News.objects.order_by('-date')[:self.count]
        return ''

def get_latest_news(parser, token):
    try:
        tag, count = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents[0]
    return LatestNewsNode(int(count))

register.tag(get_latest_news)

#
# render_rst tag implementation
#
class ReSTRenderer(template.Node):
    '''A renderer for the render_rst template tag.'''
    
    def __init__(self, rst_source_expression, initial_header_level):
        """Construct a ReSTRenderer from an input expression and initial header        level

        Keyword Arguments:
        rst_source_expression -- The Python expression, evaluated in the
                                 context of empty globals, and Django's template
                                 context as locals, that supplies the ReST
                                 source for the page content to be rendered.
                                 Yes, I know this violates Django's policy of
                                 keeping real Python code out of templates, but
                                 what the hell, we're programmers.

        initial_header_level --  The topmost header level to generate from the
                                 ReST.  When combining multiple ReST documents on a
                                 page it may be important to start with <h2>
                                 instead of <h1>, for example.
        """
        self.rst_source_expression = rst_source_expression
        self.initial_header_level = initial_header_level
        
    def render(self, ctx):
        input_string = eval(self.rst_source_expression, {}, ctx).decode('utf-8')
        parts = html_parts(
             input_string = input_string
           , input_encoding='unicode'
           , initial_header_level = self.initial_header_level)
        
        return parts['fragment'].encode('utf8')
        
def render_rst(parser, token):
    try:
        tag_name, rst_source_expression, initial_header_level = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires two arguments" % token.contents[0]
    return ReSTRenderer(rst_source_expression, int(initial_header_level))

register.tag(render_rst)


