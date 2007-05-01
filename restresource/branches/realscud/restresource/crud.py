import cherrypy
from turbogears import expose, redirect #, controllers
from turbogears import validate, validators, error_handler #,flash
from turbogears.widgets import *

import sqlobject


"""
restresource.crud

RESTful CRUD (Create,Read,Update,Delete) implementation for
Turbogears, particularly for SQLObject
This aids in rapid development of basic CRUD functionality with TG

explicitly, 'from restresource.crud import *' gives you:
  class CrudController
  class SOController: a sql object controller

The important thing here is that we get sane defaults for viewing/posting/form creation
and the template functions (which are decorated) are separated from the
functions decorated for form validation and security.  This is basically a work around
for expose() needing to be the 'final decorator' which makes it difficult to set security
from defaults.

The main thrust, is I get started right away, and I don't waste time at the beginning or
even the end with adding, for example, delete functionality, when all I want to do is
set the rights required to delete.

---------WITH EXAMPLE MODEL.PY------
class PerformedTest(History):
    #History is an InheritableSQLObject also defined
    x = IntCol()
    y = IntCol()
    testDetails = UnicodeCol(length=255)
    testNumber = IntCol()

#class User is the default from TG

---------WITH EXAMPLE CONTROLLERS.PY------

from restresource import *
from restresource.crud import *

class TestController(CrudController,RESTResource):
    #This is all that's really necessary!
    #'crud' is a magic word.  You must use 'crud' as the variable
    crud = SOController(PerformedTest)

#here we set the security without changing the templates, etc.
class UserController(CrudController,RESTResource):
    crud = SOController(User)
    crud.create = identity.require(identity.in_any_group('class_account','professor'))(crud.create)
    crud.read = identity.require(identity.not_anonymous())(crud.read)

    crud.update = identity.require(identity.has_permission('modify'))(crud.update)
    crud.delete = identity.require(identity.has_permission('modify'))(crud.delete)

    #replacing the template
    #you could also replace the whole function here, if desired.
    @expose(template='kid:myproject.templates.view')
    def read(self, *p,**kw):
        return self.crud.read(self, *p,**kw)
    read.expose_resource = True

    
class Root(controllers.RootController):

    user = UserController()
    test = TestController()

--- Features ---
* Supports SQLObject inheritance

----TODO ----
* Not all Column types are supported.  I'm adding them as I encounter them

---Design Notes---
* We want the programmer to be able to decorate the functions in SOController()
  (that's the whole point).  If they are class methods (instead of staticmethods), then
  they can only be overridden by subclassing.  Thus, they're all static methods, assuming
  they're called from something inheriting from CRUDController, able to 'find itself' at
  self.crud

* Since the chief point of this library is to separate the @expose decorator from the
  other security/validation decorators, we can wonder whether some modification to
  cherrypy would remove this issue (e.g. exposed functions being a separate set() on the Controller
                                    class, perhaps)


"""

#GLUE SQLObject and Widgets/Validators
def _soc_default_SOUnicodeCol(f):
    return TextField(name=f,)

def _soc_default_SODateCol(f):
    return CalendarDatePicker(name=f, validator=validators.DateConverter())

def _soc_default_SODateTimeCol(f):
    return CalendarDateTimePicker(name=f, validator=validators.DateTimeConverter())

def _soc_default_SOForeignKey(f):
    return HiddenField(name=f,)

def _soc_default_SOBoolCol(f):
    return CheckBox(name=f,)

def _soc_default_SOIntCol(f):
    return TextField(name=f, validator=validators.Int())

def _soc_default_Number(f):
    return TextField(name=f, validator=validators.Number())

#turbogears manual: widgets: p316,320, SOcolumns: p46
_soc_table_so_mapper = dict( [
    (sqlobject.col.SOUnicodeCol,_soc_default_SOUnicodeCol),
    (sqlobject.col.SOStringCol,_soc_default_SOUnicodeCol),
    (sqlobject.col.SODateTimeCol,_soc_default_SODateTimeCol),
    (sqlobject.col.SODateCol,_soc_default_SODateCol),
    (sqlobject.col.SOForeignKey,_soc_default_SOForeignKey),
    (sqlobject.col.SOBoolCol,_soc_default_SOBoolCol),
    (sqlobject.col.SOIntCol,_soc_default_SOIntCol),
    (sqlobject.col.SODecimalCol,_soc_default_Number),
    (sqlobject.col.SOCurrencyCol,_soc_default_Number),
    ] )

def _soc_getColumns(soObj):
    columns = {}
    for x in soObj.__mro__:
        y = x.sqlmeta.columns.items()
        if len(y) == 0: break
        columns.update(y)
    #childName is a reserved column for SO inheritance
    if 'childName' in columns:
        del columns['childName']
    return columns

def _soc_2_dict(soObj, **kw):
    soDict = dict()
    for f,v in _soc_getColumns(type(soObj)).items():
        soDict[f]=getattr(soObj,f,None)
        if type(v)==sqlobject.col.SOForeignKey:
            field_sansID = f[:-2]
            field_val = getattr(soObj,field_sansID,None)
            if field_val is not None:
                soDict[field_sansID] = _soc_2_dict(field_val)
            else:
                soDict[field_sansID] = None

    soDict['id'] = soObj.id
    for k in kw:
        soDict[k] = kw[k]
    return soDict


