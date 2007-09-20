from sqlobject import *

from turbogears.database import PackageHub

hub = PackageHub("gild")
__connection__ = hub

# class YourDataClass(SQLObject):
#     pass

