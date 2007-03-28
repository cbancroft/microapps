#!/usr/bin/env python
import pkg_resources
pkg_resources.require("TurboGears")

import cherrypy
from os.path import *
import sys

from fozzy.controllers import build_controllers

build_controllers()

if __name__ == "__main__":

    if len(sys.argv) < 2:
        cherrypy.config.update(file=join(dirname(__file__),"dev.cfg"))
    else:
        cherrypy.config.update(file=join(dirname(__file__),"%s.cfg" % sys.argv[1]))
    
    cherrypy.server.start()

def mp_setup():
    '''
    mpcp.py looks for this method for CherryPy configs but our *.cfg files handle that.
    '''
    cherrypy.config.update(file=join(dirname(__file__),"prod.cfg"))