class SOController:
    """

    """
    soClass = None
    model_form = lambda self: self.crud._get_form()
    _soc_model_form = None

    def __init__(self,soClass):
        self.soClass = soClass
        
    #these get instantiated by _get_form()
    #they do NOT get instantiated on an SOController() instantiation
    def form_fields(self):
        """return a dictionary of fields from self.soClass to build the FormFields
        Widget object.  This should be overridden if your form does not directly
        correspond to the SQLObject columns list.
        """
        field_dict=dict()

        for f,fclass in _soc_getColumns(self.soClass).items():
            field_dict[f]= _soc_table_so_mapper[type(fclass)](f)

        return field_dict
    
    def form(self,form_cls):
        #override at will
        pass

    def _get_form(self):
        if self._soc_model_form is not None:
            return self._soc_model_form

        #we have to sneak around WidgetsList's 'syntactic sugar' class declaration here
        FormFields = type('FormFields', (WidgetsList,), self.form_fields())
        class Form(TableForm):
            #__metaclass__ = _Form
            pass

        #problem: what if you don't want to inherit from WidgetsList?
        #it's tempting to put these classes right in SOController
        #classes FormFields and Form would go here
        
        #local decorators
        #self.form_fields(FormFields)
        self.form(Form)
        fields = FormFields()

        self._soc_model_form = Form(fields=fields, action="./")

        return self._soc_model_form

    @staticmethod
    def edit_form(self, table, tg_errors=None, **kwargs):
        return dict(record = table,
                    record_dict = _soc_2_dict(table), #_soc_getColumns(type(table)).keys(),
                    columns=_soc_getColumns(self.crud.soClass).keys(),
                    form = self.crud._get_form(),
                    error=tg_errors,
                    )

    @staticmethod
    def add_form(self, tg_errors=None, **kwargs):
        return dict(form = self.crud._get_form(),
                    columns=_soc_getColumns(self.crud.soClass).keys(),
                    error=tg_errors,
                    )

    def _update_error(self, *pargs, **kwargs):
        #magically, 'self' is CrudController here
        #don't ask me why! ask error_handler!
        return self.get_edit_form(*pargs, **kwargs)

    def _create_error(self, *pargs, **kwargs):
        #magically, 'self' is CrudController here
        #don't ask me why! ask error_handler!
        return self.get_add_form(**kwargs)

    @staticmethod
    @validate(form=model_form)
    @error_handler(_create_error)
    def create(self, table, **kw):
        #parents may provide foreignKey values
        if len(self.parents) > 0:
            #update %kw from parents higher up in URL
            parentDict = dict([(p.sqlmeta.table, p.id) for p in self.parents])
            for c,t in _soc_getColumns(self.crud.soClass).items():
                if type(t)==sqlobject.col.SOForeignKey and t.foreignKey.lower() in parentDict:
                    kw[c] = parentDict[t.foreignKey.lower()]

        if table is None:
            table = self.crud.soClass(**kw)
        else:
            table.set(**kw)
        table._connection.commit()
        return "ok"

    @staticmethod
    def read(self,table,**kw):
        return dict(record=table,
                    columns=_soc_getColumns(type(table)).keys(),
                    ) #_soc_2_dict(table),i=table)

    @staticmethod
    @validate(form=model_form)
    @error_handler(_update_error)
    def update(self,table,**kw):
        if table is None:
            table = self.crud.soClass(**kw)
        else:
            table.set(**kw)
        table._connection.commit()
        return "ok"
    
    @staticmethod
    def delete(self,table):
        table.destroySelf()
        return "ok"

    @staticmethod
    def list(self, **kw):
        """what is called for /foo instead of /foo/2 """
        #if cherrypy.request.method == 'POST':
        #    return self.create(None,**kw)
        #if 'add_form' in kw:
        #    return self.add_form(**kw)

        return self.search(**kw)
     
    @staticmethod
    def search(self, **kw):
        results = iter(self.crud.soClass.selectBy(**kw))
        def dict_records():
            for r in results:
                yield _soc_2_dict(r)
        return dict(members=[r for r in results] ,#list(dict_records()),
                    columns=_soc_getColumns(self.crud.soClass).keys())



class CrudController:
    """inherited by a CherryPy controller, this depends on a 'crud'
    attribute to do the real work.  This layer should be decorated
    with templates.  The corresponding crud functions should be
    decorated with security/identity/validation/error_handler wrappers.

    When overriding these methods, you will often just copy this version
    to get started.
    """
    def REST_instantiate(self, id, **kwargs):
        try:
            #user = self.parents[0]
            return self.crud.soClass.get(id)
        except:
            return None

    def REST_create(self, **kwargs):
        """Create class here only if there are inherited values
           (e.g. from parent controllers perhaps)"""
        return None

    @expose(template='kid:restresource.templates.add')
    def get_add_form(self, **kw):
        return self.crud.add_form(self,**kw)

    @expose(template='kid:restresource.templates.edit')
    def get_edit_form(self, table, **kw):
        return self.crud.edit_form(self,table,**kw)
    get_edit_form.expose_resource = True

    @expose(template='kid:restresource.templates.view')
    @expose(template='json', accept_format='text/javascript')
    def read(self,table,**kw):
        if 'edit_form' in kw:
            return self.edit_form(table, **kw)
        return self.crud.read(self,table,**kw)
    read.expose_resource = True

    def post(self,**kw):
        """when a post goes directly to /col/"""
        return self.crud.create(self,self.REST_create(**kw),**kw)

    def create(self,table,**kw):
        return self.crud.create(self,table,**kw)
    create.expose_resource = True

    def delete(self,table,**kw):
        return self.crud.delete(self,table,**kw)
    delete.expose_resource = True

    def update(self,table,**kw):
        return self.crud.update(self,table,**kw)
    update.expose_resource = True

    @expose(template='kid:restresource.templates.list')
    @expose(template='json', accept_format='text/javascript')
    def search(self,*p,**kw):
        return self.crud.search(self,*p,**kw)
    search.expose_resource = True

    def list(self,*p,**kw):
        return self.crud.list(self,*p,**kw)
    list.expose_resource = True


    
