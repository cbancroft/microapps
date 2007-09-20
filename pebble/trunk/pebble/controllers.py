import turbogears
from turbogears import controllers
from restresource import RESTResource
from pebble.model import Service,Event,Handler,AND
from simplejson import dumps as jsonify
import cherrypy
import StringIO, sys, cgitb
from restclient import POST

def build_controllers():
    m = Root()
    s = ServiceController()
    e = EventController()
    h = HandlerController()


    s.REST_children = {'event' : e}
    e.REST_children = {'handler' : h}

    cherrypy.root = m
    cherrypy.root.service = s
    return m

class Root(controllers.Root):
    @turbogears.expose()
    def index(self):
        return jsonify([s.name for s in Service.select()])

    def _cpOnError(self):
        err = sys.exc_info()
        sio = StringIO.StringIO()
        hook = cgitb.Hook(file=sio,format="text")
        hook.handle(info=err)
        tb = sio.getvalue()
        if cherrypy.config.get('DEBUG',False):
            cherrypy.response.headerMap['Content-Type'] = 'text/html'
            cherrypy.response.body = [tb]
        else:
            body = "URL: %s\nReferer: %s\ncookies: %s\nheaders: %s\ntraceback: %s" % (cherrypy.request.requestLine,
                                                                                      self.referer(),
                                                                                      str(cherrypy.request.simpleCookie),
                                                                                      str(cherrypy.request.headerMap),
                                                                                      tb)
            POST("http://hormel.ccnmtl.columbia.edu/",params={'to_address' : 'anders@columbia.edu',
                                                              'from_address' : 'anders@columbia.edu',
                                                              'subject' : "Pebble server error: %s" % str(err[0]),
                                                              'body' : body})
            cherrypy.response.body = ['Error: ' + str(err[0])]

    def referer(self):
        return cherrypy.request.headerMap.get('Referer','/')

class ServiceController(RESTResource):
    def REST_instantiate(self,name,**kwargs):
        try:
            return Service.byName(name.encode('utf8'))
        except:
            return None
    def REST_create(self,name,**kwargs):
        return Service(name=name)

    def index(self,service,**kwargs):
        return jsonify([e.name for e in service.events])
    index.expose_resource = True
    def delete(self,service):
        service.destroySelf()
        return "ok"
    delete.expose_resource = True
    def add(self,service):
        # REST_create should have handled everything
        pass
    add.expose_resource = True

    def update(self,service):
        # REST_create should have handled it
        pass
    update.expose_resource = True

class EventController(RESTResource):
    def REST_instantiate(self,name,**kwargs):
        try:
            return Event.select(AND(Event.q.name == name, Event.q.serviceID == self.parents[0].id))[0]
        except Exception, e:
            print str(e)
            return None
    def REST_create(self,name,**kwargs):
        return Event(name = name, service=self.parents[0])

    def index(self,event,**kwargs):
        """ list the handlers for the event """
        return jsonify([{'id' : h.id, 'url' : h.url, 'method' : h.method} for h in event.handlers])
    index.expose_resource = True

    def delete(self,event):
        event.destroySelf()
        return "ok"
    delete.expose_resource = True
    def add(self,event):
        # REST_create should have handled everything
        pass
    add.expose_resource = True

    def update(self,event):
        # REST_create should have handled it
        pass
    update.expose_resource = True

    @cherrypy.expose
    def add_handler(self,event,url="",method="POST"):
        h = Handler(event=event,url=url,method=method)
        raise cherrypy.HTTPRedirect("/service/%s/event/%s/handler/%d/" % (self.parents[0].name, event.name, h.id))
    add_handler.expose_resource = True

    def trigger(self,event,**kwargs):
        print str(event.handlers)
        for h in event.handlers:
            h.handle(params=kwargs)
        raise cherrypy.HTTPRedirect("/service/%s/event/%s/" % (self.parents[0].name, event.name))
    trigger.expose_resource = True

class HandlerController(RESTResource):
    def REST_instantiate(self,id,**kwargs):
        try:
            return Handler.get(id)
        except:
            return None
    def REST_create(self,name,**kwargs):
        # we don't really allow this
        return None

    def index(self,handler,**kwargs):
        """ return some basic info about this handler """
        return jsonify({'url' : handler.url, 'method' : handler.method})
    index.expose_resource = True

    def delete(self,handler):
        handler.destroySelf()
        return "ok"
    delete.expose_resource = True
    def add(self,handler,**kwargs):
        # REST_create should have handled everything
        pass
    add.expose_resource = True

    def update(self,handler,**kwargs):
        # REST_create should have handled it
        pass
    update.expose_resource = True

