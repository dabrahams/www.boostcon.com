from docutils import core, io
from docutils.writers import html4css1
from docutils import nodes

class DocInfoExtractWriter(html4css1.Writer):
    """HTML writer that extracts docinfo fields. docinfo_fields 
       determines which fields are of interest."""

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = DocInfoExtractTranslator

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

def get_parts(src, writer, **kw):
    """Converts ReST src to HTML and extracts needed docinfo-fields."""
    overrides = {'input_encoding': 'unicode',
                 'doctitle_xform': 1,
                 'initial_header_level': 1}
    overrides.update(kw)
    parts = core.publish_parts(
        source=src, writer=writer, settings_overrides=overrides)
    return (parts, writer.result)

