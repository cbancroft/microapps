from sqlobject import *
from turbogears.database import PackageHub
from restclient import rest_invoke
from threading import Thread

soClasses=["Service","Event","Handler"]

hub = PackageHub("pebble")
__connection__ = hub

class Service(SQLObject):
    name = UnicodeCol(alternateID=True,default=u"")
    events = MultipleJoin('Event')

class Event(SQLObject):
    service = ForeignKey('Service',cascade=True)
    name = UnicodeCol(default="")
    handlers = MultipleJoin('Handler')

class Handler(SQLObject):
    event = ForeignKey('Event',cascade=True)
    url = UnicodeCol(default=u"")
    method = UnicodeCol(default=u"POST")

    def handle(self,params):
        """ make the necessary request in response to the event being triggered """
        rest_invoke(self.url,method=self.method,params=params,async=True)


