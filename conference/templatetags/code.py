from django import template

import schedule

register = template.Library()

def _import_(module_name):
    m = __import__(module_name,{},{},[])
    return getattr(m, module_name.split('.')[-1])

class PythonEvaluator(template.Node):
    def __init__(self, args):
        self.args = args

    def _eval(self, value, as = None):
        if as:
            return as, value
        else:
            return None, value
    
    def render(self, ctx):
        g =  {'_self_':self}
        g.update(globals())
        save_as, value = eval('_self_._eval(%s)'%self.args, g, ctx)
        if save_as:
            ctx[save_as] = value
            return ''
        else:
            return str(value)

@register.tag
def python(parser, token):
    try:
        tag_name, args = token.contents.split(' ',1)
    except ValueError, e:
        raise template.TemplateSyntaxError, "%r tag requires two arguments" % token.contents[0]
    return PythonEvaluator(args)




#         print 'evaluating', repr(self.expression)
#         return ''
#         x = eval(self.expression, {}, ctx)
#         if self.save_as:
#             ctx[self.save_as] = x
#             return ''
#         else:
#             return str(x)
