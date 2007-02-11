from django.db import models

class Conference(models.Model):
    name = models.CharField(maxlength=100)
    # slug = models.SlugField(prepopulate_from=('name',))
    start = models.DateField('Date on which to start the schedule')
    finish = models.DateField('Date on which to end the schedule')

    def __str__(self):
        return self.name
    
    class Admin: pass

class TimeBlock(models.Model):
    name = models.CharField(maxlength=100, primary_key=True)
    start = models.TimeField()
    finish = models.TimeField()
    conference = models.ForeignKey(Conference)
    class Admin: pass

    def __str__(self):
        return self.name

class Track(models.Model):
    name = models.CharField(maxlength=100, primary_key=True)
    description = models.TextField()
    conference = models.ForeignKey(Conference)
    
    class Admin:
        list_display = ('name', 'description')

    def __str__(self):
        return self.name
        
    

