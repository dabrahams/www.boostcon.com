from django import template
from django.template import resolve_variable
from boost_consulting.ecommerce.google_checkout import total_charge

register = template.Library()
class GoogleCheckoutFee(template.Node):
    def __init__(self, price):
        self.price = price

    def render(self, ctx):
        actual_price = float(resolve_variable(self.price, ctx))
        return '%.2f'% (total_charge(actual_price) - actual_price)

@register.tag
def google_checkout_fee(parser, token):
    try:
        tag_name, args = token.split_contents()
    except ValueError, e:
        raise template.TemplateSyntaxError, "%r tag requires one arguments" % token.contents[0]
    return GoogleCheckoutFee(args)

