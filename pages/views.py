from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from models import *

def page(request, url):
    """This is basically the same thing as contrib/flatpages."""

    # Normalize URL to the format used in the database.
    if not url.startswith('/'):
        url = '/' + url

    page = get_page(url)

    if not page:
        raise Http404

    if page.template_name:
        t = loader.select_template((page.template_name, 'pages/default.html'))
    else:
        t = loader.get_template('pages/default.html')

    breadcrumbs = []
    current = page

    while current.parent():
        current = current.parent()
        breadcrumbs.append(current)

    breadcrumbs.reverse()

    c = RequestContext(request, {
        'page': page,
        'body': page.content,
        'breadcrumbs': breadcrumbs
    })

    return HttpResponse(t.render(c))


