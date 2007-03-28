from tasty.model import *
import cherrypy
from restresource import RESTResource
from dimension import Dimension
from simplejson import dumps as jsonify
import turbogears
from turbogears import controllers
from tasty.helpers import sqlobject_to_strings, xmlify, htmlify, deunicodify, broadcast_event
from types import *

def build_controllers():
    m = Root()
    s = ServiceController()
    u = UserController()
    i = ItemController()
    t = TagController()

    s.REST_children = {'user' : u, 'item' : i, 'tag'  : t}
    u.REST_children = {'item' : i, 'tag'  : t, 'user' : u}
    i.REST_children = {'user' : u, 'tag'  : t, 'item' : i}
    t.REST_children = {'user' : u, 'item' : i, 'tag' : t}

    s.main = m
    u.main = m
    i.main = m
    t.main = m

    cherrypy.root = m
    cherrypy.root.service = s
    return m

class Root(controllers.Root):
    def index(self):
        return jsonify([s.name for s in Service.select()])
    index.exposed = True

    obj = {"user" : [], "item" : [], "tag" : [],
           "-user" : [], "-item" : [], "-tag" : []}

    s = None

    def to_event_str(self):
        users = ("users=" + ",".join([u.username for u in self.obj["user"]])
                 + ",".join(["-" + u.username for u in self.obj["-user"]]))
        items = ("items=" + ",".join([u.name for u in self.obj["item"]])
                 + ",".join(["-" + u.name for u in self.obj["-item"]]))
        tags = ("tags=" + ",".join([u.name for u in self.obj["tag"]])
                + ",".join(["-" + u.name for u in self.obj["-tag"]]))
        return users + ";" + items + ";" + tags

    def referer(self):
        return cherrypy.request.headerMap.get('Referer','/')


    def _cpOnError(self):
        err = sys.exc_info()
        sio = StringIO.StringIO()
        hook = cgitb.Hook(file=sio,format="text")
        hook.handle(info=err)
        tb = sio.getvalue()
        if cherrypy.config.get('DEBUG',False):
            cherrypy.response.headerMap['Content-Type'] = 'text/plain'
            cherrypy.response.body = [tb]
        else:
            if cherrypy.config.get('error_report_email',False):
                body = "URL: %s\nReferer: %s\ncookies: %s\nheaders: %s\ntraceback: %s" % (cherrypy.request.requestLine,
                                                                                          self.referer(),
                                                                                          str(cherrypy.request.simpleCookie),
                                                                                          str(cherrypy.request.headerMap),
                                                                                          tb)
                POST(cherrypy.config.get('hormel_url'),params={'to_address' : cherrypy.config.get('error_report_email_address'),
                                                               'from_address' : cherrypy.config.get('error_report_email_address'),
                                                               'subject' : "Quip server error: %s" % str(err[0]),
                                                               'body' : body})
            cherrypy.response.body = ['Error: ' + str(err[0])]


class ServiceController(RESTResource):

    REST_content_types = {'application/xml' : 'to_xml',
                          'text/html' : 'to_html',
                          'text/plain' : 'to_json'}
    REST_default_content_type = "text/plain"

    def to_xml(self,d):
        s = """<?xml version="1.0"?><results>""" + xmlify(sqlobject_to_strings(d)) + "</results>"
        return deunicodify(s)

    def to_html(self,d):
        return "<html><head><title>tasty</title><body>" + htmlify(sqlobject_to_strings(d)) + "</body>"

    def to_json(self,d):
        s = jsonify(sqlobject_to_strings(d))
        return deunicodify(s)

    def REST_instantiate(self,name,**kwargs):
        # reset accumulators. this should probably be done
        # somewhere else. this is kind of dirty.
        self.main.obj["tag"] = []
        self.main.obj["user"] = []
        self.main.obj["item"] = []
        self.main.obj["-user"] = []
        self.main.obj["-item"] = []
        self.main.obj["-tag"] = []
        try:
            s = Service.byName(name.encode('utf8'))
            self.main.s = s
            return s
        except:
            return None
    def REST_create(self,name,**kwargs):
        s = Service(name=name)
        self.main.s = s
        hub.commit()
        broadcast_event("service_created",dict(service=s.name))
        return s

    def index(self,service,**kwargs):
        results = filter_query(service,[],[],[],[],[],[])
        return results
    index.expose_resource = True
    def delete(self,service):
        service.destroySelf()
        hub.commit()
        broadcast_event("service_deleted",dict(service=service.name))
        return "ok"
    delete.expose_resource = True

    def update(self,service):
        # REST_create should have handled it
        pass
    update.expose_resource = True

    def cloud(self,service):
        results = cloud(service,[],[],[])
        return results
    cloud.expose_resource = True



class UserController(Dimension):
    rclass         = User
    r_id_q         = User.q.username
    rclassname     = "user"
    rclass_id_name = "username"

class ItemController(Dimension):
    rclass         = Item
    r_id_q         = Item.q.name
    rclassname     = "item"
    rclass_id_name = "name"

class TagController(Dimension):
    rclass         = Tag
    r_id_q         = Tag.q.name
    rclassname     = "tag"
    rclass_id_name = "name"
