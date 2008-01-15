# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from xml.dom import minidom
from copy import copy

class metatag(object.__class__):
    def __getattr__(self, name):
        return tag(name)
    
class tag(object):
    __metaclass__ = metatag
    
    def __init__(self, name):
        self._name = name
        self._attributes = {}
        self._children = []

    def _copy(self):
        x = tag(self._name)
        x._children = copy(self._children)
        x._attributes = copy(self._attributes)
        return x
    
    def __call__(self, **attributes):
        result = self._copy()
        result._attributes.update(attributes)
        return result
    
    def __getitem__(self, children):
        result = self._copy()
        result._children += isinstance(children,tuple) and children or (children,)
        return result

    def __str__(self):
        return '<%s%s>%s</%s>' % (
            self._name
            , ''.join([' %s=%s' % kv for kv in self._attributes.items()])
            , ''.join([str(c) for c in self._children])
            , self._name)
        
    def _xml(self, d):
        e = d.createElement(self._name)
        for c in self._children:
            if isinstance(c, tag):
                cc = c._xml(d)
            else:
                cc = e.ownerDocument.createTextNode(str(c))
            e.appendChild(cc)
        for k,v in self._attributes.items():
            e.setAttribute(k,v)
        return e
    
def xml_document(t):
    d = minidom.Document()
    d.documentElement = t._xml(d)
    return d

if __name__ == '__main__':
    
    _ = tag
    print _.RequestHeader[
                _.AccountNumber[ 33 ]
              , _.MeterNumber[ 44 ]
              , _.CarrierCode[ 'FDXG' ]
            ]
    
    print xml_document(
            _.RequestHeader[
                _.AccountNumber[ 33 ]
              , _.MeterNumber[ 44 ]
              , _.CarrierCode[ 'FDXG' ]
            ])
