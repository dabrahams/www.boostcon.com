#!/usr/bin/env python
# Issue registration invitations to the users listed in the given .csv file.
import os, sys
sys.path+= ['..', '../..']
os.environ['DJANGO_SETTINGS_MODULE'] = 'boost_consulting.settings'

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
# from django.template.context import Context
from django.http import HttpRequest
from django.template import loader, Context
from django.core.mail import send_mail

from sphene.contrib.libs.common.utils.misc import cryptString, decryptString

import csv

class MissingHeading(Exception):
    pass

def parse_registrations(filename):
    r = csv.reader(open(filename))
    headings = [x.lower() for x in r.next()]
    for x in r:
        yield dict(zip(headings,x))
    
import re
email_address_re = re.compile(r'[^<]*<([^>]+@[^>]+)>\s*')

if __name__ == "__main__":

     for vitals in parse_registrations(sys.argv[1]):

        m = email_address_re.match(vitals['email'])
        if (m):
            address = m.groups(1)
            vitals['email'] = address
        else:
            address = vitals['email']
        
        # if the email is unknown...
        if User.objects.filter(
          Q( email__exact = address ) | Q( email__endswith = '<%s>'%address)
        ).count() == 0:
            
            validationcode = cryptString(
                settings.SECRET_KEY,
                '&'.join([
                    'first_name=%(first)r',
                    'last_name=%(last)r',
                    'state=%(jurisdiction)r',
                    'zip=%(postal code)r',
                    'groups=list(Group.objects.filter(Q(name__exact="2007 Attendees")%s%s))'
                    % (('s' in vitals['role']) and '|Q(name__exact="2007 Speakers")' or '',
                       ('o' in vitals['role']) and '|Q(name__exact="2007 Organizers")' or ''
                            ),
                    'is_staff=True', # Need to be "on staff" so they can add photos :(
                    ] + [
                        '%s=%%(%s)r' % (x,x) for x in
                        'email','address1','address2','affiliation','country','title','phone','fax'
                        ])
                % vitals
                )
            
            t = loader.get_template('registration/invitation_email.txt')
            
            send_mail(
                'Invitation to BoostCon community portal',
                t.render(
                    Context(
                        { 'validationcode': validationcode, 'firstname':vitals['first'], }
                        )),
                
                'BoostCon Organizers <boostcon-plan@lists.boost-consulting.com>',
                [address]
                )

    
    
