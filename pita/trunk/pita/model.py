from sqlobject import *
from turbogears.database import PackageHub

hub = PackageHub("pita")
__connection__ = hub

soClasses = ['Service','Item']

class Service(SQLObject):
    name = UnicodeCol(alternateID=True)

class Item(SQLObject):
    name = UnicodeCol()
    value = UnicodeCol(default="")
    service = ForeignKey('Service',cascade=True)
