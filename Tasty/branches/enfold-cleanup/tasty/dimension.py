from restresource import RESTResource
from tasty.model import *
from simplejson import dumps as jsonify
from tasty.helpers import sqlobject_to_strings, xmlify, htmlify, deunicodify, broadcast_event
from types import *

class Dimension(RESTResource):
    """ common base class for user, item, and tag.

    exploits the symmetry of the schema.
    """

    list = list

    REST_content_types = {'application/xml' : 'to_xml',
                          'text/html' : 'to_html',
                          'text/plain' : 'to_json'}
    REST_default_content_type = 'text/plain'
    REST_map = {'PUT' : 'update'}
    
    def to_xml(self,d):
        s = """<?xml version="1.0"?><results>""" + xmlify(sqlobject_to_strings(d)) + "</results>"
        return deunicodify(s)

    def to_html(self,d):
        return "<html><head><title>tasty</title><body>" + htmlify(sqlobject_to_strings(d)) + "</body>"

    def to_json(self,d):
        s = jsonify(sqlobject_to_strings(d))
        return deunicodify(s)

    def delete(self,obj):
        delete_rels(self.main.s,
                    self.main.obj["user"],
                    self.main.obj["item"],
                    self.main.obj["tag"],
                    self.main.obj["-user"],
                    self.main.obj["-item"],
                    self.main.obj["-tag"])
        return "ok"
    delete.expose_resource = True

    def index(self,obj,**params):
        results = filter_query(self.main.s,
                               self.main.obj["user"],
                               self.main.obj["item"],
                               self.main.obj["tag"],
                               self.main.obj["-user"],
                               self.main.obj["-item"],
                               self.main.obj["-tag"])
        return results
    index.expose_resource = True

    def related(self,obj,limit=10,**params):
        results = related(self.main.s,
                          self.main.obj['user'],
                          self.main.obj['item'],
                          self.main.obj['tag'],
                          self.main.obj["-user"],
                          self.main.obj["-item"],
                          self.main.obj["-tag"],
                          limit=limit)
        return results
    related.expose_resource = True

    def update(self,obj,**params):
        if len(self.parents) == 1:
            return "ok"
        build_all_relationships(self.main.obj["user"],
                                self.main.obj["item"],
                                self.main.obj["tag"])
        return "ok"
    update.expose_resource = True

    def cloud(self,*args,**params):
        results = cloud(self.main.s,
                        self.main.obj["user"],
                        self.main.obj["item"],
                        self.main.obj["tag"])
        return results
    cloud.expose_resource = True

    def REST_instantiate(self,id,**kwargs):
        service = self.parents[0]
        try:
            if id.startswith("-"):
                # a NOT operator
                id = id[1:]
                o = self.rclass.select(AND(self.r_id_q == id.encode('utf8'),
                                           self.rclass.q.serviceID == service.id))[0]
                self.main.obj["-" + self.rclassname].append(o)
            else:
                o = self.rclass.select(AND(self.r_id_q == id.encode('utf8'),
                                       self.rclass.q.serviceID == service.id))[0]
                self.main.obj[self.rclassname].append(o)
            return o
        except:
            return None

    def REST_create(self,id,**kwargs):
        service = self.parents[0]
        if id.startswith("-"):
            o = self.rclass(**dict([(self.rclass_id_name, id[1:]),
                                    ("service", service)]))
            self.main.obj["-" + self.rclassname].append(o)
        else:
            o = self.rclass(**dict([(self.rclass_id_name, id),
                                    ("service", service)]))
            self.main.obj[self.rclassname].append(o)
        return o
