from wsgi_intercept.httplib2_intercept import install
install()

# import everything else
#sys.setrecursionlimit(45)
from ConfigParser import ConfigParser
from StringIO import StringIO
from paste.deploy.loadwsgi import appconfig, ConfigLoader
from paste.deploy.loadwsgi import loadapp
from pkg_resources import resource_filename, resource_string
from zope.testing import testrunner
import doctest
import os.path, sys
import pkg_resources
import sys
import unittest
import wsgi_intercept

req = pkg_resources.Requirement.parse('ned')

def get_conf_data(app_name, confp):
    return dict(port=confp.get(app_name, 'port'),
                conf=confp.get(app_name, 'conf'),
                name=confp.get(app_name, 'name'))

def teardown_apps(tc, _registered=[]):
    for name, port in _registered.items:
        wsgi_intercept.remove_wsgi_intercept(name, port)

def setup_apps(app_map_fn):
    confp = ConfigParser()
    confp.read(app_map_fn)
    _registered = teardown_apps.func_defaults[0]
    for app_name in confp.sections():
        data = get_conf_data(app_name, confp)
        app = make_app(data['conf'])
        wsgi_intercept.add_wsgi_intercept(data['name'], data['port'], lambda : app)
        _registered.append(data['name'], data['port'])

def make_app(conf, res_dir):
    return loadapp('config:%s' %conf,
                   **dict(global_conf={},
                          relative_to=res_dir
                          )
                   )

def app_setUp(tc, fn='data/roundtrip_map.ini', req=None, app_map_fn=None):
    if app_map_fn is not None:
        app_map_fn = resource_filename(req, fn)
    setup_apps(app_map_fn)




root_path = pkg_resource.resource_filename('/')

# Remove script directory from path:
scriptdir = os.path.realpath(os.path.dirname(sys.argv[0]))
sys.path[:] = [p for p in sys.path if os.path.realpath(p) != scriptdir]

venv = os.environ['INSTANCE_HOME'] \
       = os.environ['ZOPE_HOME'] = os.environ.get('VIRTUAL_ENV')


defaults = '--tests-pattern ^tests$ -v'.split()
defaults += ['-m',
             '!^('
             'ZConfig'
             '|'
             'BTrees'
             '|'
             'persistent'
             '|'
             'ThreadedAsync'
             '|'
             'transaction'
             '|'
             'ZEO'
             '|'
             'ZODB'
             '|'
             'ZopeUndo'
             '|'
             'zdaemon'
             '|'
             'zope[.]testing'
             '|'
             'zope[.]app'
             ')[.]']

venv = os.path.abspath(venv)
lib_home = os.path.join(sys.prefix, 'lib', 'python%s' % sys.version[:3])
defaults += ['--path', lib_home]
#products = os.path.join(venv, 'Products')
if os.path.exists(root_path):
    defaults += ['--package-path', root_path]

# we are assuming we are in a virtual env and therefore can happily
# not worry about what we add

for path in sys.path:
    defaults += ['--test-path', path]

def load_config_file(option, opt, config_file, *ignored):
    config_file = os.path.abspath(config_file)
    print "Parsing %s" % config_file
    import Zope2
    Zope2.configure(config_file)

testrunner.setup.add_option(
    '--config-file', action="callback", type="string", dest='config_file',
    callback=load_config_file,
    help="""\
Initialize Zope with the given configuration file.
""")


def filter_warnings(option, opt, *ignored):
    import warnings
    warnings.simplefilter('ignore', Warning, append=True)

testrunner.other.add_option(
    '--nowarnings', action="callback", callback=filter_warnings,
    help="""\
Install a filter to suppress warnings emitted by code.
""")

def run():
    return testrunner.run(defaults)

if __name__ == '__main__':
    sys.exit(run())
