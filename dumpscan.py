import xml.sax
import gzip

from collections import defaultdict

class UnhandledElement (Exception):
    def __init__(self, message):
        super(UnhandledElement, self).__init__(message)

class SaxHandlerStack (xml.sax.ContentHandler):
    def __init__(self, name, parent=None):
        self.stack = []
        self.default_handler_factory = None
        self.name = name
        self.parent = parent
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = -1

    def startElement(self, name, attrs):
        if self.stack:
            self.stack[-1].startElement(name, attrs)
            return
        try:
            handler_factory = self.handler_factories[name]
        except KeyError:
            if self.default_handler_factory:
                handler_factory = self.default_handler_factory
            else:
                msg = "{} below {}".format(name, self.name)
                raise UnhandledElement(msg)
        handler = handler_factory(name=name, parent=self, attrs=attrs)
        self.stack.append(handler)
        handler.start()

    def start(self):
        pass

    def stop(self):
        pass

    def endElement(self, name):
        if self.stack:
            self.stack[-1].endElement(name)
            return
        self.stop()
        assert self.name == name
        if self.parent:
            me = self.parent.stack.pop(-1)
            assert self is me

class PrintElementTreeHandler (SaxHandlerStack):
    handler_factories = defaultdict(lambda : PrintElementTreeHandler)
    
    def __init__(self, name, parent, attrs):
        SaxHandlerStack.__init__(self, name, parent)

    def start(self):
        print " " * self.depth + self.name

class IgnoreHandler (SaxHandlerStack):
    handler_factories = defaultdict(lambda : IgnoreHandler)

    def __init__(self, name, parent, attrs):
        SaxHandlerStack.__init__(self, name, parent)

class MediawikiHandler (SaxHandlerStack):
    handler_factories = {
        "siteinfo": IgnoreHandler,
        "page": PrintElementTreeHandler,
    }

    def __init__(self, name, parent, attrs):
        SaxHandlerStack.__init__(self, name, parent)

    def start(self):
        print self.name

class DocumentHandler (SaxHandlerStack):
    handler_factories = {
        "mediawiki": MediawikiHandler,
    }

    def __init__(self, name="(root)"):
        SaxHandlerStack.__init__(self, name, None)

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    with gzip.GzipFile(filename, "r") as f:
        xml.sax.parse(f, DocumentHandler())
