from django.db import models
from datetime import *
from utils.format import _12hr_time

class Conference(models.Model):
    name = models.CharField(maxlength=100)
    # slug = models.SlugField(prepopulate_from=('name',))
    start = models.DateField('Date on which to start the schedule')
    finish = models.DateField('Date on which to end the schedule')

    def __str__(self):
        return self.name
    
    class Admin: pass

class TimeBlock(models.Model):
    # name = models.CharField(maxlength=100, primary_key=True, unique_for_date='start')
    start = models.DateTimeField()
    duration = models.SmallIntegerField('Duration in minutes', default=90)
    conference = models.ForeignKey(Conference)

    class Meta:
        ordering = ('start',)
        unique_together = (('start',),)
    
    class Admin:
        save_as = True

    @property
    def finish(self):
        return self.start + timedelta(minutes=self.duration)

    def __str__(self):
        return self.start.strftime('%m/%d %a ') + '%s - %s' % (
            _12hr_time(self.start), _12hr_time(self.finish))

class Track(models.Model):
    name = models.CharField(maxlength=100, primary_key=True)
    description = models.TextField()
    conference = models.ForeignKey(Conference)
    
    class Admin:
        list_display = ('name', 'description')

    def __str__(self):
        return self.name
        
class Presenter(models.Model):
    last_name = models.CharField(maxlength=100)
    first_name = models.CharField(maxlength=100)
    email = models.EmailField()
    bio = models.TextField()

    class Meta:
        ordering = ('last_name','first_name','email')

    class Admin:
        pass
        # list_display = ('first_name', 'last_name')

    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
class Session(models.Model):
    title = models.CharField(maxlength=200)
    
    presenters = models.ManyToManyField(
        Presenter, filter_interface = models.HORIZONTAL, related_name='Sessions')

    short_title = models.CharField(
        'Abbreviation for session continuations in schedule'
        , maxlength=50,blank=True)
    
    #
    # Format
    #
    formats = ('Lecture','Tutorial','Keynote','Workshop', 'Experience Report', 'Panel')
    format = models.CharField(
        maxlength=32,
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

    attendee_background = models.CharField(maxlength=200,blank=True)

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
    start = models.ForeignKey(TimeBlock,null=True)
    duration = models.SmallIntegerField('Duration in minutes', default=90)

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


    class Admin:
        pass
    
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

