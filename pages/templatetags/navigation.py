from django import template
from pages.models import *

register = template.Library()

class Home:
    '''A fake page that gets us an initial Home menu'''
    def children(self):
        return []

    def get_absolute_url(self):
        return '/'

    title = 'Home'
    menu_title = 'Home'
    page_title = 'Home'

class NavigationNode(template.Node):
    def __init__(self, maxdepth=1):
        super(NavigationNode,self).__init__()
        self.maxdepth = maxdepth
        
    @classmethod
    def _menu_items(self, root, pages, depth):
        if depth == 0:
            return ''

        items = []

        # Check to see if we're at the top level.  We're checking str() here
        # because we seem to be generating too many page objects.
        if len(pages) and str(pages[0].parent()) == str(root):
            items.append(
                '    <li class="self"><a href="%s">%s Home</a></li>'
                % (
                    root.get_absolute_url(),
                    root.menu_title))

        for i in range(len(pages)):
            p = pages[i]
            c = depth > 1 and p.children()

            classes = []

            if c:
                classes.append('submenu')
            
            if i == len(pages) - 1:
                classes.append('last')

            if depth > 1:
                next_level = self._menu_items(root, p.children(),depth-1)
            else:
                next_level = ''

            items.append(
                '    <li %s><a href="%s">%s</a>\n%s</li>'
                % (
                        len(classes) and ('class="' + ' '.join(classes) + '"') or '',
                        p.get_absolute_url(),
                        p.menu_title,
                        next_level))

        if not items:
            return ''
        else:
            return '  <ul>\n%s</ul>\n' % ''.join(items)

    def render(self, ctx):

        result = '<ul id="menu">\n'
        first = 'first-'

        # In case there's no representative page for "home," synthesize one
        top_pages = get_pages('/')
        if top_pages[0].menu_title.lower() != 'home':
            top_pages.insert(0, Home())
            
        for top in top_pages:
            children = top.children()
            if children:
                # increase depth to create multilevel menus
                menu_items = self._menu_items(top, children, depth=self.maxdepth)
                parent = ' class="parent"'
            else:
                menu_items = ''
                parent = ''

            result += '<li%s>' % parent

            result += '<a class="top-menu" href="%s">%s</a>\n' % (top.get_absolute_url(), top.menu_title)
            result += menu_items
            result += '</li>'

        # Unicode error if we don't encode here.  
        return (result + '</ul>\n').encode('utf-8')

def navigation_tree(parser, token):
    try:
        tagname,maxdepth=token.split_contents()
    except:
        maxdepth=1
    else:
        maxdepth = int(maxdepth)
        
    return NavigationNode(maxdepth)

register.tag(navigation_tree)

