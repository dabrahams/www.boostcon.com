# Copyright David Abrahams 2008. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django.conf import settings
import httplib
import re
from boost_consulting.utils.dom import dashtag as _, xml_document
from xml.dom import minidom
from base64 import b64encode, b64decode
from boost_consulting.ecommerce.models import Order

# Sandbox ID and key
MERCHANT_ID =  '766162824246335' #674749040905264
MERCHANT_KEY = 'QvnSBCdQJvB8xRKgBO52JA' #'OzjvzinyiBiq9SWPp0-lTg'

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
        _.checkout_shopping_cart(xmlns="http://checkout.google.com/schema/2")[
        _.shopping_cart[
            _.items[
                _.item[
                    _.item_name[order.product.name],
                    _.item_description[
                        order.product.description
                        + ' [BoostCon Order ID: %d]' % order.id
                        ],
                    _.unit_price(currency='USD')[total_charge(order.product.price)],
                    _.quantity[1]
                ]
            ],
            _.merchant_private_data[
                _.order_id[order.id],
                _.customer_id[order.customer.id],
                _.comment[ order.comment ]
                ]
            ]
        ],
        # Shipping information would go here
#        _('merchant-checkout-flow-support')[]
        )

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

def notify(request):
    file = open('/home/jim/thegooge','a')
    file.write('Incoming data:\n---------------\n')
    file.write(request.raw_post_data)
    file.write('\n\n')
    file.close()

    # Ensure that the merchant ID and key match
    match = re.match(r'^Basic (.*)$', request.META['HTTP_AUTHORIZATION'])
    if match is None:
        raise Exception('invalid HTTP Authorization')

    notify_id,notify_key = b64decode( match.group(1) ).split(':')
    if notify_id != MERCHANT_ID or notify_key != MERCHANT_KEY:
        raise Exception('id or key does not match')

    # Forward the XML onto the appropriate handler
    notify_xml = minidom.parseString(request.raw_post_data)
    notify_type = notify_xml.documentElement.tagName
    if notify_type == 'new-order-notification':
        notify_new_order(notify_xml)
    elif notify_type == 'order-state-change-notification':
        notify_order_state(notify_xml)

# Simple helper function to get the text contents of an XML node. XPath would be nicer.
def get_xml_text(xml_data,node_name):
    return xml_data.documentElement.getElementsByTagName(node_name)[0].firstChild.nodeValue

# Update the Google Checkout order # so that we can find the order in subsequent callbacks
def notify_new_order(notify_xml):
    private_data = notify_xml.documentElement.getElementsByTagName('merchant-private-data')[0]
    order_id = int(private_data.getElementsByTagName('order-id')[0].firstChild.nodeValue)
    google_id = int(get_xml_text(notify_xml,'google-order-number'))

    order = Order.objects.get(id = order_id)
    order.google_id = google_id
    order.save()

def notify_order_state(notify_xml):
    google_id = get_xml_text(notify_xml,'google-order-number')
    new_state = get_xml_text(notify_xml,'new-fulfillment-order-state')
    old_state = get_xml_text(notify_xml,'previous-fulfillment-order-state')

    if new_state == old_state:
        return

    if new_state == 'DELIVERED':
        order = Order.objects.get(google_id = google_id)
        order.state = 'S' # shipped
        order.save()
    elif new_state == 'WILL_NOT_DELIVER':
        order = Order.objects.get(google_id = google_id)
        order.state = 'D' # dropped
        order.save()        
