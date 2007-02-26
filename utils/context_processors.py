# http://www.b-list.org/weblog/2006/06/14/django-tips-template-context-processors
def media_url(request): 
    from boost_consulting import settings 
    return { 'media_url': settings.MEDIA_URL }
    
