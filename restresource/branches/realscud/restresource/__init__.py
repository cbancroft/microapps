"""
restresource

cherrypy controller mixin to make it easy to build REST applications.

handles nested resources and method-based dispatching.

here's a rough sample of what a controller would look like using this:

cherrypy.root = MainController()
cherrypy.root.user = UserController()

class PostController(RESTResource):
    def read(self,post):
        return post.as_html()
    read.expose_resource = True

    def delete(self,post):
        post.destroySelf()
        return "ok"
    delete.expose_resource = True

    def update(self,post,title="",body=""):
        post.title = title
        post.body = body
        return "ok"
    update.expose_resource = True

    def create(self, post, title="", body="")
        post.title = title
        post.body = body
        return "ok"
    create.expose_resource = True

    def REST_instantiate(self, slug, **kwargs):
        try:
            user = self.parents[0]
            return Post.select(Post.q.slug == slug, Post.q.userID = user.id)[0]
        except:
            return None

    def REST_create(self, slug, **kwargs):
        user = self.parents[0]
        return Post(slug=slug,user=user)

class UserController(RESTResource):
    REST_children = {'posts' : PostController()}

    def read(self,user):
        return user.as_html()
    read.expose_resource = True

    def delete(self,user):
        user.destroySelf()
        return "ok"
    delete.expose_resource = True

    def update(self,user,fullname="",email=""):
        user.fullname = fullname
        user.email = email
        return "ok"
    update.expose_resource = True

    def create(self, user, fullname="", email=""):
        user.fullname = fullname
        user.email = email
        return "ok"
    create.expose_resource = True

    def extra_action(self,user):
        # do something else
    extra_action.expose_resource = True

    def REST_instantiate(self, username, **kwargs):
        try:
            return User.byUsername(username)
        except:
            return None

    def REST_create(self, username, **kwargs):
        return User(username=username)

then, the site would have urls like:

    /user/bob
    /user/bob/posts/my-first-post
    /user/bob/posts/my-second-post
    /user/bob/extra_action

which represent REST resources. calling 'GET /usr/bob' would call the read() method on UserController
for the user bob. 'PUT /usr/joe' would create a new user with username 'joe'. 'DELETE /usr/joe'
would delete that user. 'GET /usr/bob/posts/my-first-post' would call read() on the Post Controller
with the post with the slug 'my-first-post' that is owned by bob.


"""

import cherrypy

def strip_empty(path):
    return [e for e in path if e != ""]

