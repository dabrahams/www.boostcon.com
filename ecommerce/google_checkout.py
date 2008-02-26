# Copyright David Abrahams 2008. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django.conf import settings
import httplib
from boost_consulting.utils.dom import tag as _, xml_document
from xml.dom import minidom
from base64 import b64encode, b64decode

# Sandbox ID and key
MERCHANT_ID =  674749040905264
MERCHANT_KEY = 'OzjvzinyiBiq9SWPp0-lTg'

API_URL = '/api/checkout/v2/merchantCheckout/Merchant/'
if settings.DEBUG:
    DOMAIN = 'sandbox.google.com'
    API_URL = '/checkout'+API_URL
else:
    DOMAIN = 'checkout.google.com'
    try:
        from boost_consulting.secure.google_checkout import MERCHANT_ID, MERCHANT_KEY
    except:
        pass

def total_charge(amount_received):
    """Compute the amount we have to charge in order to receive a certain amount
    from Google Checkout after their fees."""
    # google checkout fees are 0.02 * charge + 0.20
    # amount_received = total_charge - (total_charge * 0.02 + 0.20)
    # amount_received = (1.0 - .02) * total_charge - 0.20
    return (float(amount_received) + 0.20) / (1.0 - 0.02)

def checkout_url(request, order):

    cart = xml_document(
        _('checkout-shopping-cart', xmlns="http://checkout.google.com/schema/2")[
        _('shopping-cart')[
            _.items[
                _.item[
                    _('item-name')[order.product.name],
                    _('item-description')[order.product.description],
                    _('unit-price', currency='USD')[total_charge(order.product.price)],
                    _.quantity[1]
                ]
            ]
        ],
        # Shipping information would go here
#        _('merchant-checkout-flow-support')[]
        ])

    req_xml = cart.toxml()
    hcon = httplib.HTTPSConnection(DOMAIN)
    hcon.putrequest('POST', API_URL + str(MERCHANT_ID))
    hcon.putheader('Content-Length', len(req_xml))
    hcon.putheader('Authorization', 'Basic ' + b64encode('%s:%s' % (MERCHANT_ID,MERCHANT_KEY)))
    hcon.putheader('Content-Type', 'application/xml; charset=UTF-8')
    hcon.putheader('Accept', 'application/xml; charset=UTF-8')
    hcon.endheaders()
    hcon.send(req_xml)

    response = minidom.parseString(hcon.getresponse().read())
    return response.documentElement.getElementsByTagName('redirect-url')[0].firstChild.nodeValue

