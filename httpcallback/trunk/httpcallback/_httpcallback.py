"""
Reference Implementation of HTTPCallback

see http://microapps.org/HTTPCallback
"""

# TODO:
#   * URI Templating
#   * from_wsgi_environ

from simplejson import loads, dumps
import urllib, sys, cStringIO, re

class HTTPCallback(object):
    """
    Instantiate a basic HTTPCallback object:
    
    >>> jr = HTTPCallback(url="http://www.example.com/")
    >>> jr.url
    'http://www.example.com/'

    method should default to GET

    >>> jr.method
    'GET'

    body defaults to an empty string

    >>> jr.body
    ''

    queryString defaults to an empty string

    >>> jr.queryString
    ''

    username and password default to empty strings
    >>> jr.username
    ''
    >>> jr.password
    ''

    headers and params default to empty arrays

    >>> jr.headers
    []
    >>> jr.params
    []

    redirections defaults to 5 and follow_all_redirects to False
    >>> jr.redirections
    5
    >>> jr.follow_all_redirects
    False

    version defaults to "0.1" (HTTPCallback's current version)
    >>> jr.version
    '0.1'

    kwargs = defaults to an empty dict
    >>> jr.kwargs
    {}

    """
    def __init__(self,url="",method="GET",sendContent="",body="",queryString="",username="",password="",
                 headers=None,params=None,redirections=5,follow_all_redirects=False,version="0.1",**kwargs):
        if headers is None:
            headers = []
        if params is None:
            params = []
        self.url                  = url
        self.method               = method

        """ Either 'body' or 'sendContent' may be specified. Internally, it's normalized to
        'body' and that takes precedent. 'sendContent' is allowed for compatability with
        mochikit's XHR objects but will be lost if body is specified as well. 

        >>> jr = HTTPCallback(url="http://www.example.com/",body="foo")
        >>> jr.body
        'foo'
        >>> jr = HTTPCallback(url="http://www.example.com/",sendContent="foo")
        >>> jr.body
        'foo'
        >>> jr = HTTPCallback(url="http://www.example.com/",body="foo",sendContent="bar")
        >>> jr.body
        'bar'


        """
        self.body                 = body or sendContent

        self.queryString          = queryString
        self.username             = username
        self.password             = password


        """
        Headers may be specified either as a list of 2-arrays (or tuples), or as a dictionary. If passed
        as a dictionary, they will be normalized to a list or lists. 

        >>> jr = HTTPCallback(url="http://www.example.com/",headers=[["content-type","text/html"],["x-foo","foo"]])
        >>> jr.headers
        [['content-type','text/html'],['x-foo','foo']]
        >>> jr = HTTPCallback(url="http://www.example.com/",headers={"content-type" : "text/html", "x-foo" : "foo"})
        >>> jr.headers.length
        2
        >>> ['content-type','text/html'] in jr.headers
        True
        >>> ['x-foo','foo'] in jr.headers
        True

        tuples are allowed too but get converted to lists automatically:
        
        >>> jr = HTTPCallback(url="http://www.example.com/",headers=[("content-type","text/html"),("x-foo","foo")])
        >>> jr.headers
        [['content-type','text/html'],['x-foo','foo']]

        """
        if type(headers) == type({}):
            headers = list(headers.iteritems())
        
        self.headers              = [list(t) for t in headers]

        """ similar deal with params. can be either a list of 2-arrays or tuples, or a dictionary. Normalizes
        to list of lists.

        Dictionaries are allowed on these just because they're often very convenient to generate. If possible
        though, a list of lists (or tuples) is preferred because it allows for multiple entries with the same
        key, which will be lost in a dictionary. So if you're passing in a dictionary, make sure there's no
        chance of that happening.

        >>> jr = HTTPCallback(url="http://www.example.com/",params=[["firstname","anders"],["lastname" : "pearson"]])
        >>> jr.params
        [['firstname','anders'],['lastname' : 'pearson']]
        >>> jr = HTTPCallback(url="http://www.example.com/",params=[("firstname","anders"),("lastname" : "pearson")])
        >>> jr.params
        [['firstname','anders'],['lastname' : 'pearson']]
        >>> jr = HTTPCallback(url="http://www.example.com/",params=dict(firstname="anders",lastname="pearson"))
        >>> jr.params.length
        2
        >>> ['firstname','anders'] in jr.params
        True
        >>> ['lastname','pearson'] in jr.params
        True
        """

        if type(params) == type({}):
            params = list(params.iteritems())
        self.params               = [list(t) for t in params]

        """
        HTTPCallback does a certain amount of normalization as well, automatically extracting
        any querystring from the url (and adding it to the queryString if that's also specified).

        >>> jr = HTTPCallback(url="http://www.example.com/foo?a=b")
        >>> jr.url
        'http://www.example.com/foo'
        >>> jr.queryString
        'a=b'
        >>> jr = HTTPCallback(url="http://www.example.com/foo?a=b",queryString="c=d")
        >>> jr.url
        'http://www.example.com/foo'
        >>> jr.queryString
        'a=b&c=d'

        """

        if '?' in self.url:
            (base,qs) = self.url.split('?',1)
            self.url = base
            if self.queryString:
                self.queryString += '&' + qs
            else:
                self.queryString = qs

        self.redirections         = redirections
        self.follow_all_redirects = follow_all_redirects
        self.version              = version
        self.kwargs               = kwargs


    @classmethod
    def from_dict(cls,d=None):
        """ create a HTTPCallback object from a dictionary

        >>> jr = HTTPCallback.from_dict(dict(url="http://www.example.com/"))
        >>> jr.url
        'http://www.example.com/'
        >>> jr.method
        'GET'


        I guess this method is slightly superfluous since you could really just do

        >>> jr = HTTPCallback(**dict(url="http://www.example.com/"))
        >>> jr.url
        'http://www.example.com/'


        To get the same effect.
        
        """
        if d is None:
            d = {}
        
        return cls(url=d.get('url',''),method=d.get('method','GET'),
                   body=d.get('body',''),sendContent=d.get('sendContent'),
                   username=d.get('username',''),password=d.get('password',''),
                   headers=d.get('headers',[]),params=d.get('params',[]),
                   redirections=d.get('redirections',5),follow_all_redirects=d.get('follow_all_redirects',False),
                   version=d.get('version','0.1'),kwargs=d.get('kwargs',{}))

    @classmethod
    def from_json(cls,json=""):
        """ create a HTTPCallback object from a json string

        >>> jr = HTTPCallback.from_json("{\\"url\\" : \\"http://www.example.com/\\"}")
        >>> jr.url
        u'http://www.example.com/'
        >>> jr.method
        'GET'
        """
        return cls.from_dict(loads(json))


    @classmethod
    def from_wsgi_environ(self,environ):
        """ create a json request from a wsgi environ dictionary.

        I don't really have a specific use-case for this but since we can convert in the other direction
        it might be useful.

        """
        
        return {} # TODO



    def as_dict(self):
        """ returns a dict of the request

        >>> jr = HTTPCallback(url="http://www.example.com/")
        >>> jr.as_dict() == dict(url="http://www.example.com/",method="GET",body="",
        ...                      queryString="",username="",password="",headers=[],
        ...                      params=[], redirections=5,follow_all_redirects=False,
        ...                      version="0.1",kwargs={})
        True

        """

        # for GET requests, we fold the params into the queryString
        queryString = self.queryString
        if self.method == 'GET' and self.params:
            qs = '&'.join([k + "=" + urllib.quote(v)  for k,v in self.params])
            queryString = '&'.join([queryString,qs])

        # for other requests, we fold the params into the body, if the body
        # hasn't been specified
        body = self.body
        if self.method != 'GET' and not self.body:
            body = urllib.urlencode(self.params)

        return dict(url=self.url, method=self.method, body=body, queryString=queryString,
                    username=self.username,password=self.password,headers=self.headers,
                    params=self.params,redirections=self.redirections,follow_all_redirects=self.follow_all_redirects,
                    version=self.version,kwargs=self.kwargs)
        
    def as_json(self):
        """ return a JSON object of the HTTPCallback
        
        >>> jr = HTTPCallback(url="http://www.example.com/")
        >>> jr.as_json()
        '{"username": "", "body": "", "headers": [], "url": "http:\\\/\\\/www.example.com\\\/", "queryString": "", "redirections": 5, "version": "0.1", "params": [], "follow_all_redirects": false, "kwargs": {}, "password": "", "method": "GET"}'

        """
        return dumps(self.as_dict())

    def as_wsgi_environ(self):
        """ return a wsgi environ dict of the request

        To make it easier to bridge HTTP and WSGI, a HTTPCallback
        can be converted to a wsgi environ dictionary
        (see http://www.python.org/dev/peps/pep-0333/#environ-variables)
        suitable to pass to a WSGI application.

        >>> jr = HTTPCallback(url="http://www.example.com/")
        >>> environ = jr.as_wsgi_environ()
        >>> environ['REQUEST_METHOD']
        'GET'
        >>> environ['SCRIPT_NAME']
        ''
        >>> environ['PATH_INFO']
        ''
        >>> environ['CONTENT_LENGTH']
        '0'
        >>> environ['QUERY_STRING']
        ''
        >>> environ['SERVER_NAME']
        'www.example.com'
        >>> environ['SERVER_PORT']
        '80'
        >>> environ['SERVER_PROTOCOL']
        'http'
        >>> environ['wsgi.version']
        (1, 0)
        >>> environ['wsgi.url_scheme']
        'http'
        
        

        """

        dummy_input = cStringIO.StringIO()
        dummy_input.write(self.body)
        dummy_input.seek(0)

        environ = {
            'REQUEST_METHOD' : self.method,
            'SCRIPT_NAME' : self.extract_script_name(),
            'PATH_INFO' : self.extract_path_info(),
            'CONTENT_TYPE' : self.content_type(),
            'CONTENT_LENGTH' : str(len(self.body)),
            'QUERY_STRING' : self.queryString,
            'SERVER_NAME' : self.extract_server_name(),
            'SERVER_PORT' : self.extract_port(),
            'SERVER_PROTOCOL' : self.extract_protocol(),
            'wsgi.version' : (1,0),
            'wsgi.url_scheme' : self.extract_protocol(),
            'wsgi.input' : dummy_input, 
            'wsgi.errors' : sys.stderr, 
            'wsgi.multithread' : True,
            'wsgi.multiprocess' : True,
            'wsgi.run_once' : False}

        cookies = []
        for [key,value] in self.headers:
            if key.lower() == 'content-type' or key.lower() == 'content-length':
                continue
            elif key.lower() == 'cookie' or k.lower() == 'cookie2':
                cookies.append(value)
            else:
                h = key.upper()
                h = h.replace('-','_')
                environ['HTTP_' + h] = value
        if cookies:
            environ['HTTP_COOKIE'] = '; '.join(cookies)
            
        return environ

    def extract_script_name(self):
        parts = self.url.split('/')
        path  = '/'.join(parts[3:])
        return path.split('?')[0]

    def extract_path_info(self):
        parts = self.url.split('/')
        path  = '/'.join(parts[3:])
        url = path.split('?',1)
        return urllib.unquote_plus(url[0])

    def extract_server_name(self):
        parts     = self.url.split('/')
        hostname  = parts[2]
        hostparts = hostname.split(':')
        return hostparts[0]

    def extract_port(self):
        parts     = self.url.split('/')
        hostname  = parts[2]
        hostparts = hostname.split(':')
        if len(hostparts) > 1:
            return hostparts[1]
        return '80'

    def extract_protocol(self):
        parts = self.url.split(':')
        return parts[0]

    def content_type(self):
        """ figure out the content type for the request """
        for key,value in self.headers:
            if key.lower() == 'content-type':
                return value
        return "form-data/x-www-urlencoded"


    def as_urlencoded_json(self):
        """ returns the JSON version serialized into a urlencoded string, ready to put in
        a url or in a form-data/x-www-urlencoded request body. 

        >>> jr = HTTPCallback(url="http://www.example.com/")
        >>> jr.as_urlencoded_json()
        '%7B%22username%22%3A%20%22%22%2C%20%22body%22%3A%20%22%22%2C%20%22headers%22%3A%20%5B%5D%2C%20%22url%22%3A%20%22http%3A%5C/%5C/www.example.com%5C/%22%2C%20%22queryString%22%3A%20%22%22%2C%20%22redirections%22%3A%205%2C%20%22version%22%3A%20%220.1%22%2C%20%22params%22%3A%20%5B%5D%2C%20%22follow_all_redirects%22%3A%20false%2C%20%22kwargs%22%3A%20%7B%7D%2C%20%22password%22%3A%20%22%22%2C%20%22method%22%3A%20%22GET%22%7D'
        """

        
        return urllib.quote(self.as_json())

    def template_substitute(self,d=None):
        """ basic URI Templating. substitutes values from the dictionary into template variables in the url

        see: http://bitworking.org/projects/URI-Templates/


        >>> d = {'a' : 'fred', 'b' : 'barney', 'c' : 'cheeseburger',
        ...      '20' : 'this-is-spinal-tap', 'a~b' : 'none%20of%20the%20above',
        ...      'schema' : 'https', 'p' : 'quote=to+bo+or+not+to+be',
        ...      'e' : '','q' : 'hullo#world'}
        >>> jr = HTTPCallback(url="http://example.org/{a}/{b}/")
        >>> jr.template_substitute(d); jr.url
        'http://example.org/fred/barney/'
        >>> jr.url = "http://example.org/{a}{b}/"; jr.template_substitute(d); jr.url
        'http://example.org/fredbarney/'
        >>> jr.url = 'http://example.org/page1#{a}'; jr.template_substitute(d); jr.url
        'http://example.org/page1#fred'
        >>> jr.url = '{schema}://{20}.example.org?date={wilma}&option={a}'
        >>> jr.template_substitute(d); jr.url
        'https://this-is-spinal-tap.example.org?date=&option=fred'
        >>> jr.url = 'http://example.org/{a~b}'; jr.template_substitute(d); jr.url
        'http://example.org/none%20of%20the%20above'
        >>> jr.url = 'http://example.org?{p}'; jr.template_substitute(d); jr.url
        'http://example.org?quote=to+bo+or+not+to+be'
        >>> jr.url = 'http://example.com/order/{c}/{c}/{c}/'; jr.template_substitute(d); jr.url
        'http://example.com/order/cheeseburger/cheeseburger/cheeseburger/'
        >>> jr.url = 'http://example.com/{q}'; jr.template_substitute(d); jr.url
        'http://example.com/hullo#world'
        >>> jr.url = 'http://example.com/{e}/'; jr.template_substitute(d); jr.url
        'http://example.com//'

        """
        if d is None:
            d = {}

        for key,value in d.iteritems():
            template = "{%s}" % key
            if template in self.url:
                self.url = self.url.replace(template,value)
        # clean out any undefined template variables

        self.url = re.sub(r"(\{[^\}]*\})","",self.url)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
