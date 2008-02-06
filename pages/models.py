from utils.cache import eternal_cache as cache
from boost_consulting.utils.docinfo_writer import *
import os
import stat
import re

class PageWriter(DocInfoExtractWriter):
    docinfo_fields = ('template-name', 'order', 'keywords', 'menu-title', 'page-title')

def _normalize_url(url):
    """Prepends / to all urls, and converts \ into /"""
    url = url.replace('\\', '/')
    if url == '':
        return '/'
    if url[0] != '/':
        url = '/' + url
    return url

generators = []

def _load_page(path, url):
    """Load data for a single page from rst-file in 'path'."""
    return build_page(
        url = url,
        *get_parts(
            open(path).read(),
            PageWriter(),
            initial_header_level = 3)
        )

def build_page(parts, data, url):
    """Generate an instance of the page model from the given parts and data."""

    result = Page()
    result.url = url
    
    result.meta = parts['meta'].encode('utf-8')
    
    # Extract basic docinfo fields
    order = data['order'] or 0
    result.order = int(order)
    result.template_name = data['template-name'] or ''

    # Extract keywords
    if data['keywords']:
        self.keywords = map(lambda k: k.split(), data['keywords'].split(','))
    else:
        result.keywords = []

    # Extract title and initialize associated defaults
    if 'title' in parts:
        result.title = parts['title'].encode('utf-8')
    result.menu_title = result.page_title = result.title

    # Handle menu title and the HTML <title>...</title> overrides
    if data['menu-title']:
        result.menu_title = data['menu-title'].encode('utf-8')
    if data['page-title']:
        result.page_title = data['page-title'].encode('utf-8')

    # Extract the body
    result.content = parts['fragment'].encode('utf-8')

    return result

content_root = os.path.join(os.path.dirname(__file__), '../content/pages')

def get_pages(root_url):
    """Get all pages rooted at 'root_url'.
        
       If the modification time of the ReST file on-disk doesn't match the
       cached record's timestamp (recorded in the cache), updates the
       cached record. Returns a list of pages, or [] if no pages exists."""

    root_url = _normalize_url(root_url)
    path = os.path.join(content_root, root_url[1:])
    pages = cache.get('pages_for_' + root_url)

    try:
        mod_time = os.stat(path)[stat.ST_MTIME]
    except:
        return []

    if pages and mod_time == cache.get('mod_time_for_' + path):
        return pages
    
    try:
        files = os.listdir(path)
    except:
        files = []

    pages = []

    timeout = None
    for pattern,g in generators:
        if re.match(pattern, root_url[1:]):
            pages += g(root_url)
            timeout = 2*60
            break

    # Load all pages from filesystem.
    for f in files:
        name,ext = os.path.splitext(f)

        # skip over hidden and non-ReST files
        if f.startswith('.') or ext != '.rst':
            continue

        url = _normalize_url(os.path.join(root_url,name))
        page = _load_page(os.path.join(path, f), url);
        pages.append(page)

    pages.sort(lambda x,y: cmp((x.order,x.title), (y.order,y.title)))
    pages = tuple(pages) # make it immutable for the cache
    
    # Setup prev/next links for all siblings.
    prev = None
    for p in pages:
        if prev: prev.next = p
        p.prev = prev
        prev = p
        # the template may access the DB, so better not persist too long        
        if p.template_name:
            timeout = 2*60

    cache.set('mod_time_for_' + path, mod_time, timeout=timeout)
    cache.set('pages_for_' + root_url, pages, timeout=timeout)

    return pages

def get_page(url):
    """Fetch a single Page instance corresponding to 'url'. This loads
       all sibling pages and ensures next/prev links are setup."""
    url = _normalize_url(url)
    parent = os.path.dirname(url)
    siblings = get_pages(parent)
    for p in siblings:
        if p.url == url:
            return p
    return None

class Page(object):

    def __init__(self):
        self.url = ''
        """The URL at which this page can be found."""

        self.title = ''
        """The page title with HTML markup."""

        self.menu_title = ''
        """The page title used in menus referring to this page. Raw text."""

        self.page_title = ''
        """The page title for display in browser titlebar."""

        self.content = ''
        """HTML page content."""

        self.template_name = ''
        """The name of the Django template that will be used to render this page."""

        self.next = None
        """A 'link' to the previous sibling Page."""

        self.prev = None
        """A 'link' to the next sibling Page."""

        self.order = 0
        """The sort order of this page relative to its siblings."""

        self.keywords = []
        """Each page has a list of associated keywords used in meta keyword tags."""

    @property
    def first_child(self):
        c = self.children()
        return c and c[0] or None
    
    def __str__(self):
        return self.url

    def __repr__(self):
        return self.url

    def get_absolute_url(self):
        return self.url

    def children(self):
        c = get_pages(self.url)
        return c

    def parent(self):
        dir = os.path.dirname(self.url)
        if dir == content_root:
            return None
        else:
            return get_page(dir)

