from turbogears.database import PackageHub
from sqlobject import *
from sqlobject.inheritance import InheritableSQLObject

hub = PackageHub("tgtest")
__connection__ = hub

class Parent(InheritableSQLObject):
    x = IntCol()
    y = IntCol()

class Child1(Parent):
    z = IntCol()

class Child2(Parent):
    q = DateTimeCol()
    
class FieldTypes(SQLObject):
    utf = UnicodeCol(length=255)
    currency = CurrencyCol(default=1234)
    truefalse = BoolCol(default=True)
    x = IntCol()
    string = StringCol(default = "defaultstringval")
    datetime = DateTimeCol()
    date = DateCol()
    decimal = DecimalCol(size=4, precision=2)
    foreign = ForeignKey("Child1")
    #not testing BLOBCol,PickleCol for now
    
