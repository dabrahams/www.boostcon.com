from sphene.contrib.libs.common.utils.misc import cryptString, decryptString
from django.conf import settings
from boost_consulting.utils.host import hostname

def return_urls(request, order):
    order_hash = cryptString(settings.SECRET_KEY, str(order.id))
    host = hostname(request)
    completion_url = 'http://%(host)s/registration-complete/%(order_hash)s' % locals()
    cancel_url = 'http://%(host)s/registration-canceled/%(order_hash)s' % locals()
    return completion_url, cancel_url
    
