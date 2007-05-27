#!/usr/bin/env python
## Generate a human readable 'random' password
## password  will be generated in the form 'word'+digits+'word' 
## eg.,nice137pass
## parameters: number of 'characters' , number of 'digits'
## Pradeep Kishore Gowda <pradeep at btbytes.com >
## License : GPL 
## Date : 2005.April.15
## Revision 1.2 
## ChangeLog: 
## 1.1 - fixed typos 
## 1.2 - renamed functions _apart & _npart to a_part & n_part as zope does not allow functions to 
## start with _

from trac.env import Environment
from django.contrib.auth.models import User

def nicepass(alpha=6,numeric=2):
    """
    returns a human-readble password (say rol86din instead of 
    a difficult to remember K8Yn9muL ) 
    """
    import string
    import random
    vowels = ['a','e','i','o','u']
    consonants = [a for a in string.ascii_lowercase if a not in vowels]
    digits = string.digits
    
    ####utility functions
    def a_part(slen):
        ret = ''
        for i in range(slen):			
            if i%2 ==0:
                randid = random.randint(0,20) #number of consonants
                ret += consonants[randid]
            else:
                randid = random.randint(0,4) #number of vowels
                ret += vowels[randid]
        return ret
    
    def n_part(slen):
        ret = ''
        for i in range(slen):
            randid = random.randint(0,9) #number of digits
            ret += digits[randid]
        return ret
        
    #### 	
    fpl = alpha/2		
    if alpha % 2 :
        fpl = int(alpha/2) + 1 					
    lpl = alpha - fpl	
    
    start = a_part(fpl)
    mid = n_part(numeric)
    end = a_part(lpl)
    
    return "%s%s%s" % (start,mid,end)

import csv

class MissingHeading(Exception):
    pass

def names_and_emails(filename):
    r = csv.reader(open(filename))
    headings = [x.lower() for x in r.next()]
    first = headings.index('first')
    if first < 0:
        raise MissingHeading, 'first'
    last = headings.index('last')
    if last < 0:
        raise MissingHeading, 'last'
    email = headings.index('email')
    if email < 0:
        raise MissingHeading, 'email'
    
    return [ x[first],x[last],x[email] for x in r ]

import os

def system(cmd):
    print cmd
    os.system(cmd)
    
def permission(args):
    system('trac-admin /usr/local/boost/share/tracs/boostcon permission '+args)

if __name__ == "__main__":
    tracenv = Environment('/usr/local/share/tracs/boostcon')
    
    pass_file = open('/usr/local/etc/boostcon/trac-passwd', 'a+b')
    pass_file.seek(0)

    old_passwds = pass_file.readlines()
    old_logins = set( [ l[:l.find(':')] for l in old_passwds ] )

    db = tracenv.get_db_cnx()
    known_emails = set()
    for username,name,email in tracenv.get_known_users(db):
        if '@' in username:
            known_emails.add(username)
        if '@' in email:
            known_emails.add(email)
            
    ne = names_and_emails('/tmp/BoostReg.csv')

    new_logins = {}

    new_trac_session_attrs = []
    new_trac_perms = []
    for first,last,email in ne:
        if not email in known_emails:
            new_trac_session_attrs += [
                (email, 1, 'name', first + ' ' + last),
                (email, 1, 'email', email)
                ]
            
        if not email in old_logins and not email in new_logins:
            new_logins[email] = nicepass()
        new_trac_perms.append((email,'attendee_2006'))

    new_passwds = ['%s:%s' % (l, crypt.crypt(p)) for l,p in new_logins]

    #
    # Compose emails
    #
    message = """From: BoostCon Organizers <boostcon-plan@lists.boost-consulting.com>
To: %(first)s %(last)s <%(email)s>
Subject: Photos, wiki, and updated slides at http://boostcon.com

Dear %(first)s %(last)s,

Thanks for your participation in BoostCon'07!  We've just
launched a community portal with:

* a Photo gallery where you can upload your portrait and snapshots
  from the event.

* a Wiki where you can collaborate with other attendees
  
* a private Wiki area where you can download updated slide sets,
  and you can post anything that you only want seen by other
  BoostCon'07 attendees.

* a set of discussion forums (http://boostcon.com/traq/discussion)
  
where you can upload photos
"""

    #
    # Put these users on staff in Django and give them permission to add photos
    #
    new_django_users = []
    old_django_users = User.objects.all()
    from django.db.models import Q
    for first,last,email in ne:
        matches = old_django_users.filter(
            Q(email = email)
            | Q(email__endswith = '<%s>'%email)
            | Q(username = email))
        
        if matches.count() == 0:
            matches = [
                User(
                    username=email, is_staff=True, is_active=False,
                    is_superuser=False) ] 

        for u in matches:
            u.is_staff = True
            u.user_permissions.add('gallery.add_photo')
            new_django_users.append(u)

    #
    # Start committing things.  Hopefully by now we've found any crucial errors.
    #
    
    #
    # update the trac session database with usernames and emails
    #
    cursor = db.cursor()
    cursor.executemany("INSERT INTO session_attribute VALUES (%s,%s,%s,%s)",
                       new_trac_session_attrs)
    cursor.executemany("INSERT INTO permission VALUES (%s, %s)",
                       new_trac_perms)
    
    #
    # update the passwd file 
    #
    pass_file.seek(0,2)
    
    # add a trailing newline if necessary
    if old_passwds[-1][-1] != '\n':
        pass_file.write('\n')
        
    pass_file.write('\n'.join(new_passwds))

    # save django users
    for u in new_django_users: u.save()
    
    #
    # Send email notifications
    #
    
    
