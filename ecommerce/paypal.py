# Copyright David Abrahams 2008. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
import urllib
from boost_consulting.ecommerce import return_urls

def total_charge(amount_received):
    """Compute the amount we have to charge in order to receive a certain amount
    from PayPal after their fees.  Mostly useful for donations."""
    # paypal fees are 0.29 * charge + 0.30
    # amount_received = total_charge - (total_charge * 0.29 + 0.30)
    # actual_price = (1.0 - .029) * total_charge - 0.30
    return (float(amount_received) + 0.30) / (1.0 - .029)
   
def checkout_url(request, order):

    complete, canceled = return_urls(request,order)

    product = order.product
    destination = order.destination
    
    url = 'https://www.paypal.com/xclick/business=conservancy-boost@softwarefreedom.org&quantity=1&no_shipping=2&return=%(complete)s&cancel_return=%(canceled)s&currency_code=USD&no_shipping=1&image_url=http://boostcon.com/site-media/images/logo-small.gif' % locals()
    url += '&item_name=%s' \
        % urllib.quote_plus('%s (%s)' % (product.name, product.description))
    url += '&invoice=%d' % order.id
    url += '&amount=%.2f' % total_charge(product.price)
    url += '&shipping=%.2f' % float(order.shipping_rate)
    url += '&first_name=%s' % urllib.quote_plus(destination.first_name)
    url += '&last_name=%s' % urllib.quote_plus(destination.last_name)
    url += '&address1=%s' % urllib.quote_plus(destination.address1)
    url += '&address2=%s' % urllib.quote_plus(destination.address2)
    url += '&state=%s' % urllib.quote_plus(destination.state)
    url += '&zip=%s' % urllib.quote_plus(destination.zip)
    url += '&city=%s' % urllib.quote_plus(destination.city)
    url += '&night_phone_a=%s' % urllib.quote_plus(destination.phone)
    url += '&country=%s' % urllib.quote_plus(destination.country)
    url += '&email=%s' % urllib.quote_plus(request.user.email)

    return url
