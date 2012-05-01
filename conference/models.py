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
                    unicodedata.normalize('NFKD', string)
                    .encode('ascii', 'ignore'))
                .strip()
                .lower()))

## ---------------

class Model(object):
    def __init__(self, **kw):
        for k,v in kw.items():
            setattr(self,k,v)


class Conference(Model):
    name = '<conference name>'
    start = finish = date.today()

    def __str__(self):
        return '%s %s' % (self.name,self.start.year)
    
class TimeBlock(Model):
    start = datetime.now()
    duration = timedelta(minutes=15)
    conference = Conference()

    @property
    def finish(self):
        return self.start + self.duration

    def __str__(self):
        return self.start.strftime('%m/%d %a ') + '%s - %s' % (
            _12hr_time(self.start), _12hr_time(self.finish))

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

    levels = (None, 'Beginner', 'Beginner/Intermediate', 'Intermediate', 'Intermediate/Advanced', 'Advanced', 'All')

    # should be one of the above
    level = levels[-1]

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
