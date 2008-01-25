from django import template
from boost_consulting.utils.host import hostname

register = template.Library()
@register.inclusion_tag('checkout.html')
def checkout(price, request):
    return {
        'price': price,
        'this_url': 'http://'+hostname(request)+request.get_full_path()
        }

