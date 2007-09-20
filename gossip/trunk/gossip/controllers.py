import turbogears
from turbogears import controllers
from gossip.model import Service,Thread,Comment
from restresource import RESTResource
from simplejson import dumps as jsonify
from restclient import POST
import cherrypy
from sqlobject import *

def build_controllers():
    m = Root()
    s = ServiceController()
    t = ThreadController()
    c = CommentController()
    s.REST_children = {'thread' : t}
    t.REST_children = {'comment' : c}
    cherrypy.root = m
    cherrypy.root.service = s
    return m

def broadcast_event(event_name,params={}):
    pebble_base = cherrypy.config.get("pebblebase","")
    if pebble_base == "":
        return
    POST(pebble_base + "/event/" + event_name + "/trigger", params=params, async=True)

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
        broadcast_event("service_created",dict(service=name))
        hub.commit()
        return s

    def index(self,service,**kwargs):
        return jsonify([t.name for t in Thread.select(Thread.q.serviceID == service.id)])
    index.expose_resource = True

    def delete(self,service):
        name = service.name
        service.destroySelf()
        broadcast_event("service_deleted",dict(service=name))
        hub.commit()
        return "ok"
    delete.expose_resource = True

    def update(self,service):
        return "ok"
    update.expose_resource = True


class ThreadController(RESTResource):
    def REST_instantiate(self,name,**kwargs):
        try:
            service = self.parents[0]
            t = Thread.select(AND(Thread.q.name == name, Thread.q.serviceID == service.id))[0]
            return t
        except:
            return None

    def REST_create(self,name,**kwargs):
        service = self.parents[0]
        t = Thread(service=service,name=name)
        broadcast_event("thread_created",dict(service=service.name,name=name))
        hub.commit()
        return t

    def index(self,thread,**kwargs):
        return jsonify([c.as_dict() for c in thread.get_comments()])
    index.expose_resource = True

    def delete(self,thread):
        for c in thread.get_comments():
            c.delete()
        thread.destroySelf()
        broadcast_event("thread_deleted",dict(service=self.parents[0].name,name=thread.name))
        hub.commit()
        return "ok"
    delete.expose_resource = True

    def update(self,thread):
        return "ok"
    update.expose_resource = True

    def reply(self,thread,subject="",body="",reply_to="0",author_id="",author_email="",
              author_url="",author_ip="",author_name=""):
        c = Comment(thread=thread,subject=subject,body=body,reply_to=int(reply_to),author_id=author_id,
                    author_email=author_email,author_url=author_url,author_ip=author_ip,
                    author_name=author_name)
        broadcast_event("reply_to_thread",dict(thread=thread.name,subject=subject,body=body,
                                               reply_to=reply_to,author_id=author_id,
                                               author_email=author_email,author_url=author_url,
                                               author_name=author_name,
                                               author_ip=author_ip,service=thread.service.name))
        hub.commit()
        return str(c.id)
    reply.expose_resource = True


class CommentController(RESTResource):
    def REST_instantiate(self,id,**kwargs):
        try:
            c = Comment.get(id)
            return c
        except:
            return None

    def REST_create(self,id,**kwargs):
        """ can't do this """
        return None

    def index(self,comment,**kwargs):
        return jsonify(comment.as_dict())
    index.expose_resource = True

    def delete(self,comment):
        comment.delete()
        broadcast_event("comment_deleted",dict(thread=comment.thread.name, service=comment.thread.service.name,
                                               subject=comment.subject,body=comment.body,
                                               reply_to=comment.reply_to,author_id=comment.author_id,
                                               author_email=comment.author_email,author_url=comment.author_url,
                                               author_name=comment.author_name,
                                               author_ip=comment.author_ip))
        hub.commit()
        return "ok"
    delete.expose_resource = True

    def update(self,comment,**kwargs):
        return self.reply(comment,**kwargs)
    update.expose_resource = True

    def reply(self,comment,subject="",body="",author_id="",author_email="",
              author_url="",author_ip="",author_name=""):
        c = Comment(thread=comment.thread,subject=subject,body=body,reply_to=comment.id,
                    author_id=author_id,author_email=author_email,
                    author_url=author_url,author_ip=author_ip,author_name=author_name)
        broadcast_event("reply_to_comment",dict(thread=comment.thread.name,subject=subject,body=body,
                                                reply_to=comment.id,author_id=author_id,
                                                author_email=author_email,author_url=author_url,
                                                author_name=author_name))
        hub.commit()
        return str(c.id)
    reply.expose_resource = True



