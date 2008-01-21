from gravel.dec import wsgiapp

@wsgiapp
def app(req):
    store = req.store
    next = req.path_info_peek()
    req.app_root = req.application_url + '/'
    if req.method == 'POST':
        return post_event
    elif req.method == 'GET':
        return get_event
    elif req.method == 'PUT':
        return put_event
    elif req.method == "DELETE":
        return delete_event

@wsgiapp
def put_event(req):
    return res

@wsgiapp
def get_event(req):
    return res

@wsgiapp
def delete_event(req):
    return res

@wsgiapp
def post_event(req):
    return res



@wsgiapp
def service_page(req):
    return "This is Gravel"
