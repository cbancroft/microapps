# Tasty #

## Introduction ##

Tasty is a full featured, efficient tagging engine accessible entirely through a REST interface. You can think of it as del.icio.us but designed to be embedded within an application (or multiple applications). Since the interface is just REST, it can be embedded in an application written in any programming language (as long as that language supports basic HTTP). Tasty is written in python, using the TurboGears framework.

Please use the microapps Google Group to discuss Tasty and make feature requests. Use the Issue tracker here to report bugs.

Tasty was developed at the [Columbia Center For New Media Teaching And Learning](http://ccnmtl.columbia.edu/).

## Requirements ##

To run tasty, you will need the following:

  * [python](http://www.python.org/) 2.4
  * [TurboGears](http://turbogears.org/) 1.0b1
  * [restresource](http://cheeseshop.python.org/pypi/restresource/) 0.1
  * [restclient](http://cheeseshop.python.org/pypi/restclient/) 0.9.5
  * a relational database (tested with [PostgreSQL](http://postgresql.org/) and [sqlite](http://sqlite.org/) so far. should work with anything though)

## Installation ##

These docs cover UNIX installation. Tasty has reportedly been made to run on windows, but the author has no way to test that so you're on your own there.

The basic steps for installing Tasty are to get the code and the requirements, make sure the requirements are installed in your environment, set up a database, configure Tasty to use the database, and then start the Tasty server.
Download Tasty

Either download the source distribution from the [Cheeseshop](http://cheeseshop.python.org/pypi/Tasty).

Or check a release from subversion:

```
% svn co http://microapps.googlecode.com/svn/Tasty/tags/1.3 Tasty
```

### Install Requirements Into Your environment ###

First, you'll need a database (preferably postgresql; that's what the rest of this document will use as an example. it should work with just about any database that SQLObject supports though). Having sqlite3 installed will also be useful for running the unit tests.

Then you'll need to
[http://peak.telecommunity.com/DevCenter/EasyInstall#installation-instructions
install setuptools/easy\_install] (if you don't already have it installed).

Tasty is a pretty standard TurboGears application so if you're comfortable installing and deploying TG, It should be pretty straightforward. Tasty's requirements are all listed in the requirements.txt file and should all be ready to easy\_install.

The easiest path to installation (and the strongly recommended approach) is to use the workingenv.py script in the project directory to download and install all of the python dependencies for you:

```
% python workingenv.py -r requirements.txt working-env
```

That will create a 'working-env' directory with all of the requirements installed in it. You must then activate the environment to run tasty:

```
% source working-env/bin/activate
```

You can read more about workingenv.py in Ian Bicking's
[blog post](http://blog.ianbicking.org/workingenv-revisited.html).

You should then run the unit tests to make sure everything was installed properly. It should look something like:

```
% nosetests
............................
----------------------------------------------------------------------
Ran 28 tests in 2.876s
OK
```

### Create Database and Configure ###

To set up the database (again, using PostgreSQL as the example), you'll need to create a database user and a new database:

```
# for PostgreSQL:
% createuser tasty
% createdb tasty
```

If you change either of those, you'll want to change the entries in dev.cfg and/or prod.cfg

TurboGears can then set up the database tables with:

```
% tg-admin sql create
```

If you're upgrading from a previous release of Tasty, you can just use your existing database. Just check the config files and make sure they have the right settings.
Run the Tasty Server

It should be ready to run:

```
% python start-tasty.py
# or, for a production setup (no auto-reloading, etc)
% python start-tasty.py prod.cfg
```

### Deployment ###

The recommended approach to deployment is to run Tasty as a standalone
server behind an Apache (or lighttpd or nginx or ...)
proxy. [This article](http://thraxil.org/users/anders/posts/2006/09/13/TurboGears-Deployment-with-supervisord-and-workingenv-py/) covers how to set up a good production deployment of a TurboGears application and it's instructions should work fine for Tasty.

Tasty can also be deployed as a mod\_python application using mpcp. There is a mp\_setup() function defined in start-tasty.py. This is a trickier deployment to set up though and is no longer recommended.

## Tag Model ##

The core resources are Services, Users, Items, and Tags.

The Service resource exists primarily as a form of namespacing. it allows multiple applications to use the same tag server without stomping on each others' data. all points within an application that access the tag server should use the same Service. the service MUST always be specified in every request URI.

the Users, Items, and Tags use the model
[described](http://tagschema.com/blogs/tagschema/2005/06/slicing-and-dicing-data-20-part-2.html) on tagschema.com

## REST API ##

Tasty's interface is basically a REST interface. There are some slight variations from the canonical approach but they're reasonable ones. The important thing is that all interaction with Tasty is via HTTP and makes use of a lot of the functionality built into HTTP (methods, URIs, Accept: headers, etc.). JSON is used as the default data format but HTML and XML can also be used.

the basic 'tag item' request looks like:

```
 PUT /service/<servicename>/user/<username>/item/<itemname>/tag/<tag>/
```

to get a list of what tags a user has tagged an item with:

```
 GET /service/<servicename>/user/<username>/item/<itemname>/
```

to get a list of what items a user has tagged with a given tag:

```
 GET /service/<servicename>/user/<username>/tag/<tag>/
```

to get a list of users who have tagged an item with a given tag:

```
 GET /service/<servicename>/item/<itemname>/tag/<tag>/
```

to remove a tag from an item for a specific user:

```
 DELETE /service/<servicename>/user/<username>/item/<itemname>/tag/<tag>/
```

to remove a tag from an item, for all users:

```
 DELETE /service/<servicename>/item/<itemname>/tag/<tag>/
```

etc.

/service/

&lt;servicename&gt;

/ MUST always be the root of the request, but the other components MAY be in any order (while keeping the type/name pairs together). eg, the following requests are all equivalent and legal:

```
 GET /service/<servicename>/user/<username>/item/<itemname>/tag/<tag>/
 GET /service/<servicename>/item/<itemname>/user/<username>/tag/<tag>/
 GET /service/<servicename>/tag/<tag>/user/<username>/item/<itemname>/
```


but

```
 GET /user/<username>/item/<itemname>/tag/<tag>/service/<servicename>/
```

would be illegal.



&lt;servicename&gt;

, 

&lt;itemname&gt;

, 

&lt;username&gt;

, and 

&lt;tag&gt;

 all MUST be URI encoded strings. everything else is pretty much legal though. spaces, non-ascii (UTF-8 is preferred), etc. are all ok. whitespace at the beginning or end will be automatically trimmed off.

lists of results will be returned in JSON format strings. if an Accept header of 'application/xml' is sent, results will instead be returned in XML.

to get a list of items that a user has tagged with more than one tag (ie, the intersection):

```
 GET /service/<servicename>/user/<username>/tag/<tag1>/tag/<tag2>/tag/<tag3>/
```

similarly, any of the above GET, POST, or DELETE requests should support specifying multiple tags, items, and/or users. multiple services are NOT supported.

### Tag Clouds ###

```
 GET /service/<servicename>/user/<username>/cloud
```

it will return a dictionary with 'items' and 'tags' keys, each corresponding to a list of items or tags, each with a 'count' of how many times they appear for that user.

you can actually append 'cloud' to the end of just about any of those other requests above and it will return something reasonable.

### Related ###

```
    GET /service/<servicename>/item/<itemname>/related
```

will return a list of items that appear to be related (based on their tags + users)

also may need to specify a threshold or limit, etc.

## Client Implementations ##

Examples of client-side code for interacting with Tasty. If you have improvements on these, or additional examples in languages not covered here, please submit them.

### Commandline ###

curl is very useful for testing out ideas from the command line, particularly with its -X flag. eg,

```
curl -X POST -d "" http://localhost:9980/service/test/user/bob/item/foo/tag/blah/
curl -X DELETE http://localhost:9980/service/test/user/bob/item/foo/tag/blah/
```

### Python ###

```
import httplib, urllib
from simplejson import loads as json_to_py

def get_tags(user,item):
    url = "http://tasty.example.com/service/myservice/user/%s/item/%s/" % (user,item)
    try:
        return [t['tag'] for t in json_to_py(urllib.urlopen(url).read())['tags']]
    except json.ReadException:
        return []



def add_tag(user,item,tag):
    conn = httplib.HTTPConnection("tasty.example.com")
    url = "/service/myservice/user/%s/item/%s/tag/%s/" % (user,item,tag)
    conn.request("POST",url)
    response = conn.getresponse()
    conn.close()
```

sometimes, adding or deleting does not need to be done synchronously. if that's the case, you can eliminate http latency from bogging you down by spawning a new thread to make the request.

```
from threading import Thread

class Putter(Thread):
    def __init__(self,url):
        self.url = url
    def run(self):
        conn = httplib.HTTPConnection("tasty.example.com")
        conn.request("POST",self.url)
        r = conn.getresponse()
        conn.close()

def add_tag(user,item,tag):
    p = Putter("/service/myservice/user/%s/item/%s/tag/%s/" % (user,item,tag))
    p.start()
```


but i recommend trying it first without the thread. the performance hit of making an http request to a (presumably) local service may be surprisingly small. a Twisted implementation would probably be even faster and cleaner, but i don't really know twisted very well. sample twisted client code is welcome.

also of interest may be this sample implementation of
[cloud scaling](http://microapps.sourceforge.net/tasty/cloud_scaling.html).

### Perl ###

```
my $TASTY_BASE = "tasty.example.com";
my $TASTY_SERVICE = "example";

sub tasty_get {
    use LWP::Simple;
    use JSON;
    my $url = shift;
    my $full = "http://${TASTY_BASE}/service/${TASTY_SERVICE}/$url";
    my $r = get $full;
    my $json = new JSON;
    my $obj = $json->jsonToObj($r);
    if (!$obj) {
        $obj = {};
    }
    return $obj;
}



use LWP::UserAgent;
use HTTP::Request;
use HTTP::Request::Common qw(POST);

sub tasty_put {
    my $url = shift;
    my $ua = LWP::UserAgent->new;
    my $req = POST "http://${TASTY_BASE}/service/${TASTY_SERVICE}/$url", [];
    return $ua->request($req)->as_string;
}



sub tasty_delete {
    my $url = shift;
    my $ua = LWP::UserAgent->new;
    my $req = HTTP::Request->new(DELETE => "http://${TASTY_BASE}/service/${TASTY_SERVICE}/$url");
    my $res = $ua->request($req);
}
```


### Java ###

TODO

### PHP ###

TODO

### JavaScript ###

TODO