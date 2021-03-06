# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseServerError
from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from models import *
import paypal
import google_checkout

from sphene.contrib.libs.common.utils.misc import cryptString, decryptString
from django.conf import settings
from boost_consulting.utils.host import hostname

import boost_consulting.shipping as shipping

from decimal import Decimal

sorted_countries = shipping.COUNTRIES.items()
sorted_countries.sort()
country_choices = [('', '-- Select --')]
country_choices.extend([(code,name) for name,code in sorted_countries])
state_choices = [('', '-- Select --')]
state_choices.extend([(s,s) for s in shipping.STATES])

class Step1Form(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    address1 = forms.CharField(max_length=100)
    address2 = forms.CharField(max_length=100, required=False)
    state = forms.ChoiceField(choices=state_choices, required=False)
    city = forms.CharField(max_length=100)
    zip = forms.CharField(max_length=20)
    country = forms.ChoiceField(choices=country_choices)
    phone = forms.CharField(max_length=50)

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state and self.data.get('country') == 'US':
            raise forms.ValidationError(u'State is required for US addresses')
        return state
    
step1_fields = Step1Form.base_fields.keys()

def step1(request, slug = None):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login?next=%s' % request.path)

    has_errors = False

    if 'zip' in request.POST:
        # POST will only contain values like 'zip' if this request is a button
        # press starting at the step1 screen (and not arriving there from
        # elsewhere).

        # Re-fill and validate the form
        form = Step1Form(request.POST)
        has_errors = not form.is_valid()
        product = get_object_or_404(Product, id=request.session['product'])
        
    else:
        # We are arriving in the form from elsewhere
        product = get_object_or_404(Product, slug=slug)

        # Grab some things with which we initialize the form, even if no
        # Customer record exists for this user
        initial={'first_name':request.user.first_name,
                 'last_name':request.user.last_name}
        
        try:
            # See if we can find the customer record, with an associated
            # shipping destination
            customer = Customer.objects.get(user=request.user)
            
            destination = customer.destination

            # Grab as much information as possible from the destination
            for f in step1_fields:
                initial[f] = getattr(destination,f)

            if product.meets_prerequisite(customer) == False:
                return render_to_response('invalid_registration.html',RequestContext(request))
        except:
            # No customer record found, shipping destination missing, or not
            # quite completely formed.
            if product.prerequisite != None:
                return render_to_response('invalid_registration.html',RequestContext(request))

        # Initialize the form, unbound, with as much information as we could get
        form = Step1Form(initial=initial)

        request.session['product'] = product.id

    if request.POST and form.is_valid():
        data = form.cleaned_data

        # Compute rates for fedex ground and fedex express
        def fedex_rate(carrier, **kw):
            return shipping.create('FedEx', 'AvailableRates',
            {
            'account_number': '361927826', # a 9 digit number
            'meter_number': '7340835',
            },
            carrier=carrier,
            from_state='MA',
            from_zip_code='02143',
            to_state=data['state'].encode('utf-8'),
            to_zip_code=data['zip'],
            to_country=data['country'],
            weight=0.5,
            **kw
        )
        
        express_rate = fedex_rate(carrier = 'FDXE', packaging='FEDEXENVELOPE')
        ground_rate = fedex_rate(carrier = 'FDXG')

        try:
            if product.shippable:
                rates = express_rate.getResponse(returnAllResults=True) + \
                    ground_rate.getResponse(returnAllResults=True)

                if data['country'] == 'US':
                    rates.append(('Priority mail', 5.25, None))

                    request.session['shipping-options'] = rates

            destination,destination_created = ShippingDestination.objects.get_or_create(
                ** dict((f,data[f]) for f in step1_fields)
                )

            if destination_created:
                destination.save()

            customer, customer_created = Customer.objects.get_or_create(
                user = request.user, defaults = {'destination': destination})

            if not customer_created:
                # Save the customer's last shipping destination
                customer.destination = destination
                customer.save()
                
            destination.save()

            request.session['customer'] = customer.id
            request.session['shipping-destination'] = destination.id

        except Exception, err:
            form.errors['__all__'] = str(err)
            return render_to_response('step1.html', 
                RequestContext(request, {'form': form, 'has_errors': True, 'google_merchant_id':609132488541913}))

        if product.shippable:
            return HttpResponseRedirect('/checkout-2')
        else:
            return create_and_send_order(request)

    return render_to_response('step1.html', 
        RequestContext(request, {'form': form, 'has_errors': has_errors,
                                 'product': product, 'google_merchant_id':609132488541913}))

def order_complete(request, status, hashcode):
    order_id = int(decryptString( settings.SECRET_KEY, hashcode ))
    order = Order.objects.get(id=order_id)
    order.state = status == 'complete' and 'S' or 'D'
    order.save()
    return HttpResponseRedirect(request.path.endswith('/') and '..' or '.')

def create_and_send_order(request, shipping_method='None', shipping_rate=0):
    customer = Customer.objects.get(id=request.session['customer'])
    destination = ShippingDestination.objects.get(id=request.session['shipping-destination'])

    product = get_object_or_404(Product, id=request.session['product'])
    if product.meets_prerequisite(customer) == False:
        return render_to_response('invalid_registration.html',RequestContext(request))

    # Should we delete? Back button doesn't work very well if we do.
    #del request.session['customer']
    #del request.session['shipping-destination']
    #del request.session['shipping-options']
    #del request.session['product']

    order = Order(
        customer = customer
      , product = product
      , destination = destination
      , shipping = shipping_method
      , shipping_rate = Decimal(str(shipping_rate))
    )

    if 'orderform' in request.POST:
        return order_pdf(order)

    order.save()

    if 'google.x' in request.POST:
        url = google_checkout.checkout_url(request, order)

    elif 'paypal.x' in request.POST:
        url = paypal.checkout_url(request, order)
    
    return HttpResponseRedirect(url)
    
def step2(request):
    shippable = get_object_or_404(Product, id=request.session['product']).shippable
    if not shippable or not 'shipping-options' in request.session:
        return HttpResponseRedirect('/checkout-1')

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login?next=%s' % request.path)

    if request.POST:
        if not 'shipping' in request.POST:
            return render_to_response('step2.html', 
                  RequestContext(request,{
                      'choices': request.session['shipping-options'],
                      'error': 'Select a shipping method'
                  }))

        shipping_options = request.session['shipping-options']

        shipping_option_index = int(request.POST['shipping'])
        if shipping_option_index < 0 or shipping_option_index >= len(shipping_options):
            return render_to_response('step2.html', 
                RequestContext(request,{
                    'choices': request.session['shipping-options'],
                    'error': 'Select a shipping method'
                }))

        selected_shipping = shipping_options[shipping_option_index]

        return create_and_send_order(
            request,
            shipping_method=selected_shipping[0],
            shipping_rate=selected_shipping[1]
            )
        
    return render_to_response(
        'step2.html', 
        RequestContext(request,{'choices': request.session['shipping-options']}))


#
# Begin code for generating PDFs from database records
#
from reportlab.platypus.tables import Table
from reportlab.lib import colors

# Return s without the given suffix, if present
def rstrip_suffix(s, suffix):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    else:
        return s

# Given a database object, return the names of fields with which that object was
# defined.  Given a dict, return its keys.
def fieldnames(x):
    try:
        fields = x._meta.fields
    except AttributeError:
        return x.keys()
    return [rstrip_suffix(f.get_attname(),'_id') for f in fields]

# Given a database object or a dict, and a field name, get the PDF
# representation of that field's name and value.  This is probably much more
# complicated and general than we need it to be.  Consider rewriting this whole
# business.
def get_field(x, name):
    if isinstance(x, dict):
        return name, x[name]
    try:
        # if the Model has an attribute called pdf_<fieldname>, allow that to
        # override the existing value
        att = getattr(x,'pdf_'+name)
        
    except AttributeError:
        # Silence a couple of seldom-wanted fields
        if name in ('id','slug'):
            return name,None
        
        # just get the attribute and return it
        att = getattr(x, name)
        return name, att

    # Still working with a 'pdf_...' override; the default
    # field title is its name
    title = name

    # if the field was a tuple, assume it's (title, v)
    if isinstance(att, tuple):
        title = att[0] or name
        value = att[1]
        # if v is None, use the field's actual value (renaming the title).
        # otherwise, work with the v as the value
        if value is None:
            value = getattr(x, name)
    else:
        # the field was not a tuple, assume were overriding just its
        # representation
        value = att

    try:
        # if the value is callable on the object, do that
        value = value(x)
    except: pass
            
    return title,value
    

# Generate a PDF table representing x, a Model instance.
def printfields(x, suffix_rows = [], colWidths = (None,None)):
    try:
        fields = fieldnames(x)
    except AttributeError:
        return unicode(x)
    
    rows = []
    
    for f in fields:
        title,v = get_field(x,f)
        if v is None: continue
        title = ' '.join([ w.capitalize() for w in title.replace('_',' ').split() ])
        rows += [['%s:'% title, printfields(v)]]

    rows += suffix_rows
    
    t = Table(rows,
              colWidths = colWidths,
              style=[
            #('FONT',(0,0),(-1,1),'Times-Bold',10,12),
            ('FONT',(0,0),(-1,-1),'Helvetica',8,8),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    return t
            
def order_pdf(order):
   # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=boostpro.pdf'

    from cStringIO import StringIO
    buffer = StringIO()

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, TA_CENTER
    from reportlab.rl_config import defaultPageSize
    from reportlab.lib.units import inch

    
    PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = 'Helvetica'
    
    def page_template(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold',16)
        canvas.setFont('Times-Roman',9)

        from time import gmtime, strftime
        canvas.drawString(inch, 0.75 * inch, strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime()))
        canvas.restoreState()

    Story = [
        Image('media/images/logo.gif'), Spacer(1,0.25*inch),
        Paragraph('Order Form', ParagraphStyle('title', style,
                                                        fontSize=20, alignment=TA_CENTER)),
        Spacer(1,1*inch)]
    
    fields = 'customer,product,destination,shipping,shipping_rate,time,state,comment'.split(',')

    total_price = order.product.price + order.shipping_rate
    
    Story.append(printfields(order, [['Total:', 'USD %.2f' % total_price]], colWidths=(1.5*inch,None)))
    Story.append(Spacer(1,1*inch))
    Story.append(Paragraph("""
    To pay by check, please print this form and send it with a check for the
    total of USD %.2f, drawn on a U.S. bank account, to:
    """ % total_price, style))
    Story.append(Spacer(1,0.2*inch))
    Story.append(Preformatted("""
    Orders
    BoostPro Computing
    45 Walnut St.
    Somerville, MA 02143
    """, style))
    
    SimpleDocTemplate(buffer).build(Story, onFirstPage=page_template)
        
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def google_callback(request):
    # Technically, it would be better practice to send some XML back as well,
    # but using HTTP response codes is sufficient for the Google Checkout
    # notification API.
    try:
        google_checkout.notify(request)
        return HttpResponse()
    except:
        return HttpResponseServerError()
