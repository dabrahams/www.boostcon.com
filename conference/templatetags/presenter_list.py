from django import template

register = template.Library()
@register.inclusion_tag('conference/presenter_list.html', takes_context=True)
def presenter_list(context):
    """Trivial inclusion tag that includes the presenter list template.

Why isn't there a built-in inclusion tag that does exactly this?
"""
    return context

