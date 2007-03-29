"""
tests aren't very good yet. i'm having a hard time figuring out how to really
structure them.

but, basically, what you do to run them is

% python restresource/tests/test_server.py   # that starts the server on port 9080

and then in another terminal:

% nosetests

you'll need restclient, SQLObject, and sqlite installed to run the tests (though you don't need them
to just use restresourse normally. 

"""

import sys
sys.path.append(".")
from restresource import RESTResource
import cherrypy
from restclient import GET, POST, DELETE, PUT
import unittest
from sqlobject import *
__connection__ = "sqlite:///:memory:"


class User(SQLObject):
    username = UnicodeCol(default="",alternateID=True)
    email = UnicodeCol(default="")
    fullname = UnicodeCol(default="")

class Post(SQLObject):
    user = ForeignKey('User',cascade=True)
    slug = UnicodeCol(default="")
    title = UnicodeCol(default="")
    body = UnicodeCol(default="")


class MainController:
    @cherrypy.expose()
    def default(self,*args,**kwargs):
        return "blah"

class PostController(RESTResource):
    @cherrypy.expose()
    def read(self,post):
        return post.as_html()

    @cherrypy.expose()
    def delete(self,post):
        post.destroySelf()
        return "ok"

    @cherrypy.expose()
    def update(self,post,title="",body=""):
        post.title = title
        post.body = body
        return "ok"

    @cherrypy.expose()
    def create(self, post, title="", body=""):
        post.title = title
        post.body = body
        return "ok"


    def REST_instantiate(self, slug, **kwargs):
        try:
            user = self.parents[0]
            return Post.select(AND(Post.q.slug == slug, Post.q.userID == user.id))[0]
        except:
            return None

    def REST_create(self, slug, **kwargs):
        user = self.parents[0]
        return Post(slug=slug,user=user)

class UserController(RESTResource):
    REST_children = {'posts' : PostController()}

    @cherrypy.expose()
    def read(self,user):
        return user.as_html()

    @cherrypy.expose()
    def delete(self,user):
        user.destroySelf()
        return "ok"

    @cherrypy.expose()
    def update(self,user,fullname="",email=""):
        user.fullname = fullname
        user.email = email
        return "ok"

    @cherrypy.expose()
    def create(self, user, fullname="", email=""):
        user.fullname = fullname
        user.email = email
        return "ok"

    @cherrypy.expose()
    def extra_action(self,user):
        # do something else
        pass

    def REST_instantiate(self, username, **kwargs):
        try:
            return User.byUsername(username)
        except:
            return None

    def REST_create(self, username, **kwargs):
        return User(username=username)



def start_server():
    cherrypy.root      = MainController()
    cherrypy.root.user = UserController()
    cherrypy.config.update({'global' : {'server.socketPort' : 9080,
                                        'server.environment' : "production"}})
    cherrypy.server.start()

class TestRESTResource(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        cherrypy.server.stop()

    def test_basics(self):
        r = GET("http://localhost:9080/")
        assert r == "blah"

        


if __name__ == "__main__":
    start_server()
    
