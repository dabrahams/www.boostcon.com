 # -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import datetime

class ShippingDestination(models.Model):
    first_name = models.CharField(maxlength=100)
    last_name = models.CharField(maxlength=100)
    address1 = models.CharField(maxlength=100)
    address2 = models.CharField(maxlength=100, blank=True)
    city = models.CharField(maxlength=100)
    state = models.CharField(maxlength=100, blank=True)
    zip = models.CharField(maxlength=100)
    country = models.CharField(maxlength=100)
    phone = models.CharField(maxlength=50)

    class Admin:
        pass

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

class Customer(models.Model):
    user = models.ForeignKey(User, unique=True)
    destination = models.ForeignKey(ShippingDestination)

    # Default overrides for PDF generation.  I know this mixes presentation with
    # data structure.  So sue me.
    pdf_user = ('email', lambda x: x.user.email)
    pdf_destination = ('id number', lambda x: x.id)
                       
    class Admin:
        pass

    def __str__(self):
        return self.user.username

class Product(models.Model):
    name = models.CharField(maxlength=100)
    slug = models.SlugField(prepopulate_from=('name',))
    description = models.CharField(maxlength=500)
    price = models.FloatField(max_digits=5, decimal_places=2)

    class Admin:
        pass

    def __str__(self):
        return self.name

order_states = [('P','pending'), ('S','shipped'), ('D','dismissed')]

class Order(models.Model):
    customer = models.ForeignKey(Customer)
    product = models.ForeignKey(Product)
    destination = models.ForeignKey(ShippingDestination)
    shipping = models.CharField(maxlength=100)
    shipping_rate = models.FloatField(max_digits=5, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    state = models.CharField(maxlength=1, choices=order_states, default='P')
    comment = models.TextField(blank=True)

    # More default overrides for PDF generation.
    pdf_state = None
    pdf_time = None
    pdf_destination = ('shipping address',None)
    pdf_shipping = ('shipping method',None)
    
    def display_customer(self):
        return '<a href="/admin/ecommerce/customer/%s/">%s</a>' % (self.customer.id, str(self.customer))
    display_customer.allow_tags = True
    display_customer.short_description = 'Customer'

    def display_destination(self):
        return '<a href="/admin/ecommerce/shippingdestination/%s/">%s</a>' % (
            self.destination.id, str(self.destination))
    display_destination.allow_tags = True
    display_destination.short_description = 'Destination'

    class Admin:
        fields = (
            (None, {'fields': 
                ('customer', 'product', 'destination', 
                 'shipping', 'shipping_rate', 'time', 
                 'state', 'comment')}
            ),
        )
        list_display = ('id', 'display_customer', 'display_destination', 'product', 'time', 'state', 'comment')
        list_filter = ('state',)

    def __str__(self):
        return '%s (%s->%s, %s)' % ( \
            self.id, self.product.name, self.destination.last_name, self.destination.first_name
        )

