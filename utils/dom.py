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
        for k,v in attributes.items():
            if k.startswith('_'):
                k = k[1:]
            self._attributes[k] = v
        return self

    def __ilshift__(self, x):
        self._flatten_append(self._children,x)
        return self
        
    @staticmethod
    def _flatten_append(l, x):
        if isinstance(x,list) or isinstance(x,tuple):
            for y in x:
                tag._flatten_append(l, y)
        else:
            l.append(x)
            
    def __getitem__(self, new_children):
        tag._flatten_append(self._children, new_children)
        return self

    def __str__(self):
        return u'<%s%s>%s</%s>' % (
            self._name
            , u''.join([u' %s="%s"' % kv for kv in self._attributes.items()])
            , u''.join([str(c) for c in self._children])
            , self._name)

    def __repr__(self):
        return self.__class__.__name__ + ': ' + str(self)
    
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
              , (_.MeterNumber[ 44 ]
              , _.CarrierCode[ 'FDXG' ])
            ]
    
    print xml_document(
            _.RequestHeader[
                _.AccountNumber[ 33 ]
              , _.MeterNumber[ 44 ]
              , _.CarrierCode[ 'FDXG' ]
            ])
