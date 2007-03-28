#!/usr/local/bin/python
import pkg_resources
pkg_resources.require("TurboGears")

import turbogears
import cherrypy
cherrypy.lowercase_api = True

from os.path import *
import sys

from tasty.controllers import build_controllers

root = build_controllers()

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if __name__ == "__main__":
    if len(sys.argv) > 1:
        turbogears.update_config(configfile=sys.argv[1], 
            modulename="tasty.config")
    elif exists(join(dirname(__file__), "setup.py")):
        turbogears.update_config(configfile="dev.cfg",
            modulename="tasty.config")
    else:
        turbogears.update_config(configfile="prod.cfg",
            modulename="tasty.config")
    turbogears.start_server(root)


def mp_setup():
    '''
    mpcp.py looks for this method for CherryPy configs but our *.cfg files handle that.
    '''
    cherrypy.config.update(file=join(dirname(__file__),"prod.cfg"))
