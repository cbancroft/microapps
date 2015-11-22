# Introduction #

Torsten is a microapp for basic image tiling.

You POST an image, a tile size, and a URI of an upload handler and it slices the image up into tiles of that size, uploads each to the upload server and returns a JSON object that lists each of the pieces (URI, width, height, and location in the grid).

(The name 'Torsten' is a reference to the main character in Lars Gustafsson's short story "A Tiler's Afternoon".)

# REST API #

There is only one action: a `POST` to `/tile`. The only required parameter is `image` which should be an image file in a `multipart/form-encoded` format. There are two optional parameters: `size`, and `upload_uri` which are explained below.

A sample curl session looks like:

```
  $ curl -X POST  -F "image=@MyImage.jpg" \
    http://torsten.example.com/tile > tiles.json
```

The default tile size is 300 pixels.

The resulting JSON is a two dimensional array of tiles. It will look something like this:

```
{"tiles" : [[{"uri" : "http://uploaded.example.com/blah/blah/image_0_0.jpg",
           "width" : 300, "height" : 300},
          {"uri" : "http://uploaded.example.com/blah/blah/image_0_1.jpg",
           "width" : 300", "height" : 300},
          ...],
         [ ... ],
         ...
]}

```

You can specify a different tile size with a `size` parameter like so:

```
  $ curl -X POST  -F size=200 -F "image=@MyImage.jpg" \
    http://torsten.example.com/tile > tiles.json
```

Torsten should be configured with a default upload server URI. That URI should accept a POST request containing a file (must accept at least images) and save the file and return the URI where that file is now served from. If no `upload_uri` parameter is set, this default is what Torsten will use. To have Torsten upload to a different upload server, pass in an `upload_uri` parameter:

```
  $ curl -X POST  -F upload_uri=http://upload.example.com/upload -F "image=@MyImage.jpg" \
    http://torsten.example.com/tile > tiles.json
```

That's pretty much it. Currently only jpg, gif, and png images are
supported.

# Requirements #

  * python 2.5
  * setuptools
  * Python Image Library installed in your /usr/lib/python2.5/site-packages/ (this usually has to be installed with a distro specific command (eg, 'apt-get install python-imaging'))
  * upload server running somewhere and accessible to Torsten

All other requirements are bundled with Drinkme and will be automatically installed with the included `init.sh` script.

# Possible Future Features #

If anyone has strong feelings one way or the other about these, let us know:

  * specify no upload\_uri and get a tarball or zip of the image tiles. The JSON struct (also included in the tarball) would then refer to filenames of the tiles rather than URIs. Multipart HTTP might also be useful here.
  * specify an image URI instead of `POST`ing the image directly. Then Torsten would fetch the image at the URI, and tile it.
  * async/parallel image uploading. Currently, it uploads the tiles one at a time to the upload server and that can be a serious bottleneck if the latency on the upload server is bad. Sometimes this could be sped up by doing the uploads in parallel. The downside is that if this isn't done carefully, it could overwhelm the upload server.
  * recursive tiling. Imagining a farm of Torsten servers. Upload a really big image to one and, instead of tiling it all by itself, it makes a couple big tiles and sends each of them out to different Torsten servers which in turn make smaller tiles out of each of those, thus distributing the load a bit more evenly. I guess if things get to the point that this is necessary, you'd probably want to move to a mapReduce type setup though.

# Installation #

(Tested on Ubuntu Linux (Feisty), but should work anywhere that Paste
works.)

To install, check out code:

```
  $ svn co http://microapps.googlecode.com/svn/torsten/trunk/ torsten
```

initialize a workingenv:

```
  $ cd torsten
  $ ./init.sh .
```

init.sh takes the directory to put the workingenv in as its only
argument. It will create a workingenv and install all the necessary
(and included) eggs into it.

edit development.ini, prod.ini, or copy one of those to a different
file and configure to your liking (change port #, default upload server, etc.)

run it:

```
  $ ./start.sh . prod.ini
```

Torsten is also a WSGI/Paste app, so you should be able to combine it
with any other WSGI frameworks, servers, etc. in a standard manner.

# Credits #

Torsten was developed by Anders Pearson at the Columbia Center For New
Media Teaching and Learning (http://ccnmtl.columbia.edu/).