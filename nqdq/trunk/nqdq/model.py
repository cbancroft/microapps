from sqlobject import *
from turbogears.database import PackageHub
from datetime import datetime

hub = PackageHub("nqdq")
__connection__ = hub

soClasses = ["Service","Q","Item"]

class Service(SQLObject):
    name = UnicodeCol(alternateID=True)

class Q(SQLObject):
    service = ForeignKey('Service',cascade=True)
    name = UnicodeCol(alternateID=True)
    items = MultipleJoin('Item',orderBy="added",joinColumn="queue_id")

    def push(self,value=""):
        max = 0
        if len(self.items):
            max = self.items[-1].added
        i = Item(queue=self,value=value,added=max + 1)

    def unshift(self,value=""):
        min = 0
        if len(self.items):
            min = self.items[0].added
        i = Item(queue=self,value=value,added=min - 1)

class Item(SQLObject):
    queue = ForeignKey('Q',cascade=True)
    value = UnicodeCol(default="")
    added = IntCol(default=0)


        

	  

	  

