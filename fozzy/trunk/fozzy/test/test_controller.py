from turbogears.tests import util
from fozzy.controllers import build_controllers
from fozzy.model import Application, Document
from json import read as json_to_obj
import cherrypy, unittest

from turbogears import database
database.set_db_uri("postgres://fozzy@/fozzy_test")
cherrypy.config.update({'global' : {'server.environment' : 'production', 'server.logToScreen' : False,
                                    }})

def clear_all_applications():
    for app in Application.select():
        app.destroySelf()

def GET(url,headers={}):
    util.createRequest(url,headers=headers)
    if cherrypy.response.headerMap['Content-Type'] == 'text/plain':
        return json_to_obj(cherrypy.response.body[0])
    else:
        return cherrypy.response.body[0]

import cStringIO as StringIO
def POST(url,data=""):
    rfile = StringIO.StringIO(data)
    util.createRequest(url,method="POST",rfile=rfile)
    return cherrypy.response

def PUT(url):
    util.createRequest(url,method="PUT")
    return cherrypy.response

def DELETE(url):
    util.createRequest(url,method="DELETE")
    return cherrypy.response

def setup_module(self):
    clear_all_applications()
    build_controllers()

def teardown_module(self):
    clear_all_applications()


class FozzyTest(unittest.TestCase):
    pass

class ApplicationTest(FozzyTest):
    def test_root(self):
        r = json_to_obj(GET("/"))
        assert type(r) == type([])
        assert len(r) == 0

        POST("/application/regressiontest/")
        r = json_to_obj(GET("/"))
        assert len(r) == 1
        assert "regressiontest" in r


        POST("/application/regressiontest2/")
        r = json_to_obj(GET("/"))
        assert len(r) == 2
        assert "regressiontest2" in r

        DELETE("/application/regressiontest2/")
        r = json_to_obj(GET("/"))
        assert len(r) == 1
        assert "regressiontest2" not in r

class DocumentTest(FozzyTest):
    def test_basics(self):
        POST("/application/regressiontest/document/testdoc/index_document",
             data="text=this%20is%20some%20text%20to%20index")
        r = GET("/application/regressiontest/document/testdoc/")

        assert r == "this is some text to index"
        r = json_to_obj(GET("/application/regressiontest/search?q=index"))
        assert len(r) == 1
        assert "testdoc" == r[0][0]

        DELETE("/application/regressiontest/document/testdoc/")
        r = json_to_obj(GET("/application/regressiontest/search?q=index"))
        assert len(r) == 0


	  



	  

