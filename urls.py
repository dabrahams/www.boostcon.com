from django.conf.urls.defaults import *
from news.models import News
from news.feeds import NewsFeed
from boost_consulting.settings import serve_media

feeds = {
    'news': NewsFeed
}
    
urlpatterns = patterns('',
    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),

#    (r'^comments/', include('django.contrib.comments.urls.comments')),

    (r'^feed/(?P<url>[-\w]+)', 'django.contrib.syndication.views.feed',
     {'feed_dict': feeds}),

    (r'^community/photos/', include('stockphoto.urls')),
)

if serve_media:
    # Debug only - http://www.djangoproject.com/documentation/static_files/
    # explains why we shouldn't serve media from django in a release server.
    #              
    # For some reason I haven't yet discovered, the media/ URL seems to be
    # reserved for media used by django's admin module, so we use site-media
    urlpatterns += patterns(
        '',
        (r'^site-media/(?P<path>.*)$',
         'django.views.static.serve', {'document_root': 'media/'}))

# Generic views

news_parameters = {
    'queryset': News.objects.all(),
    'date_field': 'date'
}

urlpatterns += patterns(
    'django.views.generic.date_based',
   (r'^news/(?P<year>\d{4})/(?P<month>[A-Za-z]{3})/(?P<day>\d{1,2})/(?P<slug>(?:-|\w)+)$',
    'object_detail', dict(news_parameters, slug_field='slug')),
    
   (r'^news/(?P<year>\d{4})/(?P<month>[A-Za-z]{3})/(?P<day>\d{1,2})$',
    'archive_day',   news_parameters),
    
   (r'^news/(?P<year>\d{4})/(?P<month>[A-Za-z]{3})$',
    'archive_month', news_parameters),
    
   (r'^news/(?P<year>\d{4})$',
    'archive_year',  dict(news_parameters, make_object_list=True)),
    
   (r'^news$',
    'archive_index', dict(news_parameters, num_latest=4)),
)

urlpatterns += patterns(
    'boost_consulting.conference',
    (r'^admin/(?P<conference_name>.*)/schedule$', 'views.schedule_admin'),
    )

urlpatterns += patterns('django.views.generic',
# Enable this if you want a special homepage layout.                        
#    (r'^$', 'simple.direct_to_template', {'template': 'homepage.html'}),

    # admin and stockphoto both use a trailing-slash URL scheme, so we need to
    # make sure they always have one.                    
    (r'^admin(?P<base>(/[^/]+)*)$', 'simple.redirect_to', {'url': r'/admin%(base)s/'}),
    (r'^community/photos(?P<base>(/[^/]+)*)$', 'simple.redirect_to', {'url': r'/community/photos%(base)s/'}),
    (r'^(?P<base>.*)/$', 'simple.redirect_to', {'url': r'/%(base)s'}),
                        
    (r'^$', 'simple.redirect_to', {'url': r'/home'}),
    (r'^program/schedule$', 'simple.redirect_to', {'url': r'/program#schedule'}),
    (r'^community/wiki$', 'simple.redirect_to', {'url': r'/traq'}),
                        
    # keep the old redirects from about/shops in case people have linked there.
    (r'^(about|community)/shops/eu$', 'simple.redirect_to', {'url': r'http://boostcon.spreadshirt.net'}),
    (r'^(about|community)/shops/usa$', 'simple.redirect_to', {'url': r'http://boostcon.spreadshirt.com'}),
)

urlpatterns += patterns('',
    (r'^accounts/login/?$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/?$', 'django.contrib.auth.views.logout'),
)

urlpatterns += patterns(
    'boost_consulting',
    (r'(.*)$', 'pages.views.page'),
    )

