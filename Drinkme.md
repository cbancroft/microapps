# Introduction #

Drinkme is a microapp for basic image resizing.

You POST an image and a size, and it resizes the image
to that size and returns it. not very complicated.

# REST API #

There is only one action: a `POST` to `/resize`. The only required parameter is `image` which should be an image file in a `multipart/form-encoded` format. There are two optional parameters: `resize`, and `square` which are explained below.

A sample curl session looks like:

```
  $ curl -X POST  -F "image=@MyImage.jpg" \
    http://drinkme.example.com/resize > thumb.jpg
```

The default size is 100 pixels. It will scale the image so its
longest side is at most 100 pixels, while preserving the aspect
ratio.

You can specify a different size with a `size` parameter like so:

```
  $ curl -X POST  -F size=200 -F "image=@MyImage.jpg" \
    http://drinkme.example.com/resize > thumb200.jpg
```


Drinkme will also make square thumbnails. Ie, it will crop the
image so its width and height are equal and then scale it to
the specified size. This is disabled by default but can be
enabled by sending a non-zero value for the 'square' parameter:

```
  $ curl -X POST  -F square=1 -F "image=@MyImage.jpg" \
    http://drinkme.example.com/resize > square.jpg
```

From python, you can use the convenient [restclient](http://microapps.sourceforge.net/restclient/):
```
>>> from restclient import POST
>>> image = open("big_image.jpg", 'r').read()
>>> thumb_file = open("big_image_thumb.jpg", 'w')
>>> out = POST('http://drinkme.example.com/resize', 
               files= { 'image' : { 'file' : image_file , 'filename' : image }},
               async=False)
>>> thumb_file.write(out)
>>> thumb_file.close()
```

That's pretty much it. Currently only jpg, gif, and png images are
supported.

# Requirements #

  * python 2.5
  * setuptools

All other requirements are bundled with Drinkme and will be automatically installed with the included `init.sh` script.

# Installation #

(Tested on Ubuntu Linux (Feisty), but should work anywhere that Paste
works.)

To install, check out code:

```
  $ svn co http://microapps.googlecode.com/svn/drinkme/trunk/ drinkme
```

initialize a workingenv:

```
  $ cd drinkme
  $ ./init.sh .
```

init.sh takes the directory to put the workingenv in as its only
argument. It will create a workingenv and install all the necessary
(and included) eggs into it.

edit development.ini, prod.ini, or copy one of those to a different
file and configure to your liking (change port #, etc.)

run it:

```
  $ ./start.sh . prod.ini
```

Drinkme is also a WSGI/Paste app, so you should be able to combine it
with any other WSGI frameworks, servers, etc. in a standard manner.

# Credits #

Drinkme was developed by Anders Pearson at the Columbia Center For New
Media Teaching and Learning (http://ccnmtl.columbia.edu/).

