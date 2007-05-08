from turbogears import testutil as util
from tasty.controllers import build_controllers
from tasty.model import Service,User,Item,Tag,UserItemTag,hub
from simplejson import loads as json_to_obj
import cherrypy,unittest

from turbogears import database
database.set_db_uri("sqlite:///:memory:")
cherrypy.config.update({'global' : {'server.thread_pool' : '1'}})
#cherrypy.config.update({'global' : {'server.environment' : 'development', 'server.logToScreen' : False}})

def createTables():
    Service.createTable(ifNotExists=True)
    User.createTable(ifNotExists=True)
    Item.createTable(ifNotExists=True)
    Tag.createTable(ifNotExists=True)
    UserItemTag.createTable(ifNotExists=True)

def dropTables():
    UserItemTag.dropTable(ifExists=True)
    Tag.dropTable(ifExists=True)
    Item.dropTable(ifExists=True)
    User.dropTable(ifExists=True)
    Service.dropTable(ifExists=True)

class TastyTest(unittest.TestCase):
    def setUp(self):
        createTables()
        self.service = Service(name="testservice")
        self.user    = User(username="testuser",service=self.service)
        self.item    = Item(name="testitem",service=self.service)
        self.tag     = Tag(name="testtag",service=self.service)

        self.users = dict([(username,User(username=username,service=self.service)) for username in ["anders","jonah","eric","sky","maurice","marc"]])
        self.items = dict([(name,Item(name=name,service=self.service)) for name in ["fernandez fierro","in flames","mastodon","covenant"]])
        self.tags = dict([(name,Tag(name=name,service=self.service)) for name in ["tango","metal","swedish","argentinian","industrial"]])
        hub.commit()
        root = build_controllers()
        cherrypy.root = root


    def tearDown(self):
        dropTables()
        cherrypy.root = None

def GET(url,headers={}):
    util.create_request(url,headers=headers)
    if cherrypy.response.headerMap['Content-Type'] == 'text/plain':
        obj = json_to_obj(cherrypy.response.body[0])
        return obj
    else:
        return cherrypy.response.body[0]

def POST(url):
    util.create_request(url,method="POST")
    return cherrypy.response

def PUT(url):
    util.create_request(url,method="PUT")
    return cherrypy.response

def DELETE(url):
    util.create_request(url,method="DELETE")
    return cherrypy.response

class TestRoot(TastyTest):
    def test_basics(self):
        "basic test"
        util.create_request("/")
        body = cherrypy.response.body[0]
        assert ["testservice"] == json_to_obj(body)

        r = GET("/")
        assert "testservice" in r

class TestService(TastyTest):

    def test_index(self):
        "tests the results of calls to the service"
        r = GET("/service/testservice/")
        assert r.has_key('items')
        assert r.has_key('users')
        assert r.has_key('tags')
        assert r.has_key('user_item_tags')
        assert {u'item' : u'testitem'} in r['items']
        assert {u'user' : u'anders'} in r['users']
        assert {u'tag' : u'swedish'} in r['tags']

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
        DELETE("/service/newservice/")
        PUT("/service/newservice/")
        r = GET("/")
        assert "newservice" in r

    def test_cloud(self):
        r = GET("/service/testservice/cloud")
        assert r.has_key('tags')
        assert r.has_key('users')
        assert r.has_key('items')

