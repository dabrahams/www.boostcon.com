 # -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class Participant(models.Model):
    user = models.ForeignKey(User, unique=True)
    
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    jurisdiction = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    phone = models.PhoneNumberField()
    fax = models.PhoneNumberField()

    # delegate these properties to the User
    for a in 'first_name','last_name','email','groups','is_staff':
        locals()[a] = property(
            lambda self,a=a: getattr(self.user,a),
            lambda self,v,a=a: setattr(self.user,a,v))

    def save(self):
        self.user.save()
        models.Model.save(self)
        
    class Admin:
        pass

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

