import turbogears.testutil as util
from nqdq.controllers import build_controllers
from nqdq.model import Service,Q,Item
import cherrypy,unittest
from simplejson import loads as json_to_py

from turbogears import database
database.set_db_uri("sqlite:///:memory:")
cherrypy.config.update({'global' : {'server.environment' : 'development', 'server.logToScreen' : False,
                                    'logDebugInfoFilter.on' : False}})

def GET(url,headers={}):
    util.createRequest(url,headers=headers)
    return cherrypy.response.body[0]


import cStringIO as StringIO
def POST(url,data=""):
    rfile = StringIO.StringIO(data)
    util.createRequest(url,method="POST",rfile=rfile)
    return cherrypy.response

def DELETE(url):
    util.createRequest(url,method="DELETE")
    return cherrypy.response

def createTables():
    Service.createTable(ifNotExists=True)
    Q.createTable(ifNotExists=True)
    Item.createTable(ifNotExists=True)

def dropTables():
    Item.dropTable(ifExists=True)
    Q.dropTable(ifExists=True)
    Service.dropTable(ifExists=True)

class NQDQTest(unittest.TestCase):
    def setUp(self):
        createTables()
        self.service = Service(name="testservice")
        cherrypy.root = build_controllers()

    def tearDown(self):
        dropTables()

class TestService(NQDQTest):
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

class TestQ(NQDQTest):
    def test_add(self):
        POST("/service/testservice/q/testq/")
        r = GET("/service/testservice/")
        assert "testq" in r

    def test_delete(self):
        POST("/service/testservice/q/testq/")
        r = GET("/service/testservice/")
        assert "testq" in r
        r = DELETE("/service/testservice/q/testq/")
        r = GET("/service/testservice/")
        assert "testq" not in r

    def test_push(self):
        POST("/service/testservice/q/testq/push","value=foo")
        r = GET("/service/testservice/q/testq/")
        assert "foo" in r
        POST("/service/testservice/q/testq/push","value=bar")
        r = GET("/service/testservice/q/testq/")
        assert json_to_py(r) == ["foo","bar"]

    def test_unshift(self):
        POST("/service/testservice/q/testq/unshift","value=foo")
        r = GET("/service/testservice/q/testq/")
        assert "foo" in r
        POST("/service/testservice/q/testq/unshift","value=bar")
        r = GET("/service/testservice/q/testq/")
        assert json_to_py(r) == ["bar","foo"]

    def test_pop(self):
        POST("/service/testservice/q/testq/push","value=foo")
        r = POST("/service/testservice/q/testq/pop")
        assert "foo" in r.body[0]
        r = GET("/service/testservice/q/testq/")
        assert "foo" not in r
        POST("/service/testservice/q/testq/push","value=foo")        
        POST("/service/testservice/q/testq/push","value=bar")
        r = POST("/service/testservice/q/testq/pop")
        assert "bar" in r.body[0]
        r = GET("/service/testservice/q/testq/")
        assert json_to_py(r) == ["foo"]

    def test_shift(self):
        POST("/service/testservice/q/testq/push","value=foo")
        r = POST("/service/testservice/q/testq/shift")
        assert "foo" in r.body[0]
        r = GET("/service/testservice/q/testq/")
        assert "foo" not in r
        POST("/service/testservice/q/testq/push","value=foo")        
        POST("/service/testservice/q/testq/push","value=bar")
        r = POST("/service/testservice/q/testq/shift")
        assert "foo" in r.body[0]
        r = GET("/service/testservice/q/testq/")
        assert json_to_py(r) == ["bar"]

    def test_peek(self):
        POST("/service/testservice/q/testq/push","value=foo")
        POST("/service/testservice/q/testq/push","value=bar")
        r = GET("/service/testservice/q/testq/peek")
        assert r == "foo"
        r = GET("/service/testservice/q/testq/")
        assert json_to_py(r) == ["foo","bar"]

    def test_endpeek(self):
        POST("/service/testservice/q/testq/push","value=foo")
        POST("/service/testservice/q/testq/push","value=bar")
        r = GET("/service/testservice/q/testq/end_peek")
        assert r == "bar"
        r = GET("/service/testservice/q/testq/")
        assert json_to_py(r) == ["foo","bar"]

    def test_length(self):
        POST("/service/testservice/q/testq/push","value=foo")
        r = GET("/service/testservice/q/testq/length")
        assert r == "1"
        POST("/service/testservice/q/testq/push","value=foo")
        r = GET("/service/testservice/q/testq/length")
        assert r == "2"
        POST("/service/testservice/q/testq/pop")
        r = GET("/service/testservice/q/testq/length")
        assert r == "1"
        POST("/service/testservice/q/testq/pop")
        r = GET("/service/testservice/q/testq/length")
        assert r == "0"

    







	  




	  

