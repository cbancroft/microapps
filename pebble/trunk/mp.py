#!/usr/bin/env python

import prodpath
import pkg_resources
pkg_resources.require("TurboGears")

import cherrypy
from os.path import *
import sys

from pebble.controllers import build_controllers

build_controllers()
def mp_setup():
    '''
    mpcp.py looks for this method for CherryPy configs but our *.cfg files handle that.
    '''
    cherrypy.config.update(file=join(dirname(__file__),"prod.cfg"))



