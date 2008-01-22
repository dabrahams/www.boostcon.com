from django.conf.urls.defaults import *
from news.models import News
from news.feeds import NewsFeed
from boost_consulting import settings

feeds = {
    'news': NewsFeed
}
    
urlpatterns = patterns('',
    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),

    (r'^feed/(?P<url>[-\w]+)', 'django.contrib.syndication.views.feed',
     {'feed_dict': feeds}),

    (r'^community/photos/', include('stockphoto.urls')),
)

if settings.serve_media:
    # Debug only - http://www.djangoproject.com/documentation/static_files/
    # explains why we shouldn't serve media from django in a release server.
    #              
    # For some reason I haven't yet discovered, the media/ URL seems to be
    # reserved for media used by django's admin module, so we use site-media
    urlpatterns += patterns(
        'django.views.static',

        (r'^site-media/(?P<path>.*)$', 'serve', {'document_root': 'media/'}),
        (r'^var/sphene/(?P<path>.*)$', 'serve', {'document_root':
                                                 'media/var/sphene/'}),
        # Only for development
        (r'^static/sphene/(.*)$', 'serve', {'document_root': settings.ROOT_PATH + '/communitytools/static/sphene' }),
        )

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
    (r'^admin/conference/(?P<conference_name>.*)/schedule$', 'views.schedule_admin'),
    )

defaultdict = { 'groupName': 'boostcon' }

urlpatterns += patterns('',
    # redirect so that the BoostCon link, which surely appears all over the
    # wiki, will just lead back to the home page.
    (r'^community/wiki/show/BoostCon/?$',
     'django.views.generic.simple.redirect_to', {'url': r'/'}),

    (r'^community/forums/', include('sphene.sphboard.urls'), defaultdict),
    (r'^community/wiki/', include('sphene.sphwiki.urls'), defaultdict),
)

urlpatterns += patterns('boost_consulting',
                        
    (r'^accounts/login_or_create/?$', 'accounts.views.register_or_login', {'login':False}),
    (r'^accounts/login/?$', 'accounts.views.register_or_login', {'login':True}),
    (r'^accounts/create/?$', 'accounts.views.register_or_login', {'login':False,
                                                                  'groupName':'boostcon'}),
    (r'^accounts/logout/?$', 'accounts.views.logout'),
    (r'^accounts/create/(?P<hashcode>[a-zA-Z/\+0-9=]+)/$',
     'accounts.views.register_hash', defaultdict),
                        )




def add_trailing_slash(url_prefix):
    return (
        '^' + url_prefix + '(?P<base>(/[^/]+)*)$',
        'simple.redirect_to',
        {'url': '/' + url_prefix + '%(base)s/'},
        )

urlpatterns += patterns('django.views.generic',
# Enable this if you want a special homepage layout.                        
#    (r'^$', 'simple.direct_to_template', {'template': 'homepage.html'}),

                        
    # admin, stockphoto, and Sphene all use a trailing-slash URL scheme, so we need to
    # make sure they always have one.                    
    add_trailing_slash('admin'),
    add_trailing_slash('community/photos'),
    add_trailing_slash('community/wiki'),
    add_trailing_slash('community/forums'),

                        
    (r'^registration-(?P<status>complete|canceled)$', 'simple.direct_to_template', {'template': 'order-status.html'}),

    (r'^(?P<base>.*)/$', 'simple.redirect_to', {'url': r'/%(base)s'}),
                        
    (r'^$', 'simple.redirect_to', {'url': r'/home'}),
    (r'^program/schedule$', 'simple.redirect_to', {'url': r'/program#schedule'}),
                        
    # keep the old redirects from about/shops in case people have linked there.
    (r'^(?:about|community)/shops/eu$', 'simple.redirect_to', {'url': r'http://boostcon.spreadshirt.net'}),
    (r'^(?:about|community)/shops/usa$', 'simple.redirect_to', {'url': r'http://boostcon.spreadshirt.com'}),
)


urlpatterns += patterns(
    'boost_consulting',

    # Uncomment these to enable ecommerce
    (r'^register/(?P<slug>[-\w]+)$', 'ecommerce.views.step1'),
    (r'^checkout-1$', 'ecommerce.views.step1'),
    (r'^checkout-2$', 'ecommerce.views.step2'),

    (r'^registration-(?P<status>complete|canceled)/(?P<hashcode>[a-zA-Z0-9=]+)$',
     'ecommerce.views.order_complete'),
                        

    (r'(.*)$', 'pages.views.page'),
    )

