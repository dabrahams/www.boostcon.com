 # -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import PhoneNumberField

class Participant(models.Model):
    user = models.ForeignKey(User, unique=True)
    
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    jurisdiction = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    phone = PhoneNumberField()
    fax = PhoneNumberField()

    # delegate these properties to the User
    for a in 'first_name','last_name','email','groups','is_staff':
        locals()[a] = property(
            lambda self,a=a: getattr(self.user,a),
            lambda self,v,a=a: setattr(self.user,a,v))

    def save(self):
        self.user.save()
        models.Model.save(self)
        
    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

