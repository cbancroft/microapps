import cherrypy
import turbogears

from cherrypy.filters.basefilter import BaseFilter
from turbogears import controllers, database
from sqlobject.util.threadinglocal import local as threading_local

from restresource import RESTResource
from simplejson import dumps as jsonify

from tasty.model import *
from tasty.dimension import Dimension
from tasty.helpers import sqlobject_to_strings, xmlify, htmlify
from tasty.helpers import deunicodify, broadcast_event

class TransactionsFilter(BaseFilter):

    def on_start_resource(self):
        for hub in database.hub_registry:
            hub.begin()

#             print '*' * 20
#             import threading
#             print threading.currentThread().getName(), hub.threadConnection
#             print '*' * 20


    def after_error_response(self):
        database.rollback_all()

    def before_finalize(self):
        database.commit_all()

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

class ObjectsDescriptor(object):

    def __init__(self, name='obj'):
        self.name = name
        self.threadingLocal = threading_local()

    def __get__(self, obj, type=None):
        try:
            return getattr(self.threadingLocal, self.name)
        except AttributeError:
            value = {"user" : [], "item" : [], "tag" : [],
                     "-user" : [], "-item" : [], "-tag" : []}
            setattr(self.threadingLocal, self.name, value)
            return value

    def __set__(self, obj, value):
        if value is None:
            try:
                delattr(self.threadingLocal, self.name)
            except AttributeError:
                pass

class Root(controllers.Root):

    _cp_filters = [TransactionsFilter()]

    def index(self):
        return jsonify([s.name for s in Service.select()])
    index.exposed = True

    obj = ObjectsDescriptor()

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

class ServiceController(RESTResource):

    REST_content_types = {'application/xml' : 'to_xml',
                          'text/html' : 'to_html',
                          'text/plain' : 'to_json'}
    REST_default_content_type = "text/plain"
    REST_map = {'PUT' : 'update'}
    
    def to_xml(self,d):
        s = """<?xml version="1.0"?><results>""" + xmlify(sqlobject_to_strings(d)) + "</results>"
        return deunicodify(s)

    def to_html(self,d):
        return "<html><head><title>tasty</title><body>" + htmlify(sqlobject_to_strings(d)) + "</body>"

    def to_json(self,d):
        s = jsonify(sqlobject_to_strings(d))
        return deunicodify(s)

    def REST_instantiate(self,name,**kwargs):
        # Reset accumulators. This should probably be done somewhere
        # else. This is kind of dirty.  See the ObjectsDescriptor
        # above to find out why we set this to None.
        self.main.obj = None
        try:
            s = Service.byName(name.encode('utf8'))
            self.main.s = s
            return s
        except:
            return None

    def REST_create(self,name,**kwargs):
        s = Service(name=name)
        self.main.s = s
        return s

    def index(self,service,**kwargs):
        results = filter_query(service, [], [], [], [], [], [])
        return results
    index.expose_resource = True

    def delete(self,service):
        service.destroySelf()
        return "ok"
    delete.expose_resource = True

    def update(self,service):
        # REST_create should have handled it
        return "ok"
    update.expose_resource = True

    def cloud(self,service):
        results = cloud(service, [], [], [])
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
