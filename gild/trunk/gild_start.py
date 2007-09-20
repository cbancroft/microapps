#!/usr/bin/env python
import pkg_resources
pkg_resources.require("TurboGears")

import cherrypy
from os.path import *
import sys
from gild.controllers import Root

cherrypy.root = Root()

if __name__ == "__main__":
    if exists(join(dirname(__file__),"setup.py")):
        cherrypy.config.update(file=join(dirname(__file__),"dev.cfg"))
    else:
        cherrypy.config.update(file=join(dirname(__file__),"prod.cfg"))
    cherrypy.server.start()

def mp_setup():
    cherrypy.config.update(file=join(dirname(__file__),"prod.cfg"))
