#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="httpcallback",
      version="0.1",
      description="reference implementation of HTTPCallback",
      summary="reference implementation of HTTPCallback",
      author="Anders Pearson",
      author_email="anders@columbia.edu",
      url="http://code.google.com/p/microapps/HTTPCallback",
      license="BSD",
      zip_safe=True,
      install_requires = [
            "simplejson",
      ],
      packages=find_packages(),
      )
