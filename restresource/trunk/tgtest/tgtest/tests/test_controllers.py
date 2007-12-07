from turbogears import testutil
from tgtest.controllers import Root
from tgtest.model import Parent,Child1,Child2,FieldTypes
import cherrypy
import cStringIO as StringIO

cherrypy.root = Root()
def createTables():
    Parent.createTable(ifNotExists=True)
    Child1.createTable(ifNotExists=True)
    Child2.createTable(ifNotExists=True)
    FieldTypes.createTable(ifNotExists=True)

def dropTables():
    Parent.dropTable(ifExists=True)
    Child1.dropTable(ifExists=True)
    Child2.dropTable(ifExists=True)
    FieldTypes.dropTable(ifExists=True)

createTables()

def test_method():
    "the index method should return a string called now"
    import types
    result = testutil.call(cherrypy.root.index)
    assert type(result["now"]) == types.StringType

def test_indextitle():
    "The indexpage should have the right title"
    testutil.createRequest("/")
    assert "<title>Welcome to TurboGears</title>" in cherrypy.response.body[0]

def test_child1():
    testutil.createRequest("/child1/",method="GET")
    assert "<th>x</th>" in cherrypy.response.body[0]
    assert "<th>y</th>" in cherrypy.response.body[0]
    assert "<th>z</th>" in cherrypy.response.body[0]
    assert "<th>childName</th>" not in cherrypy.response.body[0]

def test_child2():
    testutil.createRequest("/child2/",method="GET")
    assert "<th>x</th>" in cherrypy.response.body[0]
    assert "<th>y</th>" in cherrypy.response.body[0]
    assert "<th>w</th>" in cherrypy.response.body[0]
    assert "<th>childName</th>" not in cherrypy.response.body[0]

def test_child1_create():
    testutil.createRequest("/child1/",
                           method="POST",
                           rfile=StringIO.StringIO('x=1&y=2&z=3'))

    #print cherrypy.response.body[0]
    assert "ok" in cherrypy.response.body[0]

def test_fieldtypes_child():
    testutil.createRequest("/child1/1/fieldtypes/",method="GET")
    assert "<th>utf</th>" in cherrypy.response.body[0]
    assert "<th>currency</th>" in cherrypy.response.body[0]
    assert "<th>truefalse</th>" in cherrypy.response.body[0]
    assert "<th>x</th>" in cherrypy.response.body[0]
    assert "<th>string</th>" in cherrypy.response.body[0]
    assert "<th>datetime</th>" in cherrypy.response.body[0]
    assert "<th>date</th>" in cherrypy.response.body[0]
    assert "<th>decimal</th>" in cherrypy.response.body[0]
    assert "<th>enum</th>" in cherrypy.response.body[0]
    assert "<th>floater</th>" in cherrypy.response.body[0]
    assert "<th>foreignID</th>" in cherrypy.response.body[0]

def test_fieldtypes_create():
    testutil.createRequest("/child1/1/fieldtypes",
                           method="POST",
                           rfile=StringIO.StringIO("utf=asdf&currency=2.23&truefalse=on&x=90&string=happyjoy&datetime=2007/1/26 16:12&date=1/26/2007&decimal=1.1&enum=enumY&floater=2.2"))
    #print cherrypy.response.body[0]
    assert "ok" in cherrypy.response.body[0]

def test_fieldtypes_errorhandle():
    """currency will be a string.  Should return the form"""
    testutil.createRequest("/child1/1/fieldtypes/",
                           method="POST",
                           rfile=StringIO.StringIO("utf=asdf&currency=NOT_A_CURRENCY&truefalse=on&x=90&string=happyjoy&datetime=2007/1/26 16:12&date=1/26/2007&decimal=1.1&enum=enumY&floater=2.2"))
    assert "Please enter a number" in cherrypy.response.body[0]

def test_fieldtypes_create_confirm():
    testutil.createRequest("/child1/1/fieldtypes/1/",method="GET")
    print cherrypy.response.body[0]
    #foreignID
    assert "<td>1</td>" in cherrypy.response.body[0]
    #utf
    assert "<td>asdf</td>" in cherrypy.response.body[0]
    #currency
    assert "<td>2.23</td>" in cherrypy.response.body[0]
    #truefalse
    assert "<td>True</td>" in cherrypy.response.body[0]
    #x
    assert "<td>90</td>" in cherrypy.response.body[0]
    #string
    assert "<td>happyjoy</td>" in cherrypy.response.body[0]
    #datetime
    assert "<td>2007-01-26 16:12:00</td>" in cherrypy.response.body[0]
    #date
    assert "<td>2007-01-26</td>" in cherrypy.response.body[0]
    #decimal
    assert "<td>1.1</td>" in cherrypy.response.body[0]
    #float
    assert "<td>2.2</td>" in cherrypy.response.body[0]
    #enum
    assert "<td>enumY</td>" in cherrypy.response.body[0]
    
