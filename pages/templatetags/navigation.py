from django import template
from pages.models import *

register = template.Library()

class Home:
    '''A fake page that gets us an initial Home menu'''
    def children(self):
        return []

    def get_absolute_url(self):
        return '/'

    # Not sure why this is needed, but somehow an instance of Home class is
    # getting mixed up with real pages.
    url = '/'
    title = 'Home'
    menu_title = 'Home'
    page_title = 'Home'

class NavigationNode(template.Node):
    def __init__(self, maxdepth=1):
        super(NavigationNode,self).__init__()
        self.maxdepth = maxdepth
        
    def _menu_items(self, root, pages, depth):
        if depth >= self.maxdepth:
            return []

        items = []

        indent = (depth*4+2)*' '
        
        # Check to see if we're at the top level.  We're checking str() here
        # because we seem to be generating too many page objects.
        if len(pages) and str(pages[0].parent()) == str(root):
            items.append(
                indent
                + '<li><a href="%s" class="self">%s Home</a></li>'
                % (root.get_absolute_url(),root.menu_title))

        link_attributes = ' class="drop"'
        
        for i in range(len(pages)):
            p = pages[i]

            next_level = self._menu_items(root, p.children(),depth+1)

            items.append(indent+'<li>')
            
            url = p.get_absolute_url()
            menu_title = p.menu_title

            items.append(
                indent+ (next_level and self.open_parent or self.open_leaf) % locals()
                )
            
            items += next_level
            
            if next_level:
                items.append(indent+ self.close_parent)

            items.append(indent+ '</li>')
            
        if not items:
            return []
        else:
            indent = indent[:-2]
            return [indent+'<ul>'] + items + [indent+'</ul>']

    open_parent = '''<a%(link_attributes)s href="%(url)s">%(menu_title)s<!--[if IE 7]><!--></a><!--<![endif]-->
<!--[if lte IE 6]><table><tr><td><![endif]-->'''
    close_parent = '''<!--[if lte IE 6]></td></tr></table></a><![endif]-->'''
    open_leaf = '''<a href="%(url)s">%(menu_title)s</a>'''

        
    def render(self, ctx):

        result = ['<ul>']
        link_attributes = ''

        # In case there's no representative page for "home," synthesize one
        top_pages = get_pages('/')
        if top_pages[0].menu_title.lower() != 'home':
            top_pages.insert(0, Home())
            
        for top in top_pages:
            children = top.children()
            if children:
                # to create multilevel menus, increase depth 
                menu_items = self._menu_items(
                    top, children, depth=0)
            else:
                menu_items = []

            url = top.get_absolute_url()
            menu_title = top.menu_title
            
            result += ['<li>', self.open_parent % locals()]       \
                      + menu_items                              \
                      + [ self.close_parent, '</li>']

        result += ['</ul>']

        # Unicode error if we don't encode here.  
        return ('\n'.join(result)).encode('utf-8')

def navigation_tree(parser, token):
    try:
        tagname,maxdepth=token.split_contents()
    except:
        maxdepth=1
    else:
        maxdepth = int(maxdepth)
        
    return NavigationNode(maxdepth)

register.tag(navigation_tree)

