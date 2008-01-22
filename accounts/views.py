# Create your views here.


from django import newforms as forms
from django.conf import settings
from django.contrib.auth.models import User,Group
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import loader, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login as auth_login, logout as auth_logout
from accounts.models import Participant
from sphene.community.models import Group as Community, GroupMember as CommunityMember

from urllib import urlencode
from cgi import parse_qs as urldecode

from sphene.contrib.libs.common.utils.misc import cryptString, decryptString

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.clean_data.get('username')
        password = self.clean_data.get('password')

        if not (username and password):
            return self.clean_data

        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise forms.ValidationError(u'Invalid username or password')
        except:
            raise forms.ValidationError(u'Invalid username or password')

        return self.clean_data

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=2)
    first_name = forms.CharField(max_length=40, min_length=2)
    last_name = forms.CharField(max_length=40, min_length=2)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.clean_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError(u'Username has to be at least three characters long')
        try:
            user = User.objects.get(username=username)
        except Exception,e:
            return username
        raise forms.ValidationError(u'Username is already taken')

    def clean_email(self):
        email = self.clean_data.get('email')
        if User.objects.filter(email=email).count():
            raise forms.ValidationError(u'This email address is already in use')
        return email

    def clean_password(self):
        password = self.clean_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError(u'Password has to be at least six characters long')
        return password

    def clean(self):
        password = self.clean_data.get('password')
        password2 = self.clean_data.get('password2')

        if (password and password2) and (password != password2):
            self.password_mismatch = True
            raise forms.ValidationError(u'Passwords did not match')

        self.password_mismatch = False
        return self.clean_data

def register_or_login(request, login=False, group=None):

    next = request.REQUEST.get('next', '/')

    if request.POST:
        if login:
            login_form = LoginForm(request.POST, prefix='login')
            reg_form = RegistrationForm()

            if login_form.is_valid():
                user = authenticate(
                    username=login_form.clean_data['username']
                  , password=login_form.clean_data['password']
                )
                auth_login(request, user)

                request.session['account_message'] = 'Logged in successfully, welcome!'

                return HttpResponseRedirect(next)
        else:
            login_form = LoginForm(prefix='login')
            reg_form = RegistrationForm(request.POST)

            if reg_form.is_valid():
                regdata = reg_form.cleaned_data.copy()
                regdata.pop('password2')
                regdata['next'] = next
                
                email_address = regdata['email']
                
                subject = 'Email verification required for site %s' % group.get_name()

                validationcode = cryptString(settings.SECRET_KEY, urlencode(regdata))

                t = loader.get_template('accounts/account_verification_email.txt')
                c = {
                    'email': email_address,
                    'baseurl': group.baseurl,
                    'validationcode': validationcode,
                    'group': group,
                    }

                send_mail( subject, t.render(RequestContext(request, c)), None, [email_address] )
                return render_to_response( 'accounts/register_emailsent.html',
                                           { 'email': email_address },
                                           context_instance = RequestContext(request) )
    else:
        login_form = LoginForm(prefix='login')
        reg_form = RegistrationForm()

    return render_to_response('login_or_register.html', 
        RequestContext(request, {
            'reg_form': reg_form
          , 'login_form': login_form
          , 'next': next}))

class RegisterEmailAddress(forms.Form):
    email_address = forms.EmailField()
    
    def clean(self):
        if 'email_address' not in self.cleaned_data:
            return self.cleaned_data

        if User.objects.filter( email__exact = self.cleaned_data['email_address'] ).count() != 0:
            raise forms.ValidationError("Another user is already registered with the email address %s."
                                        % self.cleaned_data['email_address'] )
        return self.cleaned_data


def register(request, group = None):

    if request.method == 'POST':
        form = RegisterEmailAddress(request.POST)
        if form.is_valid():
            regdata = form.cleaned_data
            email_address = regdata['email_address']
            if not group:
                subject = 'Email verification required'
            else:
                subject = 'Email verification required for site %s' % group.get_name()
            validationcode = cryptString( settings.SECRET_KEY, email_address )
            t = loader.get_template('sphene/community/accounts/account_verification_email.txt')
            c = {
                'email': email_address,
                'baseurl': group.baseurl,
                'validationcode': validationcode,
                'group': group,
                }
            send_mail( subject, t.render(RequestContext(request, c)), None, [email_address] )
            return render_to_response( 'sphene/community/register_emailsent.html',
                                       { 'email': email_address,
                                         },
                                       context_instance = RequestContext(request) )
        pass
    else:
        form = RegisterEmailAddress()

    return render_to_response( 'sphene/community/register.html',
                               { 'form': form },
                               context_instance = RequestContext(request) )

username_re = r'^\w+$'

import re
email_extract_re = re.compile(r'^(?:^.*&)?email=([^&]+).*')

def register_hash(request, hashcode, group = None):
    params = dict([(x[0],x[1][0]) for x in urldecode(decryptString( settings.SECRET_KEY, hashcode )).iteritems()])
    next = params.pop('next', '/')
        
    # Validate the email address, etc.
    params['password2'] = params['password']
    reg_form = RegistrationForm( params )

    if reg_form.is_valid():
        # OK, create the new user
        vitals = reg_form.cleaned_data

        user = User(
            username=vitals['username']
            , first_name=vitals['first_name']
            , last_name=vitals['last_name']
            , email=vitals['email']
            )

        user.set_password(vitals['password'])
        user.save()
        
        user = authenticate(
            username = user.username, password = vitals['password'])
        
        auth_login(request, user)
        request.session['account_message'] = 'User account created. You are now logged in!'

        return HttpResponseRedirect(next)
    else:
        print '******* reg_form:', reg_form
        
    return render_to_response( 'login_or_register.html',
                               { 'form': reg_form },
                               context_instance = RequestContext(request) )


def logout(request):
    next = request.REQUEST.get('next', '/')
    auth_logout(request)
    request.session['account_message'] = 'You are now logged out!'
    return HttpResponseRedirect(next)


##############################################################
####
#### The following code was copied from the django captchas project.
#### and slightly modified.

try:

    from djaptcha.models import CaptchaRequest
    from cStringIO import StringIO
    import random
    import Image,ImageDraw,ImageFont
    
except:
    pass

# You need to get the font from somewhere and have it accessible by Django
# I have it set in the djaptcha's settings dir
#from django.conf.settings import FONT_PATH,FONT_SIZE

def captcha_image(request,token_id,group = None):
    """
    Generate a new captcha image.
    """
    captcha = CaptchaRequest.objects.get(id=token_id)
    text = captcha.text
    #TODO: Calculate the image dimensions according to the given text.
    #      The dimensions below are for a "X+Y" text
    image = Image.new('RGB', (40, 23), (39, 36, 81))
    # You need to specify the fonts dir and the font you are going to usue
    font = ImageFont.truetype(settings.FONT_PATH,settings.FONT_SIZE)
    draw = ImageDraw.Draw(image)
    # Draw the text, starting from (2,2) so the text won't be edge
    draw.text((2, 2), text, font = font, fill = (153, 204, 0))
    # Saves the image in a StringIO object, so you can write the response
    # in a HttpResponse object
    out = StringIO()
    image.save(out,"JPEG")
    out.seek(0)
    response = HttpResponse()
    response['Content-Type'] = 'image/jpeg'
    response.write(out.read())
    return response
