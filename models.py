# -*- coding: utf-8 -*-
from datetime import *
from format import _12hr_time

## ---------------

import re
import unicodedata

__version__ = '0.0.1'


def slugify(string):

    """
    Slugify a unicode string.

    Example:

        >>> slugify(u"Héllø Wörld")
        u"hello-world"

    """

    return re.sub(r'[-\s]+', '-',
            unicode(
                re.sub(r'[^\w\s-]', '',
                    unicodedata.normalize('NFKD', unicode(string))
                    .encode('ascii', 'ignore'))
                .strip()
                .lower()))

## ---------------

class metamodel(type):
    class Objects(object):
        def __init__(self):
            self.__all = set()

        def all(self):
            return self.__all

    def __new__(cls, name, bases, dir):
        dir['objects'] = metamodel.Objects()
        return type.__new__(cls, name, bases, dir)

class Model(object):
    __metaclass__ = metamodel
    def __init__(self, **kw):
        for k,v in kw.items():
            setattr(self,k,v)

    def save(self):
        self.__class__.objects.all().add(self)

    def delete(self):
        self.__class__.objects.all().remove(self)

class Conference(Model):
    name = '<conference name>'
    start = finish = date.today()

    def __str__(self):
        return '%s %s' % (self.name,self.start.year)
    
class TimeBlock(Model):
    start = datetime.now()
    duration = 15 # in minutes
    conference = Conference()

    @property
    def finish(self):
        return self.start + timedelta(self.duration)

    def __str__(self):
        return self.start.strftime('%m/%d %a ') + '%s - %s' % (
            _12hr_time(self.start), _12hr_time(self.finish))

    def __cmp__(self,other):
        return cmp(self.start,other.start)

class Track(Model):
    name = '<track name>'
    description = '<track description> (unused)'
    conference = Conference()
    
    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

class Presenter(Model):
    last_name = '<presenter last name>'
    first_name = '<presenter first name>'
    email = '<presenter-email@domain.com>'
    bio = '<presenter\'s bio>'

    def full_name(self):
        return self.first_name + ' ' + self.last_name
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_absolute_url(self):
        return '/program/speakers#%s' % self.slug()

    def slug(self):
        return slugify(str(self))

    def __cmp__(self,other):
        return cmp(
            (self.last_name,self.first_name),
            (other.last_name,other.first_name)
            )

class Session(Model):
    title = '<session title>'
    
    # Presenters (should only be left blank for social events
    presenters = [Presenter()]

    # Abbreviation for session continuations in schedule
    short_title = '<session abbrev>'

    # Note to appear on schedule page
    schedule_note = ''
    
    #
    # Format
    #
    formats = ('Lecture','Tutorial','Keynote','Workshop', 'Experience Report',
               'Panel', 'Social Event')
    # should be one of the above
    format = formats[-1]

    #
    # Experience Level and Background
    #
    beginner = 1
    intermediate = 2
    advanced = 4
    level = beginner|intermediate|advanced

    level_names = (None, 'Beginner', 'Intermediate', 'Beginner/Intermediate', 'Advanced', '?', '?', 'Intermediate/Advanced',  'All')

    def level_name(self):
        return level or ''
        
    attendee_background = '<attendee background>'

    #
    # Content
    #
    description = '<session description>'


    # Boost library/tool names covered, e.g. "Regex, Build"',
    boost_components = ''
    
    track = Track()

    #
    # Scheduling
    #
    start = TimeBlock() # Starting Session Block

    # length in minutes
    duration = 90 

    def __str__(self):
        return ', '.join([s.last_name for s in self.presenters]) \
               + ': ' + (self.short_title or self.title)

    @property
    def display_name(self):
        return str(self)
    
    def get_absolute_url(self):
        return '/program/sessions#%s' % self.slug()

    def slug(self):
        return slugify(str(self))

    @property
    def finish(self):
        return self.start.start + timedelta(minutes=self.duration)

    def __init__(self, presenter=None, **kw):
        if presenter:
            kw['presenters'] = (presenter,)

        super(Session,self).__init__(**kw)
