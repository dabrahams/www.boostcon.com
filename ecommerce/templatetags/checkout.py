from django import template
register = template.Library()
@register.inclusion_tag('checkout.html')
def checkout():
    return {}

