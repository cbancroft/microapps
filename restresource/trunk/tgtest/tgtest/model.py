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
    w = DateTimeCol()
    
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
    enum = EnumCol(enumValues=('enumX', 'enumY', 'enumZ'), default='enumX')
    floater = FloatCol(default=0)
    #not testing BLOBCol,PickleCol for now
    
