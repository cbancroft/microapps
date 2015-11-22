# Introduction #

Gild is a simple REST service which converts text in one of several simplified markup formats to html. currently it supports textile, markdown, and reStructuredText.

# REST API #

to use it, you make a `POST` (or `GET` actually if you prefer) request to `gild.example.com` (or wherever it's running) to either `/textile`, `/markdown`, or `/reST` with your text as a param named 'text'. it will return an HTML snippet of the converted text.

eg,

```
 $ curl -X POST -F text=foo http://gild.example.com/textile/
 <p>foo</p>
```


Gild also supports (for some engines) 'validate' and 'sanitize' options. 'validate' will ensure that the output snippet will be well-formed and valid XHTML. ie, it will fix up mismatched tags, strip out illegal elements and attributes, etc. 'sanitize' will remove or neuter all traces of javascript from the output, which is nice for processing untrusted input and protecting against cross-site scripting attacks. both are enabled by default. you must explicitly disable them if you feel that you need to allow invalid markup and javascript. (note that at the moment, for the textile engine, you must also turn off 'validate' if you are turning off 'sanitize'). currently, validate and sanitize can't be disabled for markdown and reST. also, beware that while textile and markdown strip out the javascript stuff, reST just escapes it (rendering it harmless).

future plans for gild:

  * memcached based memoization
  * nofollow support (at least for textile when my patch makes it out to a release)
  * other formats: plain structured text, Text::Tiki, possibly a clone of mediawiki's syntax (minus wiki links)
  * look into using MoinMoin's pluggable parser mechanism to allow us to just use all of their format plugins directly

# Requirements #

  * python 2.5
  * setuptools

All other requirements are bundled with Gild and will be automatically installed with the included `init.sh` script.

# Installation #

(Tested on Ubuntu Linux (Feisty), but should work anywhere that TurboGears
works.)

To install, check out code:

```
  $ svn co http://microapps.googlecode.com/svn/gild/trunk/ gild
```

initialize a workingenv:

```
  $ cd gild
  $ ./init.sh .
```

init.sh takes the directory to put the workingenv in as its only
argument. It will create a workingenv and install all the necessary
(and included) eggs into it.

Edit dev.cfg, prod.cfg, or copy one of those to a different
file and configure to your liking (change port #, etc.)

run it:

```
  $ ./start.sh . prod.cfg
```

# Credits #

Gild was developed by Anders Pearson at the Columbia Center For New
Media Teaching and Learning (http://ccnmtl.columbia.edu/).
