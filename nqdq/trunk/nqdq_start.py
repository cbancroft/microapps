#!/usr/bin/env python
import pkg_resources
pkg_resources.require("TurboGears")

import cherrypy
from os.path import *
import sys

from nqdq.controllers import build_controllers

build_controllers()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cherrypy.config.update(file=join(dirname(__file__),sys.argv[1]))
    else:
        cherrypy.config.update(file=join(dirname(__file__),"dev.cfg"))
    cherrypy.server.start()

def mp_setup():
    cherrypy.config.update(file=join(dirname(__file__),"prod.cfg"))    

