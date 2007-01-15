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
    @classmethod
    def _menu_items(self, root, pages, depth):
        if depth == 0:
            return ''

        items = []

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

        return '  <ul>\n%s</ul>\n' % ''.join(items)

    def render(self, ctx):

        result = '<ul>\n'
        first = 'first-'

        for top in [Home()] + get_pages('/'):
            children = top.children()
            if children:
                # increase depth to create multilevel menus
                menu_items = self._menu_items(top, children, depth=1)
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
    return NavigationNode()

register.tag(navigation_tree)

