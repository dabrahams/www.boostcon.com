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

    (r'^comments/', include('django.contrib.comments.urls.comments')),

    (r'^feed/(?P<url>[-\w]+)', 'django.contrib.syndication.views.feed',
     {'feed_dict': feeds}),
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

urlpatterns += patterns('django.views.generic',
    (r'^$', 'simple.direct_to_template', {'template': 'homepage.html'}),
    (r'^admin(.*[^/])$', 'simple.redirect_to', {'url': r'admin\1/'}),

#      (r'^news$', 'list_detail.object_list', {'queryset': news_set}),
#      (r'^news/(?P<object_id>\d+)$', 'list_detail.object_detail', {'queryset':
#                                                                    news_set}),
                        
    (r'^(?P<base>.*)/$', 'simple.redirect_to', {'url': r'/%(base)s'})
)

urlpatterns += patterns('',
    (r'^customers/', include('boost_consulting.customers.urls'))
)

urlpatterns += patterns(
    'boost_consulting',
    (r'^test/(.*)$', 'formtest.views.test'),
    (r'^test$', 'formtest.views.test', {'id': None}),
    (r'^step1/(?P<slug>[-\w]+)$', 'formtest.views.step1'),
    (r'^step1$', 'formtest.views.step1'),
    (r'^step2$', 'formtest.views.step2'),
    (r'(.*[^/])$', 'pages.views.page'),
    )

