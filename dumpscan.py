import xml.sax
import gzip
import codecs

from collections import defaultdict, deque

import saxhandlers
from saxhandlers import SaxHandlerStack
from saxhandlers import IgnoreHandler
from saxhandlers import PrintElementStackHandler

class Revision (object):
    def __init__(self):
        self.page = None
        self.id = None
        self.timestamp = None
        self.contributor = None
        self.comment = None
        self.text = None
        self.sha1 = None
        self.model = None
        self.format = None
        self.parentid = None

class Page (object):
    def __init__(self):
        self.title = None
        self.ns = None
        self.id = None

class User (object):
    def __init__(self):
        self.username = None
        self.id = None

class RevisionTagHandler (SaxHandlerStack):
    def __init__(self, name, parent, attrs):
        SaxHandlerStack.__init__(self, name, parent)
        self.revision = Revision()
        self.revision.page = self.parent.page
        self.handler_factories = {
            "comment": self.value_handler(),
            "id": self.value_handler(int),
            "sha1": self.value_handler(),
            "model": self.value_handler(),
            "format": self.value_handler(),
            "parentid": self.value_handler(int),
            "minor": IgnoreHandler,
            "text": IgnoreHandler,
            "contributor": IgnoreHandler,
            "timestamp": IgnoreHandler
        }

    def value_handler(self, *args, **kwargs):
        make = saxhandlers.create_value_element_handler
        return make(self.revision, *args, **kwargs)

    def stop(self):
        self.callback(self.revision)

class PageTagHandler (SaxHandlerStack):
    def __init__(self, name, parent, attrs):
        SaxHandlerStack.__init__(self, name, parent)
        self.page = Page()
        self.handler_factories = {
            "revision": RevisionTagHandler,
            "title": self.value_handler(),
            "ns": self.value_handler(int),
            "id": self.value_handler(int),
        }

    def value_handler(self, *args, **kwargs):
        make = saxhandlers.create_value_element_handler
        return make(self.page, *args, **kwargs)

class MediawikiTagHandler (SaxHandlerStack):
    handler_factories = {
        "siteinfo": IgnoreHandler,
        "page": PageTagHandler,
    }

    def __init__(self, name, parent, attrs):
        SaxHandlerStack.__init__(self, name, parent)

class DocumentHandler (SaxHandlerStack):
    handler_factories = {
        "mediawiki": MediawikiTagHandler,
    }

    def __init__(self, name="(root)"):
        SaxHandlerStack.__init__(self, name, None)
        self.callback = None

def parse_revisions(filename):
    parser = xml.sax.make_parser(["xml.sax.IncrementalParser"])
    ready = deque()
    def deliver(x):
        ready.append(x)
    handler = DocumentHandler()
    handler.callback = deliver
    parser.setContentHandler(handler)
    with gzip.GzipFile(filename, "r") as raw_f:
        f = codecs.EncodedFile(raw_f, "utf8")
        for line in f:
            parser.feed(line)
            while ready:
                yield ready.popleft()
        parser.close()
        while ready:
            yield ready.popleft()

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    for revision in parse_revisions(filename):
        args = revision.id, revision.page.title
        print "revision #{} of page '{}'".format(*args)
