# Fozzy #

Fozzy is a full-text search service. It utilizes PostgreSQL's tsearch2 engine to do the hard work of stemming and searching. Its interface is just an extremely simple REST API so it can easily be integrated into just about any other application.

Fozzy doesn't have any fancy query language and doesn't attempt to track additional fields on documents. Its goal is to be good enough for the 80% of apps that just need a simple search box where a user can type in a word or two and get the relevant documents back. If you want more advanced functionality than this, you might want to look at lucene or something similar instead of Fozzy.
Installation

I've only ever installed Fozzy on linux systems, but it ought to work on any platform that supports PostgreSQL and Python 2.4. Some of the installation commands may be different though. Let me know if you get it working elsewhere.

You'll need several things installed first:

  * PostgreSQL, obviously. Additionally, it will have to be compiled with tsearch2 enabled, which may not be the default on some platforms. Refer to the PostgreSQL documentation for instructions on how to do this.
  * Python >= 2.4
  * Turbogears 0.8.x. see http://www.turbogears.org/download/index.html for instructions on installing turbogears
  * restresource. If you've installed TurboGears, you should have setuptools installed, so you can just do: % sudo easy\_install restresource and it should install it for you.

Then, grab a copy of the the fozzy source code and unpack it somewhere and cd into the directory.

First, we need to set up the database. By default, Fozzy will use a database named 'fozzy' and a database user also named 'fozzy'. If you prefer something different, just remember to change it in the .cfg files.

```
% createuser fozzy 
% createdb fozzy
```

Next, we let the turbogears admin script setup our database tables:

```
% tg-admin sql create
```

Just remember to do that from inside the fozzy source directory and make sure that dev.cfg has the database settings you want to use.

The tsearch2 stuff takes some additional setup:

```
% psql fozzy -U fozzy < fozzy/sql/tsearch2.sql
% psql fozzy -U fozzy < fozzy/sql/fozzy.sql
```

Those scripts add the tsearch2 stored procedures and add the right indexes and vector columns to the database.

For a simple setup, that's pretty much it. You can run Fozzy using the standalone cherrypy http server in TurboGears with:

```
% python fozzy_start.py
```

and it will start fozzy listening on port 9081 (or whatever you might have changed it to in dev.cfg).

If you have curl installed, you can test it out from the commandline:

```
% curl -X PUT -d "text=this%20is%20some%20text%20to%20index%20" \
  http://localhost:9081/application/curltest/document/sample/
ok
% curl http://localhost:9081/application/curltest/search?q=index
[["sample","this is some text to <b>index</b>",0.100000]]
```

For a production system, you'll probably want to deploy Fozzy either as a mod\_python application or behind a lighttpd or apache proxy. See the TurboGears deployment docs for more instructions on how to do that.

## Configuration ##

There isn't much to configure with Fozzy. There are two config files: dev.cfg and prod.cfg. Fozzy will look at dev.cfg if you run it standalone with fozzy\_start.py. It will look at prod.cfg instead if you run it as a mod\_python app. See the turbogears documentation for more info on the format of the config files and why there are two, etc.

## Using Fozzy ##

The API is pretty simple and shouldn't be hard to integrate into just about any application written in any language that can do basic HTTP.

First, the basics of Fozzy. There are only two components of Fozzy's model: Applications, and Documents. Applications only exist to allow you to use a single Fozzy server to handle search for multiple applications with their data seperate. When integrating an Fozzy into your application, you'll want to just come up with a single application name and always use that. Documents are just the things that get indexed. Documents have a body (the text that gets indexed) and a name (a short, unique string that goes into the url that you identify them by).

So, to integrate Fozzy into your application, you first need to come up with a single application name that all your calls to Fozzy will include, then you need to come up with a convention for uniquely naming documents. That will probably be based on whatever you already use for a primary key for those objects in your application, or filenames or something similar.

Usage then consists of constructing urls and making HTTP requests.

To add a new document to your application, you make a PUT request to

```
http://fozzy_server/application/<yourappname>/document/<documentname>/
```

with the parameter 'text' set to the body text of the document. Fozzy will add the document and index the text. Using curl from the commandline, this would look something like:

```
 % curl -X PUT -d "text=this%20is%20some%20text%20to%20index%20" \
   http://localhost:9081/application/curltest/document/sample/
```

Using the [restclient](Restclient.md) python package (installable with easy\_install), the exact same request would look like:

```
  PUT("http://localhost:9081/application/curltest/document/sample/",
  params={'text' : "this is some text to index"})
```

To search for a phrase, you make a GET request to /application//search?q=text%20to%20search%20fo

Ie,

```
 % curl http://localhost:9081/application/curltest/search?q=index
```

with curl, or

```
 results = GET("http://localhost:9081/application/curltest/search?q=index")
```

with restclient. The result of the query is a JSON string, which should parse into a list of result tuples, each of which consists of (document\_name, excerpt, rank) with the most relevant documents at the front of the list.

To update a document, you just make another PUT request to the same URL that was used for adding it, sending the new text to be indexed in its place.

To remove a document from Fozzy, just send a DELETE request to the document's URL (the same URL used for creating and updating) and it will delete it from the index.

That's pretty much all there is too it. The general pattern is that you find the spots in your application where a new content item is added, edited, or removed, and insert in a request to your Fozzy server to take the appropriate action on the item. Then you create a search interface that passes the query to Fozzy and formats and returns the result set.

## Download ##

easy\_install is the recomended approach, but you can also just grab
the egg straight from the [cheeseshop](http://cheeseshop.python.org/pypi/fozzy/).

## Credits ##

Fozzy was written by Anders Pearson (anders@columbia.edu) at the
[Columbia Center for New Media Teaching and Learning](http://ccnmtl.columbia.edu/).

## License ##

Fozzy is distributed under the GNU GPL.