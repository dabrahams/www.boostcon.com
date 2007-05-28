from django.conf.urls.defaults import *
from django.conf import settings

from models import Gallery, Photo, ADMIN_URL, STOCKPHOTO_URL

info_dict = { 'extra_context': { 'admin_url': ADMIN_URL,
                                 'stockphoto_url': STOCKPHOTO_URL} }

urlpatterns = patterns('django.views.generic.list_detail',
	(r'^$', 'object_list',
		dict(info_dict, queryset=Gallery.objects.all(),
		     paginate_by= 10, allow_empty= True)),
	(r'^(?P<object_id>\d+)/$', 'object_detail',
		dict(info_dict, queryset=Gallery.objects.all())),
	(r'^detail/(?P<object_id>\d+)/$', 'object_detail',
		dict(info_dict, queryset=Photo.objects.all())),
)
urlpatterns += patterns('stockphoto.views',
	(r'^import/(\d+)/$', 'import_photos'),
    (r'^export/(\d+)/$', 'export'),
)
