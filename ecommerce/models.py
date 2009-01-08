 # -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
import datetime

class ShippingDestination(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    zip = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

class ShippingDestinationAdmin(admin.ModelAdmin):
    pass
admin.site.register(ShippingDestination, ShippingDestinationAdmin)

class Customer(models.Model):
    user = models.ForeignKey(User, unique=True)
    destination = models.ForeignKey(ShippingDestination)

    # Default overrides for PDF generation.  I know this mixes presentation with
    # data structure.  So sue me.
    pdf_user = ('email', lambda x: x.user.email)
    pdf_destination = ('id number', lambda x: x.id)
                       

    def __str__(self):
        return self.user.username

class CustomerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Customer, CustomerAdmin)

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    shippable = models.BooleanField()
    prerequisite = models.ForeignKey('self',blank=True,null=True)

    def __str__(self):
        return self.name

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
admin.site.register(Product, ProductAdmin)

order_states = [('P','pending'), ('S','shipped'), ('D','dismissed')]

class Order(models.Model):
    customer = models.ForeignKey(Customer)
    product = models.ForeignKey(Product)
    destination = models.ForeignKey(ShippingDestination)
    shipping = models.CharField(max_length=100)
    shipping_rate = models.DecimalField(max_digits=5, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=1, choices=order_states, default='P')
    google_id = models.CharField(max_length=100,null=True)
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

    def __str__(self):
        return '%s (%s->%s, %s)' % ( \
            self.id, self.product.name, self.destination.last_name, self.destination.first_name
        )

class OrderAdmin(admin.ModelAdmin):
    fields = ('customer', 'product', 'destination',
            'shipping', 'shipping_rate',
            'state', 'google_id', 'comment')

    list_display = (
            'id', 'display_customer', 'display_destination',
            'product', 'time', 'state', 'comment')

    list_filter = ('state',)

admin.site.register(Order, OrderAdmin)


