from turbogears import controllers, expose
from model import *
# import logging
# log = logging.getLogger("tgtest.controllers")

import sys
sys.path.insert(0,'..')

from restresource.crud import *
from restresource import *

class ParentController(CrudController,RESTResource):
    crud = SOController(Parent)
    
class Child1Controller(CrudController,RESTResource):
    crud = SOController(Child1)
    
class Child2Controller(CrudController,RESTResource):
    crud = SOController(Child2)
    
class FieldTypesController(CrudController,RESTResource):
    crud = SOController(FieldTypes)
    

class Root(RESTResource,controllers.RootController):

    child1 = Child1Controller()
    child1.REST_children = {'fieldtypes':FieldTypesController()}
    child2 = Child2Controller()
    
    @expose(template="tgtest.templates.welcome")
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Responding For Duty")
        return dict(now=time.ctime())
