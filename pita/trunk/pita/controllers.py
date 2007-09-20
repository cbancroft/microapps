import logging

import cherrypy

import turbogears
from turbogears import controllers, expose, validate, redirect
from turbogears import widgets

from pita.model import *
from restresource import RESTResource
from simplejson import dumps as jsonify
from restclient import POST


def broadcast_event(event_name,params={}):
    pebble_base = cherrypy.config.get("pebblebase","")
    if pebble_base == "":
        print "no pebble base"
        return
    POST(pebble_base + "/event/" + event_name + "/trigger", params=params, async=True)

class ItemController(RESTResource):
    def REST_instantiate(self,name,**kwargs):
        try:
            service = self.parents[0]
            return Item.select(AND(Item.q.name == name.encode('utf8'), Item.q.serviceID == service.id))[0]
        except:
            return None

    def REST_create(self,name,**kwargs):
        service = self.parents[0]
        value = kwargs.get('value','')
        broadcast_event("item_updated",dict(service=service.name,item=name,value=value))
        i = Item(name=name.encode('utf8'),value=value.encode('utf8'),service=service)
        hub.commit()
        return i

    def index(self,item,**kwargs):
        return item.value
    index.expose_resource = True

    def add(self,item,**kwargs):
        return "ok"
    add.expose_resource = True

    def update(self,item,**kwargs):
        item.value = kwargs.get('value','')
        hub.commit()
        return "ok"
    update.expose_resource = True

    def delete(self,item,**kwargs):
        item.destroySelf()
        hub.commit()
        broadcast_event("item_deleted",dict(service=self.parents[0].name,item=item.name))
        return "ok"
    delete.expose_resource = True

class ServiceController(RESTResource):
    REST_children = {'item' : ItemController()}

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
        return jsonify([i.name for i in Item.select(Item.q.serviceID == service.id)])
    index.expose_resource = True

    def items(self,service,**kwargs):
        return jsonify([{"item" : i.name, "value" : i.value} for i in Item.select(Item.q.serviceID == service.id)])
    items.expose_resource = True

    def dictionary(self,service,**kwargs):
        return jsonify(dict([(i.name,i.value) for i in Item.select(Item.q.serviceID == service.id)]))
    dictionary.expose_resource = True

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

            
class Root(controllers.RootController):
    service = ServiceController()
    @turbogears.expose()
    def index(self): 
        return jsonify([s.name for s in Service.select()])
    

