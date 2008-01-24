from django import template
from django.template import resolve_variable
from boost_consulting.ecommerce.paypal import total_charge

register = template.Library()
class PayPalFee(template.Node):
    def __init__(self, price):
        self.price = price

    def render(self, ctx):
        print '*** ctx=', ctx
        actual_price = float(resolve_variable(self.price, ctx))
        return '%.2f'% (total_charge(actual_price) - actual_price)

@register.tag
def paypal_fee(parser, token):
    try:
        tag_name, args = token.split_contents()
    except ValueError, e:
        raise template.TemplateSyntaxError, "%r tag requires one arguments" % token.contents[0]
    return PayPalFee(args)