class RESTResource:
    # default method mapping. ie, if a GET request is made for
    # the resource's url, it will try to call an read() method (if it exists);
    # if a PUT request is made, it will try to call an create() method.
    # if you prefer other method names, just override these values in your
    # controller with REST_map
    REST_defaults = {'DELETE' : 'delete',
                     'GET' : 'read',
                     'POST' : 'update',
                     'PUT' : 'create'}
    REST_map = {}
    # if the resource has children resources, list them here. format is
    # a dictionary of name -> resource mappings. ie,
    #
    # REST_children = {'posts' : PostController()}

    REST_children = {}

    parents = []

    REST_content_types = {}
    REST_default_content_type = ""

    # REST_ids_are_root
    # 'params' are parameters in a URI separated by ;'s
    # They can represent ids or methods/objects
    # Sample REST_ids_are_root=False uri (better for resource 'context' using /'s)
    # /col;4/edit_form
    # Sample REST_ids_are_root=True uri (same as wsgiCollection)
    # /col/4;edit_form

    REST_ids_are_root = True

    def CT_dispatch(self,d):
        method = cherrypy.request.method
        if method != 'GET':
            return d
        if cherrypy.request.headerMap.has_key('Accept'):
            accept = cherrypy.request.headerMap['Accept']
            if self.REST_content_types.has_key(accept):
                m = self.REST_content_types[accept]
                if hasattr(self,m):
                    cherrypy.response.headerMap['Content-Type'] = accept
                    return getattr(self,m)(d)
        # use the default content type
        if self.REST_default_content_type != "":
            if self.REST_content_types.has_key(self.REST_default_content_type):
                m = self.REST_content_types[self.REST_default_content_type]
                if hasattr(self,m):
                    cherrypy.response.headerMap['Content-Type'] = self.REST_default_content_type
                    return getattr(self,m)(d)
        # something's wrong with the default type. let's just return the data
        # without doing anything
        return d

    def REST_dispatch(self, resource, resource_params, **params):
        # if this gets called, we assume that default has already
        # traversed down the tree to the right location and this is
        # being called for a raw resource
        #
        # resource_params here is used for dispatching to a
        # method-resource_param-based function.  ??still good idea?
        method = cherrypy.request.method

        param_method = None
        if resource_params:
            param_method = method.lower() + '_' + resource_params.pop(0)

        if param_method and hasattr(self,param_method):
            m = getattr(self,param_method)

        elif self.REST_map.has_key(method):
            m = getattr(self,self.REST_map[method])
        elif self.REST_defaults.has_key(method):
            m = getattr(self,self.REST_defaults[method])

        if m and getattr(m, "expose_resource"):
            return m(resource,*resource_params,**params)

        raise cherrypy.NotFound

    def parse_resource_token(self,token):
        resource_params = token.split(';')
        resource_name = resource_params.pop(0)
        return (resource_name,resource_params)

    @cherrypy.expose
    #/child1/5/fieldtypes
    #child1;5/fieldtypes
    #child1/5
    #child1/;add_form
    #child1/add_form
    def default(self, *vpath, **params):
        """This method will get called by default by CherryPy when it can't
        map an object path directly (a.b.c for request /a/b/c) which if we have
        RESTful urls (interspersed with id's) will be most of the time.

        Before this would only be inherited by sub-Root controllers, but to handle
        situations like /a;1/ or /a;add_form it needs to be sub-classed by the
        Root Controller now.

        So default() now simply handles one token between /'s and other
        methods dispatch handling

        * pass resource to sub-object (update obj.parents first)
        * call local method
        * getresource(id)
        * continue down vpath
        """
        #resource_id = None
        resource_name = None
        resource_params = list() #anything between ;'s
        #this stays in default()
        if vpath:
            # Make a copy of vpath in a list
            vpath = list(vpath)
            # strip out any empty elements from the path
            # this can happen if there's a // in the url
            vpath = strip_empty(vpath)
            (rname,rparams) = self.parse_resource_token(vpath.pop(0))
            return self.map_vpath([],rname,rparams,vpath,params)
            #.split(';')
            #resource_name = resource_params.pop(0)
            #if vpath and vpath[0].startswith(';'):
            #    resource_params.extend(vpath.pop(0).split(';')[1:])

        #elif ....
        # i guess we should try to find index() or something METHOD-based?


        else:
            raise cherrypy.NotFound

    def collection_dispatcher(self,myname,resource_params,vpath,params):
        # coming in, vpath has already consumed the top-most resource
        # resource_params will turn into the 'params' that affect function/object dipatch
        # 

        #probably only ever one resource, but I need to distinguish between
        #None and Nothing
        resources = [] 

        if resource_params:
            if not REST_ids_are_root:
                resources.append(self.getresource(resource_params, params))
            #else:
            #   ?should we dispatch using the parameters
            #    even if there is more vpath?
        if vpath:
            (rname,rparams) = self.parse_resource_token(vpath.pop(0))
            if REST_ids_are_root:
                if rname:
                    #rname is an id
                    resources.append(self.getresource((rname), params))
                    rname = None
                #for urls like: /col/id;edit_form
                #here we're conscious making this equivalent to
                #the much stranger: /col;edit_form/id
                resource_params.extend(rparams)
                if vpath:
                    (rname,rparams) = self.parse_resource_token(vpath.pop(0))

            elif not REST_ids_are_root and not rname and rparams:
                #url like: /col/;id
                #rparams are ids
                resources.append(self.getresource(rparams, params))
                #corner case: multiple resources could get added in
                #  a url like: /col;1/;2  Is that good or bad?
                if vpath:
                    (rname,rparams) = self.parse_resource_token(vpath.pop(0))
                    
            if rname:
                return self.map_vpath(resources,rname,rparams,vpath,params)
            else:
                #urls like: /col/id/;edit_form AND /col/;add_form
                #corner case: if /col/;1/;2 then ';2' might get lost here
                resource_params.extend(rparams)

        #if we get here, vpath is exhausted
        #so either rest_dispatch or col_dispatch
        if resource:
            return self.REST_dispatch()
        else:
            return self.REST_collection_dispatch(rparams)
            #still outstanding:
            # if REST_ids_are_root and not resource, then resource_params might have dispatch info
            #   and if rname or rparams (had vpath) then that might dispatch to function or object
            # if not REST_ids_are_root
            #   if rname then  dispatch to function/obj
            #   else if vpath(after pop)

            
                
            if rname or rparams:
                #cases: terminally use (rname,rparams) for dispatch OR more vpath 
                #if we've still got something left
                #map_vpath()

        #optiosn:
        # rest_dispatch
        # collection_dispatch
        # object_dispatch

        #terminal location
        if resource:
            
            #rname,rparams could still be about the next resource child    
            #else:
            #    rparams.insert(0,rname)
                

            #?what happens to rname/rparams?
        if not vpath and resource:
            #rest dispatch
        else:
            #map_vpath(resource_params,vpath)
            #if no more vpath, then use resource_params to col_dispatch
            #

        if vpath:
            #return map_vpath(resource)
            #add resource to child
        else:
            #rest dispatch


                

        ##OLD code
        if not resource_id:
            #we don't have an id, so it's either the collection
            #OR we want to pass handling to the collection object to
            #figure it out.
            ##this means the request is connected to the collection
            ##rather than a resource member
            collection_method = cherrypy.request.method.lower()
            #if there's a method POST, PUT, etc call that
            #this is for the collection, not the resource
            if resource_params:
                param_method = '_'.join((collection_method,
                                         resource_params.pop(0) ))
                if hasattr(self,param_method):
                    collection_method = param_method
            m = getattr(self, collection_method, self.list)
            return self.CT_dispatch(m(*resource_params, **params))

        # Coerce the ID to the correct db type
        resource = self.getresource(resource_id,params,resource_params)
        
        # There may be further virtual path components.
        # Try to map them to methods in children or this class.
        if vpath:
            return self.map_vpath(resource,resource_params,vpath,params)
        # No further known vpath components. Call a default handler
        # based on the method
        return self.CT_dispatch(self.REST_dispatch(resource,resource_params,**params))
            

    def getresource(self,resource_params,params):
        """not doing anything with resource_params
        this could in theory be sent along to REST_* functions
        it is named without an '_' to avoid clobber from a '/col/;resource' hook
        """
        resource = self.REST_instantiate(resource_params[0], **params)
        if resource is None:
            if cherrypy.request.method in ["PUT","POST"]:
                # PUT and POST can be used to create a resource
                resource = self.REST_create(resource_params[0], **params)
            else:
                raise cherrypy.NotFound
        return resource


    def map_vpath(self,resources,a,rparams,vpath,params):
        #resources is an array
        #its needed here, just to append to the getobj
        #so maybe resources doesn't belong in this part?
        #'a' will be a collection or a function
        #(a,rparams) = self.parse_resource_token(vpath.pop(0))

        obj = None
        if self.REST_children.has_key(a):
            obj = self.REST_children[a]
        elif isinstance(getattr(self,a,None), RESTResource):
            obj = getattr(self,a)

        if obj:
            obj.parents = [p for p in self.parents]
            obj.parents.extend(resources)
            return obj.collection_dispatcher(a,rparams,vpath,params)
            
        #?do i need an 'if resources' here?
        method = getattr(self, a, None)
        if method and getattr(method, "expose_resource"):
            return self.CT_dispatch(method(resources[0], *vpath, **params))
        else:
            # path component was specified but doesn't
            # map to anything exposed and callable
            raise cherrypy.NotFound

    def REST_instantiate(self, id, *params, **kwargs):
        """ instantiate a REST resource based on the id

        this method MUST be overridden in your class. it will be passed
        the id (from the url fragment) and should return a model object
        corresponding to the resource.

        if the object doesn't exist, it should return None rather than throwing
        an error. if this method returns None and it is a PUT request,
        REST_create() will be called so you can actually create the resource.
        """
        raise cherrypy.NotFound

    def REST_create(self, id, *params, **kwargs):
        """ create a REST resource with the specified id

        this method should be overridden in your class.
        this method will be called when a PUT request is made for a resource
        that doesn't already exist. you should create the resource in this method
        and return it.
        """
        raise cherrypy.NotFound

