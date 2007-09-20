from turbogears.tests import util
from gild.controllers import Root
import cherrypy,unittest,urllib
import cStringIO as StringIO

cherrypy.config.update({'global' : {'server.environment' : 'development', 'server.logToScreen' : False,
                                    'logDebugInfoFilter.on' : False}})


def GET(url,headers={}):
    util.createRequest(url,headers=headers)
    return cherrypy.response.body[0]

def POST(url,data={}):
    rfile = StringIO.StringIO(urllib.urlencode(data))
    util.createRequest(url,method="POST",rfile=rfile)
    return cherrypy.response.body[0]

def strip_whitespace(text=""):
    text = text.replace(' ','')
    text = text.replace('\n','')
    text = text.replace('\r','')
    return text

class GildTest(unittest.TestCase):
    def setUp(self):
        cherrypy.root = Root()

class TestRoot(GildTest):
    def test_basics(self):
        "basic test"
        body = GET("/")
        assert "textile" in body
        assert "markdown" in body
        assert "reST" in body

    def test_textile(self):
        "test the textile engine"
        r = POST("/textile",{'text' : 'foo'})
        assert r == "<p>foo</p>"

    def test_markdow(self):
        "test the markdown engine"
        r = POST("/markdown",{'text' : 'foo'})
        assert strip_whitespace(r) == "<p>foo</p>"

    def test_reST(self):
        "test the reST engine"
        r = POST("/reST",{'text' : 'foo'})
        assert strip_whitespace(r) == "<p>foo</p>"

    def test_unicode(self):
        "make sure high order unicode is supported properly"
        r = POST("/textile",{'text' : u"foo \u2012".encode('utf8')})
        # this isn't quite right. it *should* return a utf8 string instead
        # of ascii with XML numerical char refs, but this is a known bug in
        # pytextile. someday i'll fix it if no one else does first. 
        assert r == "<p>foo &#8210;</p>"

        r = POST("/markdown",{'text' : u"foo \u2012".encode('utf8')})
        assert strip_whitespace(r).decode('utf8') == strip_whitespace(u"<p>foo \u2012</p>")

        r = POST("/reST",{'text' : u"foo \u2012".encode('utf8')})
        assert strip_whitespace(r).decode('utf8') == strip_whitespace(u"<p>foo \u2012</p>")

    def test_sanitize(self):
        "tests the sanitization functionality"

        r = POST("/textile",{'text' : "<script>alert('this is nasty')</script>"})
        assert r == ""

        # test turning it off. (if you're trusting the input)

        r = POST("/textile",{'text' : "<script>alert('this is nasty')</script>",
                             'sanitize' : "0", 'validate' : '0'})
        assert r == "<script>alert('this is nasty')</script>"

        # currently no way to turn off sanitizing for markdown (that i know of)

        # reST escapes dangerous stuff instead of removing it, which is fine
        r = POST("/reST",{'text' : "<script>alert('this is nasty')</script>"})
        assert strip_whitespace(r) == strip_whitespace("<p>&lt;script&gt;alert('this is nasty')&lt;/script&gt;</p>")
        # also no way of turning off sanitizing for reST
    

