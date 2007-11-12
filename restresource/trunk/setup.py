#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="restresource",
    version="0.4",
    description="helper for writing REST services with cherrypy,turbogears",
    long_description="helper for writing REST services with cherrypy",            
    author="anders,schuyler",
    author_email="anders@columbia.edu",
    url="http://microapps.org",
    license="BSD",

    install_requires = [
        "TurboGears >= 1.0.1",
    ],
    include_package_data = True,
    package_data = {'':['*.kid',],
                    },
    zip_safe=False,
    packages=find_packages(exclude=["tgtest","tgtest.*"]),
    )
