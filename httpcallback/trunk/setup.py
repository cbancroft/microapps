#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="jsonrequest",
      version="0.1",
      description="reference implementation of JSONRequest",
      summary="reference implementation of JSONRequest",
      author="Anders Pearson",
      author_email="anders@columbia.edu",
      url="http://microapps.sourceforge.net/jsonrequest/",
      license="BSD",
      zip_safe=True,
      install_requires = [
            "simplejson",
      ],
      packages=find_packages(),
      )
