from turbogears import testutil as util
from gossip.controllers import build_controllers
from gossip.model import Service,Thread,Comment
import cherrypy,unittest
from json import read as json_to_py
import cStringIO as StringIO

from turbogears import database
database.set_db_uri("sqlite:///:memory:")
cherrypy.config.update({'global' : {'server.environment' : 'development'}})

def GET(url,headers={}):
    util.create_request(url,headers=headers)
    return cherrypy.response.body[0]

def POST(url,data=""):
    rfile = StringIO.StringIO(data)
    util.create_request(url,method="POST",rfile=rfile)
    return cherrypy.response

def DELETE(url):
    util.create_request(url,method="DELETE")
    return cherrypy.response

def createTables():
    Service.createTable(ifNotExists=True)
    Thread.createTable(ifNotExists=True)
    Comment.createTable(ifNotExists=True)

def dropTables():
    Comment.dropTable(ifExists=True)
    Thread.dropTable(ifExists=True)
    Service.dropTable(ifExists=True)

class GossipTest(unittest.TestCase):
    def setUp(self):
        createTables()
        self.service = Service(name="testservice")
        cherrypy.root = build_controllers()

    def tearDown(self):
        dropTables()

class TestService(GossipTest):
    def test_basics(self):
        util.create_request("/",method="POST")
        print str(cherrypy.response.body[0])
        assert 1 == 0

    def test_add(self):
        POST("/service/newservice/")
        r = GET("/")
        print str(r)
        assert "newservice" in r

    def test_delete(self):
        POST("/service/newservice/")
        r = GET("/")
        assert "newservice" in r
        DELETE("/service/newservice/")
        r = GET("/")
        assert "newservice" not in r

class TestThread(GossipTest):
    def test_add(self):
        POST("/service/testservice/thread/testthread/")
        r = GET("/service/testservice/")
        assert "testthread" in r

    def test_delete(self):
        POST("/service/testservice/thread/testthread/")
        r = GET("/service/testservice/")
        assert "testthread" in r
        DELETE("/service/testservice/thread/testthread/")
        r = GET("/service/testservice/")
        assert "testthread" not in r

class TestComment(GossipTest):
    def test_add(self):
        POST("/service/testservice/thread/testthread/reply","body=test%20body")
        r = GET("/service/testservice/thread/testthread/")
        assert "test body" in r

    def test_delete(self):
        comment_id = POST("/service/testservice/thread/testthread/reply","body=test%20body").body[0]
        r = GET("/service/testservice/thread/testthread/")
        assert "test body" in r
        DELETE("/service/testservice/thread/testthread/comment/%s" % comment_id)
        r = GET("/service/testservice/thread/testthread/")
        assert "test body" not in r


	  


	  
