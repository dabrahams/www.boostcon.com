from django import template
from boost_consulting.utils.host import hostname

register = template.Library()
@register.inclusion_tag('conference/session_list.html', takes_context=True)
def session_list( context ):
    """Trivial inclusion tag that includes the session list template.

Why isn't there a built-in inclusion tag that does exactly this?
"""
    return context

