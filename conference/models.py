from django.db import models
from datetime import *

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
    
    def format_time(self):
        return self.start.strftime('%I:%M%p - ') + self.finish.strftime('%I:%M%p')
    
    def __str__(self):
        return self.start.strftime('%a ') + self.format_time()

class Track(models.Model):
    name = models.CharField(maxlength=100, primary_key=True)
    description = models.TextField()
    conference = models.ForeignKey(Conference)
    
    class Admin:
        list_display = ('name', 'description')

    def __str__(self):
        return self.name
        
class Speaker(models.Model):
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
    
    speakers = models.ManyToManyField(Speaker, filter_interface =
                                      models.HORIZONTAL, related_name='Sessions')
    short_title = models.CharField(
        'Abbreviation for session continuations in schedule'
        , maxlength=50,blank=True)
    
    #
    # Format
    #
    formats = ('Lecture','Tutorial','Keynote','Workshop', 'Experience Report', 'Panel')
    format = models.CharField(
        maxlength=32,
        choices= tuple(zip(formats,formats)))

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
    start = models.ForeignKey(TimeBlock)
    duration = models.TimeField()

    def __str__(self):
        return ', '.join([s.last_name for s in self.speakers.all()]) \
               + ': ' + (self.short_title or self.title)


    class Admin:
        pass
    
    class Meta:
        # These constraints are imperfect but should catch many common errors
        unique_together = (
            ('start','track'),          # only one session may start in a given
                                        # track at a given time
            
          # ('speakers', 'start'),      # a given speaker can only start one
                                        # session at a time
            
            ('title',),                  # no two sessions can have the same title
            )
    
def populate_db():
    #
    # Conference
    #
    boostcon07 = Conference(name='boostcon07',
                            start=date(2007,5,13),
                            finish=date(2007,5,18))
    
    boostcon07.save()

    #
    # TimeBlock
    #
    mon = [
        TimeBlock(start=datetime(2007,5,14,*t), conference=boostcon07)
        
        for t in ((9,00), (10,30), (2+12,30), (4+12,00))]

    for block in mon:
        block.save()
        
        for i,name in enumerate(('tue','wed','thu','fri')):
            copy = TimeBlock(start=block.start+timedelta(i+1),conference=block.conference)
            copy.save()
            locals()[name] = locals().get(name,[]) + [copy]

    #
    # Track
    #
    user = Track(name='User',description='user track',conference=boostcon07)
    user.save()
    
    dev = Track(name='Dev',description='developer track',conference=boostcon07)
    dev.save()

    
    
    
