import turbogears
from turbogears import controllers
from nqdq.model import Service,Q,Item,hub
from restresource import RESTResource
from simplejson import dumps as jsonify
from restclient import POST
import cherrypy
from sqlobject import *

def broadcast_event(event_name,params={}):
    pebble_base = cherrypy.config.get("pebblebase","")
    if pebble_base == "":
        return
    POST(pebble_base + "/event/" + event_name + "/trigger", params=params, async=True)

def build_controllers():
    m = Root()
    s = ServiceController()
    q = QController()
    s.REST_children = {'q' : q}
    cherrypy.root = m
    cherrypy.root.service = s
    return m

class Root(controllers.Root,RESTResource):
    @turbogears.expose()
    def index(self):
        return jsonify([s.name for s in Service.select()])
        
class ServiceController(RESTResource):
    def REST_instantiate(self,name,**kwargs):
        try:
            s = Service.byName(name.encode('utf8'))
            return s
        except:
            return None

    def REST_create(self,name,**kwargs):
        s = Service(name=name)
        hub.commit()
        broadcast_event("service_created",dict(service=name))
        return s

    def index(self,service,**kwargs):
        return jsonify([q.name for q in Q.select(Q.q.serviceID == service.id)])
    index.expose_resource = True

    def delete(self,service):
        name = service.name
        service.destroySelf()
        hub.commit()
        broadcast_event("service_destroyed",dict(service=name))
        return "ok"
    delete.expose_resource = True

    def update(self,service):
        return "ok"
    update.expose_resource = True

class QController(RESTResource):
    def REST_instantiate(self, name, **kwargs):
        try:
            service = self.parents[0]
            r = Q.select(AND(Q.q.name == name.encode('utf8'),
                             Q.q.serviceID == service.id))[0]
            return r
        except Exception, e:
            return None

    def REST_create(self,name,**kwargs):
        service = self.parents[0]
        q = Q(name=name,service=service)
        broadcast_event("queue_created",dict(service=service.name,name=name))
        hub.commit()
        return q

    def index(self,q,**kwargs):
        return jsonify([item.value for item in q.items])
    index.expose_resource = True

    def delete(self,q):
        name = q.name
        q.destroySelf()
        hub.commit()
        broadcast_event("queue_deleted",dict(service=q.service.name,name=name))
        return "ok"
    delete.expose_resource = True

    def shift(self,q):
        """ return the first item in the Q and remove it"""
        if len(q.items):
            i = q.items[0]
            i.destroySelf()
            hub.commit()
            broadcast_event("shift",dict(service=q.service.name,q=q.name,value=i.value))
            return i.value
        else:
            return ""
    shift.expose_resource = True

    def peek(self,q):
        """ return the first item on the Q but don't remove it """
        if len(q.items):
            broadcast_event("peek",dict(service=q.service.name,q=q.name,value=q.items[0].value))
            return q.items[0].value
        else:
            return ""
    peek.expose_resource = True    

    def pop(self,q):
        """ remove the last item on the Q and return it """
        if len(q.items):
            i = q.items[-1]
            i.destroySelf()
            hub.commit()
            broadcast_event("pop",dict(service=q.service.name,q=q.name,value=i.value))
            return i.value
        else:
            return ""
    pop.expose_resource = True    

    def end_peek(self,q):
        """ return last item on Q but don't remove it """
        if len(q.items):
            broadcast_event("end_peek",dict(service=q.service.name,q=q.name,value=q.items[-1].value))
            return q.items[-1].value
        else:
            return ""
    end_peek.expose_resource = True    

    def push(self,q,value=""):
        """ add an item to the end of the Q """
        q.push(value)
        hub.commit()
        broadcast_event("push",dict(service=q.service.name,q=q.name,value=value))
        return "ok"
    push.expose_resource = True    

    def unshift(self,q,value=""):
        """ add an item at the front of the Q """
        q.unshift(value)
        hub.commit()
        broadcast_event("unshift",dict(service=q.service.name,q=q.name,value=value))
        return "ok"
    unshift.expose_resource = True    

    def update(self,q,**kwargs):
        return self.push(q,**kwargs)
    update.expose_resource = True

    def length(self,q,**kwargs):
        return str(len(q.items))
    length.expose_resource = True











	  

	  
