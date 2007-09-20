import turbogears
from turbogears import controllers

from textile import textile as textile_render
from markdown import Markdown as markdown_render
from docutils.core import publish_string as reST_render

from docutils import core
from docutils.writers.html4css1 import Writer,HTMLTranslator

class NoHeaderHTMLTranslator(HTMLTranslator):
    def astext(self):
        return ''.join(self.body)


_w = Writer()
_w.translator_class = NoHeaderHTMLTranslator


class Root(controllers.Root):
    @turbogears.expose()
    def index(self):
        return "available engines: textile, markdown, reST"

    @turbogears.expose()
    def textile(self,text=u"",validate=u"1",sanitize=u"1"):
        sanitize = (False,True)[int(sanitize == "1")]
        validate = (False,True)[int(validate == "1")]
        return textile_render(text.decode('utf8').encode('ascii','xmlcharrefreplace'),
                   validate=validate,sanitize=sanitize)

    @turbogears.expose()
    def markdown(self,text=u"",validate=u"1",sanitize=u"1"):
        return markdown_render(text).toString()

    @turbogears.expose()
    def reST(self,text=u"",validate=u"1",sanitize="1"):
        return reST_render(text, writer=_w)
    
        
