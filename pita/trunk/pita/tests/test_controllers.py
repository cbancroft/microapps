from turbogears import testutil
from pita.controllers import Root
from pita.model import Service,Item
import cherrypy,unittest

from turbogears import database
database.set_db_uri("sqlite:///:memory:")
cherrypy.config.update({'global' : {'server.environment' : 'development', 'server.logToScreen' : False,
                                    'logDebugInfoFilter.on' : False}})

def createTables():
    Service.createTable(ifNotExists=True)
    Item.createTable(ifNotExists=True)

def dropTables():
    Item.dropTable(ifExists=True)
    Service.dropTable(ifExists=True)

class PitaTest(unittest.TestCase):
    def setUp(self):
        createTables()
        self.service = Service(name="testservice")
        cherrypy.root = Root()
        

    def tearDown(self):
        dropTables()

def GET(url,headers={}):
    testutil.createRequest(url,headers=headers)
    return cherrypy.response.body[0]


import cStringIO as StringIO
def POST(url,data=""):
    rfile = StringIO.StringIO(data)
    testutil.createRequest(url,method="POST",rfile=rfile)
    return cherrypy.response

def DELETE(url):
    testutil.createRequest(url,method="DELETE")
    return cherrypy.response

class TestRoot(PitaTest):
    def test_basics(self):
        "basic test"
        testutil.createRequest("/")
        body = cherrypy.response.body[0]
        assert "testservice" in body

class TestService(PitaTest):
    def test_add(self):
        POST("/service/newservice/")
        r = GET("/")
        assert "newservice" in r

    def test_delete(self):
        POST("/service/newservice/")
        r = GET("/")
        assert "newservice" in r
        DELETE("/service/newservice/")
        r = GET("/")
        assert "newservice" not in r

class TestItem(PitaTest):
    def test_add(self):
        POST("/service/testservice/item/foo/","value=some data")
        r = GET("/service/testservice/")
        assert "foo" in r
        r = GET("/service/testservice/item/foo/")
        assert "some data" == r

    def test_delete(self):
        POST("/service/testservice/item/foo/","value=some data")
        r = GET("/service/testservice/")
        assert "foo" in r
        DELETE("/service/testservice/item/foo/")
        r = GET("/service/testservice/")
        assert "foo" not in r

    def test_unicode(self):
        POST("/service/testservice/item/unicode_test/","value=%E5%AD%90%E4%BE%9B")
        r = GET("/service/testservice/item/unicode_test/")
        assert u"\u5b50\u4f9b" in r

