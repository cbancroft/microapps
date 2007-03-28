#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="restresource",
      version="0.1",
      description="helper for writing REST services with cherrypy",
      summary="helper for writing REST services with cherrypy",
      long_description="helper for writing REST services with cherrypy",            
      author="anders",
      author_email="anders@columbia.edu",
      url="http://code.thraxil.org/restresource/",
      license="BSD",
      zip_safe=False,
      packages=find_packages()
      )
