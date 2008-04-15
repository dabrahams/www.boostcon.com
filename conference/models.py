from django.db import models
from datetime import *
from utils.format import _12hr_time
from django.template.defaultfilters import slugify

class Conference(models.Model):
    name = models.CharField(max_length=100, unique_for_year='start')
    # slug = models.SlugField(prepopulate_from=('name',))
    start = models.DateField('Date on which to start the schedule')
    finish = models.DateField('Date on which to end the schedule')

    def __str__(self):
        return '%s %s' % (self.name,self.start.year)
    
    class Admin: pass

class TimeBlock(models.Model):
    # name = models.CharField(max_length=100, primary_key=True, unique_for_date='start')
    start = models.DateTimeField()
    duration = models.SmallIntegerField('Duration in minutes', default=90)
    conference = models.ForeignKey(Conference)

    class Meta:
        ordering = ('start',)
        unique_together = (('start',),)
    
    class Admin:
        save_as = True
        list_filter = ('conference',)
        
    @property
    def finish(self):
        return self.start + timedelta(minutes=self.duration)

    def __str__(self):
        return self.start.strftime('%m/%d %a ') + '%s - %s' % (
            _12hr_time(self.start), _12hr_time(self.finish))

class Track(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    description = models.TextField()
    conference = models.ForeignKey(Conference)
    
    class Admin:
        list_display = ('name', 'description')

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
    
class Presenter(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField()

    def full_name(self):
        return self.first_name + ' ' + self.last_name
    
    class Meta:
        ordering = ('last_name', 'first_name', 'email')

    class Admin:
        list_display = ('last_name', 'first_name', 'email')

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def get_absolute_url(self):
        return '/program/speakers#%s' % self.slug()

    def slug(self):
        return slugify(str(self))
    
class Session(models.Model):
    title = models.CharField(max_length=200)
    
    presenters = models.ManyToManyField(
        Presenter
      , verbose_name = 'Presenters (should only be left blank for social events)'
      , filter_interface = models.HORIZONTAL
      , related_name='sessions'
      , blank=True
        )

    short_title = models.CharField(
        'Abbreviation for session continuations in schedule and admin interface'
        , max_length=50,blank=True)

    schedule_note = models.CharField(
        'Note to appear on schedule page', max_length=200, blank=True)
    
    #
    # Format
    #
    formats = ('Lecture','Tutorial','Keynote','Workshop', 'Experience Report',
               'Panel', 'Social Event')
    format = models.CharField(
        max_length=32,
        choices= tuple(zip([x.lower() for x in formats],formats)))

    #
    # Experience Level and Background
    #
    beginner = 1
    intermediate = 2
    advanced = 4

    level = models.SmallIntegerField(
        choices=(
            (beginner, 'Beginner'),
            (beginner|intermediate, 'Beginner/Intermediate'),
            (intermediate, 'Intermediate'),
            (intermediate|advanced, 'Intermediate/Advanced'),
            (advanced, 'Advanced'),
            (beginner|intermediate|advanced, 'All'),
            ),
        default=beginner|intermediate|advanced)

    def level_name(self):
        result = []
        for l in 'beginner','intermediate','advanced':
            if getattr(self,l) & self.level:
                result.append(l)
                
        if 0 < len(l) < 3:
            return '/'.join(l)
        else:
            return ''
        
    attendee_background = models.CharField(max_length=200,blank=True)

    #
    # Content
    #
    description = models.TextField()

    boost_components = models.TextField(
        'Boost library/tool names covered, e.g. "Regex, Build"',
        blank=True)
    
    track = models.ForeignKey(Track,blank=True,null=True)
        
    #
    # Scheduling
    #
    start = models.ForeignKey(TimeBlock, verbose_name = 'Starting Session Block', null=True)
    duration = models.SmallIntegerField('length (min)', default=90)

    _presenters = None
    
    def __init__(self, *args, **kw):
        
        if 'presenter' in kw:
            self._presenters = [kw['presenter']]
            del kw['presenter']
        elif 'presenters' in kw:
            self._presenters=kw['presenters']
            del kw['presenters']

        super(Session,self).__init__(*args, **kw)

    def save(self):
        super(Session,self).save()
        
        if self._presenters:
            self.presenters.add(*self._presenters)
            del self._presenters
            super(Session,self).save()
        
    def __str__(self):
        return ', '.join([s.last_name for s in self.presenters.all()]) \
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

    class Admin:
        list_display = ('display_name', 'duration', 'track', 'start')
        search_fields = ('title', 'presenters__last_name',
                         'presenters__first_name', 'start__start')
        
    class Meta:
        # These constraints are imperfect but should catch many common errors
        unique_together = (
            ('start','track'),          # only one session may start in a given
                                        # track at a given time
            
          # ('speakers', 'start'),      # a given speaker can only start one
                                        # session at a time.
                                        # But you can't do this with ManyToMany
                                        # fields in django.
            
            ('title',),                  # no two sessions can have the same title
            )

