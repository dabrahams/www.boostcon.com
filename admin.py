from django.contrib import admin
from models import *

class ConferenceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Conference, ConferenceAdmin)

class TimeBlockAdmin(admin.ModelAdmin):
    save_as = True
    list_filter = ('conference',)
admin.site.register(TimeBlock, TimeBlockAdmin)

class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
admin.site.register(Track, TrackAdmin)

class PresenterAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email')
admin.site.register(Presenter, PresenterAdmin)

class SessionAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'duration', 'track', 'start')
    search_fields = ('title', 'presenters__last_name',
                     'presenters__first_name', 'start__start')
admin.site.register(Session, SessionAdmin)

