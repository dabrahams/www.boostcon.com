from django.http import HttpResponse
from django.shortcuts import render_to_response
from conference.models import Conference, TimeBlock, Track

def schedule_admin(request, conference_name):
    conference = Conference.objects.get(name=conference_name)
    
    ctx = {
        'conference' : conference
        , 'time_blocks' : TimeBlock.objects.filter(conference=conference)
        , 'tracks' : Track.objects.filter(conference=conference)
        , 'title' : 'Schedule Administration'
        }
        
    return render_to_response('conference/schedule.html', ctx)
