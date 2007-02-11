# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django import template

register = template.Library()

class CodeRenderer(template.Node):
    '''A renderer for the code template tag.'''
    
    def __init__(self, source_expression):
        """Construct a CodeRenderer from an input expression

        Keyword Arguments:
        source_expression -- The Python expression, evaluated in the
                             context of empty globals, and Django's template
                             context as locals, that supplies the page content
                             to be rendered.
                             Yes, I know this violates Django's policy of
                             keeping real Python code out of templates, but
                             what the hell, we're programmers.
         """
        self.source_expression = source_expression
        
    def render(self, ctx):
        return str(eval(self.source_expression, {}, ctx))

        
def code(parser, token):
    try:
        tag_name, source_expression = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires two arguments" % token.contents[0]
    return CodeRenderer(source_expression)

register.tag(code)
