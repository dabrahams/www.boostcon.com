from docutils import core, io

# Attempt to account for relative path differences to stylesheets and
# templates on installed system.  ***This is a HACK***.
#
# Because the paths of the cwd and the default stylesheet and template.txt on
# our live server have something in common, Python calculates a relative path
# between them (see html4css1.Writer's class-level initializations).  It's not
# clear why this should cause those stylesheets not to be found, but in fact it
# does.  Perhaps the cwd gets changed later, I don't know.  On my development
# system we have no path elements in common and thus we end up with an absolute
# path, and the stylesheet and template are always found.
import os
_save_cwd = os.getcwd()
os.chdir('/')
try:
    from docutils.writers import html4css1
finally:
    os.chdir(_save_cwd)
    
from docutils import nodes
from boost_consulting.settings import MEDIA_URL
from docutils.transforms import Transform
import re

class LinkTitlesTransform(Transform):
    default_priority = 461

    title_re = re.compile(r'^(.*)\(([^)]+)\)$')

    def apply(self):
        doc = self.document
        for ref in doc.traverse(nodes.reference):
            open = ref.next_node(descend=0, siblings=1)
            if not open: continue
            if not isinstance(open, nodes.Text) or \
                    open.astext().strip() != '(': 
                continue
            title = open.next_node(descend=0, siblings=1)
            if not title: continue
            if not isinstance(title, nodes.title_reference):
                continue
            close = title.next_node(descend=0, siblings=1)
            if not close: continue
            if not isinstance(close, nodes.Text) or \
                    close.astext()[0] != ')': 
                continue

            ref['title'] = title.astext()
            ref.parent.remove(open)
            ref.parent.remove(title)
            ref.parent.replace(close, nodes.Text(close.data[1:], close.data[1:]))

class DocInfoExtractWriter(html4css1.Writer):
    """HTML writer that extracts docinfo fields. docinfo_fields 
       determines which fields are of interest."""

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = DocInfoExtractTranslator

    def get_transforms(self):
        return html4css1.Writer.get_transforms(self) + [LinkTitlesTransform]

    def translate(self):
        self.result = {}
        for field in self.docinfo_fields:
            self.result[field.lower()] = None

        # Copied from html-writer. We need to get visitor before translation.
        self.visitor = visitor = self.translator_class(self.document)
        visitor.docinfo_fields = self.docinfo_fields
        self.document.walkabout(visitor)
        for attr in self.visitor_attributes:
            setattr(self, attr, getattr(visitor, attr))
        self.output = self.apply_template()
        self.result.update(visitor.result)

    docinfo_fields = ()

class DocInfoExtractTranslator(html4css1.HTMLTranslator):
    def __init__(self, document):
        html4css1.HTMLTranslator.__init__(self, document)
        self.result = {}
        self.in_interested_field = False

    def starttag(self, node, tagname, suffix='\n', empty=0, **attributes):
        for a in 'href', 'src':
            href = attributes.get(a)
            if href and href.startswith('/site-media/'):
                attributes[a] = href.replace('/site-media', MEDIA_URL, 1)
        return html4css1.HTMLTranslator.starttag(self, node, tagname, suffix, empty, **attributes)
    
    def visit_field(self, node):
        if self.in_docinfo:
            name = node[0].astext()
            if name.lower() in self.docinfo_fields:
                self.field_start = len(self.body)
                self.in_interested_field = True
                return
        return html4css1.HTMLTranslator.visit_field(self, node)

    def depart_field(self, node):
        if self.in_docinfo:
            name = node[0].astext()
            if name.lower() in self.docinfo_fields:
                self.result[name.lower()] = ''.join(self.body[self.field_start:])
                del self.body[self.field_start:]
                self.in_interested_field = False
                return
        return html4css1.HTMLTranslator.depart_field(self, node)

    def visit_field_name(self, node):
        if self.in_interested_field:
            raise nodes.SkipNode
        return html4css1.HTMLTranslator.visit_field_name(self, node)

    def visit_field_body(self, node):
        if self.in_interested_field:
            raise nodes.SkipDeparture
        return html4css1.HTMLTranslator.visit_field_body(self, node)

    def visit_date(self, node):
        if self.in_docinfo:
            if 'date' in self.docinfo_fields:
                self.result['date'] = node[0].astext()
                raise nodes.SkipNode
        return html4css1.HTMLTranslator.visit_date(self, node)

    def visit_author(self, node):
        if self.in_docinfo:
            if 'author' in self.docinfo_fields:
                self.result['author'] = node[0].astext()
                raise nodes.SkipNode
        return html4css1.HTMLTranslator.visit_author(self, node)

    # adds href title
    def visit_reference(self, node):
        if node.has_key('refuri'):
            href = node['refuri']
            if ( self.settings.cloak_email_addresses
                 and href.startswith('mailto:')):
                href = self.cloak_mailto(href)
                self.in_mailto = 1
        else:
            assert node.has_key('refid'), \
                   'References must have "refuri" or "refid" attribute.'
            href = '#' + node['refid']
        atts = {'href': href, 'class': 'reference'}
        if not isinstance(node.parent, nodes.TextElement):
            assert len(node) == 1 and isinstance(node[0], nodes.image)
            atts['class'] += ' image-reference'
        if node.hasattr('title'):
            atts['title'] = node['title']
        self.body.append(self.starttag(node, 'a', '', **atts))

def get_parts(src, writer, **kw):
    """Converts ReST src to HTML and extracts needed docinfo-fields."""
    overrides = {'input_encoding': 'utf-8',
                 'doctitle_xform': 1,
                 'initial_header_level': 2,
                 'toc_backlinks':'none'
                 }
    overrides.update(kw)

    # Hack. Change to the correct directory for includes to work.
    # os.chdir(os.path.dirname(os.path.dirname(__file__)))

    parts = core.publish_parts(
        source=src, writer=writer, settings_overrides=overrides)
    return (parts, writer.result)

