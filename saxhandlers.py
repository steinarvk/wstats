import xml.sax

from collections import defaultdict

class UnhandledElement (Exception):
    def __init__(self, message):
        super(UnhandledElement, self).__init__(message)

class SaxHandlerStack (xml.sax.ContentHandler):
    def __init__(self, name, parent=None, callback=None):
        self.child = None
        self.name = name
        self.parent = parent
        self.callback = callback
        if self.parent:
            self.depth = self.parent.depth + 1
            if not self.callback:
                self.callback = self.parent.callback
        else:
            self.depth = -1

    def startElement(self, name, attrs):
        if self.child:
            self.child.startElement(name, attrs)
            return
        try:
            handler_factory = self.handler_factories[name]
        except KeyError:
            try:
                handler_factory = self.default_handler_factory
            except AttributeError:
                handler_factory = None
        if not handler_factory:
            msg = "{} below {}".format(name, self.name)
            raise UnhandledElement(msg)
        handler = handler_factory(name=name, parent=self, attrs=attrs)
        assert not self.child
        self.child = handler
        handler.start()

    def start(self):
        pass

    def stop(self):
        pass

    def endElement(self, name):
        if self.child:
            self.child.endElement(name)
            return
        self.stop()
        assert self.name == name
        if self.parent:
            assert self.parent.child is self
            self.parent.child = None

    def characters(self, content):
        if self.child:
            self.child.characters(content)

class PrintElementTreeHandler (SaxHandlerStack):
    handler_factories = defaultdict(lambda : PrintElementTreeHandler)
    
    def __init__(self, name, parent, attrs):
        SaxHandlerStack.__init__(self, name, parent)

    def start(self):
        print " " * self.depth + self.name

class PrintElementStackHandler (SaxHandlerStack):
    handler_factories = defaultdict(lambda : PrintElementStackHandler)

    def __init__(self, name, parent, attrs):
        SaxHandlerStack.__init__(self, name, parent)

    def start(self):
        nodes = [self]
        while nodes[-1].parent:
            nodes.append(nodes[-1].parent)
        print ".".join(reversed([node.name for node in nodes]))

class IgnoreHandler (SaxHandlerStack):
    handler_factories = defaultdict(lambda : IgnoreHandler)

    def __init__(self, name, parent, attrs):
        SaxHandlerStack.__init__(self, name, parent)

class TextHandler (SaxHandlerStack):
    handler_factories = {}

    def __init__(self, name, parent):
        SaxHandlerStack.__init__(self, name, parent)
        self.content = []

    def characters(self, data):
        self.content.append(data)

    def text(self):
        return "".join(self.content).strip()

class ValueElementHandler (TextHandler):
    handler_factories = {}

    def __init__(self, name, parent, target, parser, force_name):
        TextHandler.__init__(self, name, parent)
        self.target = target
        self.parser = parser
        self.attrname = force_name or self.name

    def stop(self):
        value = self.parser(self.text())
        setattr(self.target, self.attrname, value)

def identity(s):
    return s

def create_value_element_handler(target, parser=identity, force_name=None):
    def construct(name, parent, attrs):
        rv = ValueElementHandler(name, parent, target, parser, force_name)
        return rv
    return construct

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    handler = PrintElementTreeHandler("(root)", None, None)
    xml.sax.parse(filename, handler)