class TestTags(TastyTest):
    def test_basics(self):
        POST("/service/testservice/user/anders/")
        r = GET("/service/testservice/")
        assert r.has_key('users')
        assert {'user' : 'anders'} in r['users']

        r = GET("/service/testservice/user/anders/")
        assert r.has_key('tags')
        assert r.has_key('items')

        assert r['tags'] == []
        assert r['items'] == []

        POST("/service/testservice/user/anders/item/foo/tag/bar/tag/baz")
        r = GET("/service/testservice/")

        assert {'tag' : 'bar'} in r['tags']
        assert {'tag' : 'baz'} in r['tags']
        assert {'item' : 'foo'} in r['items']

        r = GET("/service/testservice/user/anders/")
        assert {'tag' : 'bar'} in r['tags']
        assert {'tag' : 'baz'} in r['tags']
        assert {'item' : 'foo'} in r['items']
        assert [{'tag' : 'bar'},{'item' : 'foo'}] in r['tag_items']

    def test_addmulti(self):

        # carefully verify beginning state
        POST("/service/testservicex/user/x/item/y/tag/z/tag/w")
        r = GET("/service/testservicex/")

        assert {'tag' : 'z'} in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'item' : 'y'} in r['items']
        assert {'user' : 'x'} in r['users']
        assert [{'user' : 'x'}, {'item' : 'y'}, {'tag' : 'z'}] in r['user_item_tags']
        assert [{'user': 'x'}, {'item': 'y'}, {'tag': 'w'}] in r['user_item_tags']

        r = GET("/service/testservicex/user/x")
        assert {'tag' : 'z'} in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'item' : 'y'} in r['items']
        assert [{'tag' : 'z'},{'item' : 'y'}] in r['tag_items']
        assert [{'tag' : 'w'},{'item' : 'y'}] in r['tag_items']        

        r = GET("/service/testservicex/item/y")
        assert {'tag' : 'z'} in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'user' : 'x'} in r['users']
        assert [{'tag': 'z'}, {'user': 'x'}] in r['tag_users']
        assert [{'tag': 'w'}, {'user': 'x'}] in r['tag_users']

        r = GET("/service/testservicex/tag/z")
        assert {'item' : 'y'} in r['items']
        assert {'user' : 'x'} in r['users']
        assert [{'user': 'x'}, {'item': 'y'}] in r['user_items']

        r = GET("/service/testservicex/tag/w")
        assert {'item' : 'y'} in r['items']
        assert {'user' : 'x'} in r['users']
        assert [{'user': 'x'}, {'item': 'y'}] in r['user_items']

        
    def test_delete_single_uit(self):
        # clear + reset
        DELETE("/service/testservicex/")
        POST("/service/testservicex/user/x/item/y/tag/z/tag/w")

        # try deleting one
        DELETE("/service/testservicex/user/x/item/y/tag/z")
        r = GET("/service/testservicex/")

        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'item' : 'y'} in r['items']
        assert {'user' : 'x'} in r['users']
        assert [{'user' : 'x'}, {'item' : 'y'}, {'tag' : 'z'}] not in r['user_item_tags']
        assert [{'user': 'x'}, {'item': 'y'}, {'tag': 'w'}] in r['user_item_tags']

        r = GET("/service/testservicex/user/x")
        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'item' : 'y'} in r['items']
        assert [{'tag' : 'z'},{'item' : 'y'}] not in r['tag_items']
        assert [{'tag' : 'w'},{'item' : 'y'}] in r['tag_items']        

        r = GET("/service/testservicex/item/y")
        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'user' : 'x'} in r['users']
        assert [{'tag': 'z'}, {'user': 'x'}] not in r['tag_users']
        assert [{'tag': 'w'}, {'user': 'x'}] in r['tag_users']

        r = GET("/service/testservicex/tag/w")
        assert {'item' : 'y'} in r['items']
        assert {'user' : 'x'} in r['users']
        assert [{'user': 'x'}, {'item': 'y'}] in r['user_items']

    def test_delete_multi_uit(self):
        # clear + reset
        DELETE("/service/testservicex/")
        POST("/service/testservicex/user/x/item/y/tag/z/tag/w")

        # try deleting two tags
        
        DELETE("/service/testservicex/user/x/item/y/tag/z/tag/w")
        r = GET("/service/testservicex/")

        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} not in r['tags']
        assert {'item' : 'y'} not in r['items']
        assert {'user' : 'x'} not in r['users']
        assert [{'user' : 'x'}, {'item' : 'y'}, {'tag' : 'z'}] not in r['user_item_tags']
        assert [{'user': 'x'}, {'item': 'y'}, {'tag': 'w'}] not in r['user_item_tags']

    def test_delete_single_user_tag(self):
        # clear + reset
        DELETE("/service/testservicex/")
        POST("/service/testservicex/user/x/item/y/tag/z/tag/w")

        # delete a user-tag
        DELETE("/service/testservicex/user/x/tag/z/")
        r = GET("/service/testservicex/")

        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'item' : 'y'} in r['items']
        assert {'user' : 'x'} in r['users']
        assert [{'user' : 'x'}, {'item' : 'y'}, {'tag' : 'z'}] not in r['user_item_tags']
        assert [{'user': 'x'}, {'item': 'y'}, {'tag': 'w'}] in r['user_item_tags']

        r = GET("/service/testservicex/user/x")
        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'item' : 'y'} in r['items']
        assert [{'tag' : 'z'},{'item' : 'y'}] not in r['tag_items']
        assert [{'tag' : 'w'},{'item' : 'y'}] in r['tag_items']        

        r = GET("/service/testservicex/item/y")
        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'user' : 'x'} in r['users']
        assert [{'tag': 'z'}, {'user': 'x'}] not in r['tag_users']
        assert [{'tag': 'w'}, {'user': 'x'}] in r['tag_users']

        r = GET("/service/testservicex/tag/w")
        assert {'item' : 'y'} in r['items']
        assert {'user' : 'x'} in r['users']
        assert [{'user': 'x'}, {'item': 'y'}] in r['user_items']
        
    def test_delete_single_tag(self):
        # clear + reset
        DELETE("/service/testservicex/")
        POST("/service/testservicex/user/x/item/y/tag/z/tag/w")

        # delete a tag
        DELETE("/service/testservicex/tag/z/")
        r = GET("/service/testservicex/")

        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'item' : 'y'} in r['items']
        assert {'user' : 'x'} in r['users']
        assert [{'user' : 'x'}, {'item' : 'y'}, {'tag' : 'z'}] not in r['user_item_tags']
        assert [{'user': 'x'}, {'item': 'y'}, {'tag': 'w'}] in r['user_item_tags']

        r = GET("/service/testservicex/user/x/")
        
        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'item' : 'y'} in r['items']
        assert [{'tag' : 'z'},{'item' : 'y'}] not in r['tag_items']
        assert [{'tag' : 'w'},{'item' : 'y'}] in r['tag_items']        

        r = GET("/service/testservicex/item/y")
        assert {'tag' : 'z'} not in r['tags']
        assert {'tag' : 'w'} in r['tags']
        assert {'user' : 'x'} in r['users']
        assert [{'tag': 'z'}, {'user': 'x'}] not in r['tag_users']
        assert [{'tag': 'w'}, {'user': 'x'}] in r['tag_users']

        r = GET("/service/testservicex/tag/w")
        assert {'item' : 'y'} in r['items']
        assert {'user' : 'x'} in r['users']
        assert [{'user': 'x'}, {'item': 'y'}] in r['user_items']
	

    def test_unicode(self):
        POST('/service/testservice/user/anders/item/foo/tag/%E5%AD%90%E4%BE%9B/')
        r = GET("/service/testservice/")

        # u"\u5b50\u4f9b" == %E5%AD%90%E4%BE%9B url encoded

        assert {'tag' : u"\u5b50\u4f9b"} in r['tags']
        
    def test_cloud(self):
        r = GET("/service/testservice/cloud")
        assert r['items'] == []
        assert r['users'] == []
        assert r['tags']  == []

        POST("/service/testservice/user/anders/item/foo/tag/bar/")
        POST("/service/testservice/user/anders/item/qux/tag/bar/")

        r = GET("/service/testservice/cloud")
        assert {'item' : 'foo',    'count' : 1} in r['items']
        assert {'tag'  : 'bar',    'count' : 2} in r['tags']
        assert {'user' : 'anders', 'count' : 2} in r['users']

        r = GET("/service/testservice/user/anders/cloud")
        assert {'item' : 'foo','count' : 1} in r['items']
        assert {'tag'  : 'bar','count' : 2} in r['tags']

        r = GET("/service/testservice/item/foo/cloud")
        assert {'tag'  : 'bar',   'count' : 1} in r['tags']
        assert {'user' : 'anders','count' : 1} in r['users']

        r = GET("/service/testservice/tag/bar/cloud")
        assert {'item'  : 'foo',   'count' : 1} in r['items']
        assert {'item'  : 'qux',   'count' : 1} in r['items']
        assert {'user'  : 'anders','count' : 2} in r['users']

    def test_accept(self):
        """ test the handling of 'Accept:' http headers """
        # default should be json
        r = GET("/service/testservice/")
        assert r.has_key('tags')

        # explicitly ask for text/plain (json)
        r = GET("/service/testservice/",headers={"Accept" : "text/plain"})
        assert r.has_key('tags')

        # ask for xml
        r = GET("/service/testservice/",headers={"Accept" : "application/xml"})
        assert """<?xml """ in r

        # ask for html
        r = GET("/service/testservice/",headers={"Accept" : "text/html"})
        assert "<html>" in r

        r = GET("/service/testservice/user/anders/",headers={"Accept" : "application/xml"})
        assert """<?xml """ in r

        r = GET("/service/testservice/user/anders/",headers={"Accept" : "text/html"})
        assert """<html>""" in r

        # ask for a bogus accept type
        r = GET("/service/testservice/user/anders/",headers={"Accept" : "application/foo"})
        assert r.has_key('items')

    def test_related(self):
        POST("/service/testservice/user/anders/item/foo/tag/bar/")
        POST("/service/testservice/user/anders/item/qux/tag/bar/")

        r = GET("/service/testservice/item/foo/related")

        assert r.has_key('items')
        assert {'item' : 'qux'} in r['items']
        # make sure it excludes the original query
        assert {'item' : 'foo'} not in r['items']

        r = GET("/service/testservice/tag/bar/related")
        assert r.has_key('tags')

        r = GET("/service/testservice/user/anders/related")
        assert r.has_key('users')
