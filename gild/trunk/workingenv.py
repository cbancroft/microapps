#!/usr/bin/env python

import sys
import os
import re
import shutil
import optparse
import logging
import urllib2
import urlparse
try:
    import setuptools
    import pkg_resources
except ImportError:
    setuptools = pkg_resources = None

__version__ = '0.0'

class BadCommand(Exception):
    pass


ez_setup_url = 'http://peak.telecommunity.com/dist/ez_setup.py'
python_version = '%s.%s' % (sys.version_info[0], sys.version_info[1])
python_dir = 'lib/python%s' % python_version

help = """\
This script builds a 'working environment', which is a directory set
up for isolated installation of Python scripts, libraries, and
applications.

To activate an installation, you must add the %s directory
to your $PYTHONPATH; after you do that the import path will be
adjusted, as will be installation locations.  Or use
"source bin/activate" in a Bash shell.
""" % python_dir

parser = optparse.OptionParser(
    version=__version__,
    usage='%%prog [OPTIONS] NEW_DIRECTORY\n\n%s' % help)

parser.add_option('-v', '--verbose',
                  action="count",
                  dest="verbose",
                  default=0,
                  help="Be verbose (use multiple times for more effect)")
parser.add_option('-q', '--quiet',
                  action="count",
                  dest="quiet",
                  default=0,
                  help="Be more and more quiet")
parser.add_option('-n', '--simulate',
                  action="store_true",
                  dest="simulate",
                  help="Simulate (just pretend to do things)")
parser.add_option('--force',
                  action="store_false",
                  dest="interactive",
                  default=True,
                  help="Overwrite files without asking")
parser.add_option('-f', '--find-links',
                  action="append",
                  dest="find_links",
                  default=[],
                  metavar="URL",
                  help="Extra locations/URLs where packages can be found (sets up your distutils.cfg for future installs)")
parser.add_option('-Z', '--always-unzip',
                  action="store_true",
                  dest="always_unzip",
                  help="Don't install zipfiles, no matter what (sets up your distutils.cfg for future installs)")
parser.add_option('--site-packages',
                  action="store_true",
                  dest="site_packages",
                  help="Include the global site-packages (not included by default)")
parser.add_option('--no-extra',
                  action="store_false",
                  dest="install_extra",
                  default=True,
                  help="Don't create non-essential directories (like conf/)")
parser.add_option('-r', '--requirements',
                  dest="requirements",
                  action="append",
                  metavar="FILE/URL",
                  help="A file or URL listing requirements that should be installed in the new environment (one requirement per line).  This file can also contain lines starting with -Z, -f, and -r")

class Logger(object):

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    NOTIFY = (logging.INFO+logging.WARN)/2
    WARN = WARNING = logging.WARN
    ERROR = logging.ERROR
    FATAL = logging.FATAL

    LEVELS = [DEBUG, INFO, NOTIFY, WARN, ERROR, FATAL]

    def __init__(self, consumers):
        self.consumers = consumers
        self.indent = 0

    def debug(self, msg, *args, **kw):
        self.log(self.DEBUG, msg, *args, **kw)
    def info(self, msg, *args, **kw):
        self.log(self.INFO, msg, *args, **kw)
    def notify(self, msg, *args, **kw):
        self.log(self.NOTIFY, msg, *args, **kw)
    def warn(self, msg, *args, **kw):
        self.log(self.WARN, msg, *args, **kw)
    def error(self, msg, *args, **kw):
        self.log(self.WARN, msg, *args, **kw)
    def fatal(self, msg, *args, **kw):
        self.log(self.FATAL, msg, *args, **kw)
    def log(self, level, msg, *args, **kw):
        if args:
            if kw:
                raise TypeError(
                    "You may give positional or keyword arguments, not both")
        args = args or kw
        rendered = None
        for consumer_level, consumer in self.consumers:
            if self.level_matches(level, consumer_level):
                if rendered is None:
                    if args:
                        rendered = msg % args
                    else:
                        rendered = msg
                    rendered = ' '*self.indent + rendered
                if hasattr(consumer, 'write'):
                    consumer.write(rendered+'\n')
                else:
                    consumer(rendered)

    def level_matches(self, level, consumer_level):
        """
        >>> l = Logger()
        >>> l.level_matches(3, 4)
        False
        >>> l.level_matches(3, 2)
        True
        >>> l.level_matches(slice(None, 3), 3)
        False
        >>> l.level_matches(slice(None, 3), 2)
        True
        >>> l.level_matches(slice(1, 3), 1)
        True
        >>> l.level_matches(slice(2, 3), 1)
        False
        """
        if isinstance(level, slice):
            start, stop = level.start, level.stop
            if start is not None and start > consumer_level:
                return False
            if stop is not None or stop <= consumer_level:
                return False
            return True
        else:
            return level >= consumer_level

    #@classmethod
    def level_for_integer(cls, level):
        levels = cls.LEVELS
        if level < 0:
            return levels[0]
        if level >= len(levels):
            return levels[-1]
        return levels[level]

    level_for_integer = classmethod(level_for_integer)

class Writer(object):

    def __init__(self, base_dir, logger, simulate,
                 interactive):
        self.base_dir = base_dir
        self.simulate = simulate
        self.interactive = interactive
        self.logger = logger

    def ensure_dir(self, dir):
        if os.path.exists(self.path(dir)):
            self.logger.debug('Directory %s exists', dir)
            return
        self.logger.info('Creating %s', dir)
        if not self.simulate:
            os.makedirs(self.path(dir))

    def ensure_file(self, filename, content):
        path = self.path(filename)
        if os.path.exists(path):
            c = self.read_file(path)
            if c == content:
                self.logger.debug('File %s already exists (same content)',
                                  filename)
                return
            elif self.interactive:
                if self.simulate:
                    self.logger.warn('Would overwrite %s (if confirmed)',
                                     filename)
                else:
                    response = self.get_response(
                        'Overwrite file %s?' % filename)
                    if not response:
                        return
            else:
                self.logger.warn('Overwriting file %s', filename)
        else:
            self.logger.info('Creating file %s', filename)
        if not self.simulate:
            f = open(path, 'w')
            f.write(content)
            f.close()

    def path(self, path):
        return os.path.join(self.base_dir, path)

    def read_file(self, path):
        f = open(path)
        try:
            c = f.read()
        finally:
            f.close()
        return c

    def add_pythonpath(self):
        """
        Add the working Python path to $PYTHONPATH
        """
        writer_path = self.path(python_dir)
        cur_path = os.environ.get('PYTHONPATH', '')
        parts = [os.path.abspath(p) for p in cur_path.split(os.pathsep)]
        if writer_path in parts:
            return
        parts.append(writer_path)
        os.environ['PYTHONPATH'] = os.pathsep.join(parts)

    def get_response(self, msg, default=None):
        """
        Ask the user about something.  An empty response will return
        default (default=None means an empty response will ask again)
        """
        if default is None:
            prompt = '[y/n]'
        elif default:
            prompt = '[Y/n]'
        else:
            prompt = '[y/N]'
        while 1:
            response = raw_input(prompt).strip().lower()
            if not response:
                if default is None:
                    print 'Please enter Y or N'
                    continue
                return default
            if response[0] in ('y', 'n'):
                return response[0] == 'y'
            print 'Y or N please'

basic_layout = [
    python_dir,
    python_dir+'/distutils',
    python_dir+'/setuptools',
    'bin',
    ]

extra_layout = [
    'src',
    'conf',
    ]

files_to_write = {}

def make_working_environment(
    writer, logger, find_links, always_unzip,
    include_site_packages, install_extra):
    """
    Create a working environment.  ``writer`` is a ``Writer``
    instance, ``logger`` a ``Logger`` instance.

    ``find_links`` and ``always_unzip`` are used to create
    ``distutils.cfg``, which controls later installations.

    ``include_site_packages``, if true, will cause the environment
    to pick up system-wide packages (besides the standard library).

    ``install_extra``, if true, puts in some directories like
    ``conf/`` and ``src/``
    """
    if os.path.exists(writer.base_dir):
        logger.notify('Updating working environment in %s' % writer.base_dir)
    else:
        logger.notify('Making working environment in %s' % writer.base_dir)
    layout = basic_layout[:]
    if install_extra:
        layout.extend(extra_layout)
    for dir in layout:
        writer.ensure_dir(dir)
    to_write = files_to_write.copy()
    cfg = distutils_cfg
    if find_links:
        first = True
        for find_link in find_links:
            if first:
                find_link = 'find_links = %s' % find_link
                first = False
            else:
                find_link = '             %s' % find_link
            cfg += find_link + '\n'
    if always_unzip:
        cfg += 'zip_ok = false\n'
    to_write[python_dir+'/distutils/distutils.cfg'] = cfg
    if setuptools is None:
        install_setuptools(writer, logger)
    else:
        setuptools_path = os.path.dirname(setuptools.__file__)
        to_write[python_dir+'/setuptools.pth'] = os.path.dirname(setuptools_path)+'\n'
    for path, content in to_write.items():
        content = content % dict(
            working_env=os.path.abspath(writer.base_dir),
            python_version=python_version)
        writer.ensure_file(path, content)
    writer.ensure_file(python_dir+'/site.py',
                       site_py(include_site_packages))

def install_setuptools(writer, logger):
    """
    Install setuptools into a new working environment (only called
    if setuptools is not installed on the system)
    """
    if writer.simulate:
        logger.notify('Would have installed local setuptools')
        return
    logger.notify('Installing local setuptools')
    f_in = urllib2.urlopen(ez_setup_url)
    tmp_dir = os.path.join(writer.path('tmp'))
    tmp_exists = os.path.exists(tmp_dir)
    if not tmp_exists:
        os.mkdir(tmp_dir)
    ez_setup_path = writer.path('tmp/ez_setup.py')
    f_out = open(ez_setup_path, 'w')
    shutil.copyfileobj(f_in, f_out)
    f_in.close()
    f_out.close()
    writer.add_pythonpath()
    os.system('%s %s --install-dir=%s --script-dir=%s'
              % (sys.executable, ez_setup_path,
                 writer.path(python_dir), writer.path('bin')))
    os.unlink(ez_setup_path)
    if not tmp_exists:
        os.rmdir(tmp_dir)

def read_requirements(logger, requirements):
    """
    Read all the lines from the requirement files, including recursive
    reads.
    """
    lines = []
    req_re = re.compile(r'^(?:-r|--requirements)\s+')
    for fn in requirements:
        logger.info('Reading requirement %s' % fn)
        for line in get_lines(fn):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = req_re.search(line)
            if match:
                lines.extend([read_requirements(line[match.end():])])
                continue
            lines.append(line)
    return lines

def parse_requirements(logger, requirement_lines, options):
    """
    Parse all the lines of requirements.  Can override options.
    Returns a list of requirements to be installed.
    """
    options_re = re.compile(r'^--?([a-zA-Z0-9_-]*)\s+')
    plan = []
    for line in requirement_lines:
        match = options_re.search(line)
        if match:
            option = match.group(1)
            value = line[match.end():]
            if option in ('f', 'find-links'):
                options.find_links.append(value)
            elif option in ('Z', 'always-unzip'):
                options.always_unzip = True
            else:
                logger.error("Bad option override in requirement: %s" % line)
            continue
        plan.append(line)
    return plan

def install_requirements(writer, logger, plan):
    """
    Install all the requirements found in the list of filenames
    """
    writer.add_pythonpath()
    args = ', '.join([
        '"%s"' % req.replace('"', '').replace("'", '') for req in plan])
    logger.notify('Installing %s' % ', '.join(plan))
    if not writer.simulate:
        os.system("%s -c 'import setuptools.command.easy_install; "
                  "setuptools.command.easy_install.main([\"-q\", %s])'"
                  % (sys.executable, args))

def get_lines(fn_or_url):
    scheme = urlparse.urlparse(fn_or_url)[0]
    if not scheme:
        # Must be filename
        f = open(fn_or_url)
    else:
        f = urllib2.urlopen(fn_or_url)
    try:
        return f.readlines()
    finally:
        f.close()

def main():
    options, args = parser.parse_args()
    if not args or len(args) > 1:
        raise BadCommand("You must provide a single output directory")
    output_dir = args[0]
    level = 1 # Notify
    level += options.verbose
    level -= options.quiet
    if options.simulate and not options.verbose:
        level += 1
    level = Logger.level_for_integer(3-level)
    logger = Logger(
        [(level, sys.stdout)])
    requirements = options.requirements or []
    requirement_lines = read_requirements(logger, requirements)
    plan = parse_requirements(logger, requirement_lines, options)
    writer = Writer(output_dir, logger, simulate=options.simulate,
                    interactive=options.interactive)
    make_working_environment(
        writer, logger, options.find_links or [],
        options.always_unzip, options.site_packages,
        options.install_extra)
    if plan:
        install_requirements(writer, logger, plan)

def site_py(include_site_packages):
    s = """\
def __boot():
    # Duplicating setuptools' site.py...
    PYTHONPATH = os.environ.get('PYTHONPATH')
    if PYTHONPATH is None or (sys.platform=='win32' and not PYTHONPATH):
        PYTHONPATH = []
    else:
        PYTHONPATH = PYTHONPATH.split(os.pathsep)
    pic = getattr(sys,'path_importer_cache',{})
    stdpath = sys.path[len(PYTHONPATH):]
    mydir = os.path.dirname(__file__)
    known_paths = dict([(makepath(item)[1],1) for item in sys.path]) # 2.2 comp

    oldpos = getattr(sys,'__egginsert',0)   # save old insertion position
    sys.__egginsert = 0                     # and reset the current one

    for item in PYTHONPATH:
        addsitedir(item)

    sys.__egginsert += oldpos           # restore effective old position

    d,nd = makepath(stdpath[0])
    insert_at = None
    new_path = []

    for item in sys.path:
        p,np = makepath(item)

        if np==nd and insert_at is None:
            # We've hit the first 'system' path entry, so added entries go here
            insert_at = len(new_path)

        if np in known_paths or insert_at is None:
            new_path.append(item)
        else:
            # new path after the insert point, back-insert it
            new_path.insert(insert_at, item)
            insert_at += 1

    sys.path[:] = new_path
    
import sys
import os
import __builtin__

def makepath(*paths):
    dir = os.path.abspath(os.path.join(*paths))
    return dir, os.path.normcase(dir)

def abs__file__():
    \"\"\"Set all module' __file__ attribute to an absolute path\"\"\"
    for m in sys.modules.values():
        try:
            m.__file__ = os.path.abspath(m.__file__)
        except AttributeError:
            continue

try:
    set
except NameError:
    class set:
        def __init__(self, args=()):
            self.d = {}
            for v in args:
                self.d[v] = None
        def __contains__(self, key):
            return key in self.d
        def add(self, key):
            self.d[key] = None

def removeduppaths():
    \"\"\" Remove duplicate entries from sys.path along with making them
    absolute\"\"\"
    # This ensures that the initial path provided by the interpreter contains
    # only absolute pathnames, even if we're running from the build directory.
    L = []
    known_paths = set()
    for dir in sys.path:
        # Filter out duplicate paths (on case-insensitive file systems also
        # if they only differ in case); turn relative paths into absolute
        # paths.
        dir, dircase = makepath(dir)
        if not dircase in known_paths:
            L.append(dir)
            known_paths.add(dircase)
    sys.path[:] = L
    return known_paths

def _init_pathinfo():
    \"\"\"Return a set containing all existing directory entries from sys.path\"\"\"
    d = set()
    for dir in sys.path:
        try:
            if os.path.isdir(dir):
                dir, dircase = makepath(dir)
                d.add(dircase)
        except TypeError:
            continue
    return d

def addpackage(sitedir, name, known_paths):
    \"\"\"Add a new path to known_paths by combining sitedir and 'name' or execute
    sitedir if it starts with 'import'\"\"\"
    if known_paths is None:
        _init_pathinfo()
        reset = 1
    else:
        reset = 0
    fullname = os.path.join(sitedir, name)
    try:
        f = open(fullname, "rU")
    except IOError:
        return
    try:
        for line in f:
            if line.startswith(\"#\"):
                continue
            if line.startswith("import"):
                exec line
                continue
            line = line.rstrip()
            dir, dircase = makepath(sitedir, line)
            if not dircase in known_paths and os.path.exists(dir):
                sys.path.append(dir)
                known_paths.add(dircase)
    finally:
        f.close()
    if reset:
        known_paths = None
    return known_paths

def addsitedir(sitedir, known_paths=None):
    \"\"\"Add 'sitedir' argument to sys.path if missing and handle .pth files in
    'sitedir'\"\"\"
    if known_paths is None:
        known_paths = _init_pathinfo()
        reset = 1
    else:
        reset = 0
    sitedir, sitedircase = makepath(sitedir)
    if not sitedircase in known_paths:
        sys.path.append(sitedir)        # Add path component
    try:
        names = os.listdir(sitedir)
    except os.error:
        return
    names.sort()
    for name in names:
        if name.endswith(os.extsep + "pth"):
            addpackage(sitedir, name, known_paths)
    if reset:
        known_paths = None
    return known_paths

def addsitepackages(known_paths):
    \"\"\"Add site-packages (and possibly site-python) to sys.path\"\"\"
    prefixes = [os.path.join(sys.prefix, "local"), sys.prefix]
    if sys.exec_prefix != sys.prefix:
        prefixes.append(os.path.join(sys.exec_prefix, "local"))
    for prefix in prefixes:
        if prefix:
            if sys.platform in ('os2emx', 'riscos'):
                sitedirs = [os.path.join(prefix, "Lib", "site-packages")]
            elif os.sep == '/':
                sitedirs = [os.path.join(prefix,
                                         "lib",
                                         "python" + sys.version[:3],
                                         "site-packages"),
                            os.path.join(prefix, "lib", "site-python")]
                try:
                    # sys.getobjects only available in --with-pydebug build
                    sys.getobjects
                    sitedirs.insert(0, os.path.join(sitedirs[0], 'debug'))
                except AttributeError:
                    pass
            else:
                sitedirs = [prefix, os.path.join(prefix, "lib", "site-packages")]
            if sys.platform == 'darwin':
                # for framework builds *only* we add the standard Apple
                # locations. Currently only per-user, but /Library and
                # /Network/Library could be added too
                if 'Python.framework' in prefix:
                    home = os.environ.get('HOME')
                    if home:
                        sitedirs.append(
                            os.path.join(home,
                                         'Library',
                                         'Python',
                                         sys.version[:3],
                                         'site-packages'))
            for sitedir in sitedirs:
                if os.path.isdir(sitedir):
                    addsitedir(sitedir, known_paths)
    return None

def setquit():
    \"\"\"Define new built-ins 'quit' and 'exit'.
    These are simply strings that display a hint on how to exit.

    \"\"\"
    if os.sep == ':':
        exit = 'Use Cmd-Q to quit.'
    elif os.sep == '\\\\':
        exit = 'Use Ctrl-Z plus Return to exit.'
    else:
        exit = 'Use Ctrl-D (i.e. EOF) to exit.'
    __builtin__.quit = __builtin__.exit = exit


class _Printer(object):
    \"\"\"interactive prompt objects for printing the license text, a list of
    contributors and the copyright notice.\"\"\"

    MAXLINES = 23

    def __init__(self, name, data, files=(), dirs=()):
        self.__name = name
        self.__data = data
        self.__files = files
        self.__dirs = dirs
        self.__lines = None

    def __setup(self):
        if self.__lines:
            return
        data = None
        for dir in self.__dirs:
            for filename in self.__files:
                filename = os.path.join(dir, filename)
                try:
                    fp = file(filename, "rU")
                    data = fp.read()
                    fp.close()
                    break
                except IOError:
                    pass
            if data:
                break
        if not data:
            data = self.__data
        self.__lines = data.split('\\n')
        self.__linecnt = len(self.__lines)

    def __repr__(self):
        self.__setup()
        if len(self.__lines) <= self.MAXLINES:
            return "\\n".join(self.__lines)
        else:
            return "Type %s() to see the full %s text" % ((self.__name,)*2)

    def __call__(self):
        self.__setup()
        prompt = 'Hit Return for more, or q (and Return) to quit: '
        lineno = 0
        while 1:
            try:
                for i in range(lineno, lineno + self.MAXLINES):
                    print self.__lines[i]
            except IndexError:
                break
            else:
                lineno += self.MAXLINES
                key = None
                while key is None:
                    key = raw_input(prompt)
                    if key not in ('', 'q'):
                        key = None
                if key == 'q':
                    break

def setcopyright():
    \"\"\"Set 'copyright' and 'credits' in __builtin__\"\"\"
    __builtin__.copyright = _Printer("copyright", sys.copyright)
    if sys.platform[:4] == 'java':
        __builtin__.credits = _Printer(
            "credits",
            "Jython is maintained by the Jython developers (www.jython.org).")
    else:
        __builtin__.credits = _Printer("credits", \"\"\"\\
    Thanks to CWI, CNRI, BeOpen.com, Zope Corporation and a cast of thousands
    for supporting Python development.  See www.python.org for more information.\"\"\")
    here = os.path.dirname(os.__file__)
    __builtin__.license = _Printer(
        "license", "See http://www.python.org/%.3s/license.html" % sys.version,
        ["LICENSE.txt", "LICENSE"],
        [os.path.join(here, os.pardir), here, os.curdir])


class _Helper(object):
    \"\"\"Define the built-in 'help'.
    This is a wrapper around pydoc.help (with a twist).

    \"\"\"

    def __repr__(self):
        return "Type help() for interactive help, " \\
               "or help(object) for help about object."
    def __call__(self, *args, **kwds):
        import pydoc
        return pydoc.help(*args, **kwds)

def sethelper():
    __builtin__.help = _Helper()

def aliasmbcs():
    \"\"\"On Windows, some default encodings are not provided by Python,
    while they are always available as "mbcs" in each locale. Make
    them usable by aliasing to "mbcs" in such a case.\"\"\"
    if sys.platform == 'win32':
        import locale, codecs
        enc = locale.getdefaultlocale()[1]
        if enc.startswith('cp'):            # "cp***" ?
            try:
                codecs.lookup(enc)
            except LookupError:
                import encodings
                encodings._cache[enc] = encodings._unknown
                encodings.aliases.aliases[enc] = 'mbcs'

def setencoding():
    \"\"\"Set the string encoding used by the Unicode implementation.  The
    default is 'ascii', but if you're willing to experiment, you can
    change this.\"\"\"
    encoding = "ascii" # Default value set by _PyUnicode_Init()
    if 0:
        # Enable to support locale aware default string encodings.
        import locale
        loc = locale.getdefaultlocale()
        if loc[1]:
            encoding = loc[1]
    if 0:
        # Enable to switch off string to Unicode coercion and implicit
        # Unicode to string conversion.
        encoding = "undefined"
    if encoding != "ascii":
        # On Non-Unicode builds this will raise an AttributeError...
        sys.setdefaultencoding(encoding) # Needs Python Unicode build !


def execsitecustomize():
    \"\"\"Run custom site specific code, if available.\"\"\"
    try:
        import sitecustomize
    except ImportError:
        pass


def main():
    abs__file__()
    paths_in_sys = removeduppaths()
    if include_site_packages:
        paths_in_sys = addsitepackages(paths_in_sys)
    setquit()
    setcopyright()
    sethelper()
    aliasmbcs()
    setencoding()
    execsitecustomize()
    # Remove sys.setdefaultencoding() so that users cannot change the
    # encoding after initialization.  The test for presence is needed when
    # this module is run as a script, because this code is executed twice.
    if hasattr(sys, "setdefaultencoding"):
        del sys.setdefaultencoding
    __boot()
"""
    s += '\n\ninclude_site_packages = %r\n\n' % include_site_packages
    s += "\n\nmain()\n"
    return s

files_to_write[python_dir + '/distutils/__init__.py'] = """\
import os

dirname = os.path.dirname
lib_dir = dirname(dirname(__file__))
working_env = dirname(dirname(lib_dir))

# This way we run first, but distutils still gets imported:
__path__.insert(0, os.path.join(os.path.dirname(os.__file__), 'distutils'))

import dist
def make_repl(v):
    return v.replace('__WORKING__', working_env)
    
old_parse_config_files = dist.Distribution.parse_config_files
def parse_config_files(self, filenames=None):
    old_parse_config_files(self, filenames)
    for d in self.command_options.values():
        for name, value in d.items():
            if isinstance(value, list):
                value = [make_repl(v) for v in value]
            elif isinstance(value, tuple):
                value = tuple([make_repl(v) for v in value])
            elif isinstance(value, basestring):
                value = make_repl(value)
            else:
                print "unknown: %%s=%%r" %% (name, value)
            d[name] = value
dist.Distribution.parse_config_files = parse_config_files
"""

files_to_write[python_dir+'/setuptools/__init__.py'] = """\
import os, sys
# setuptools should be on sys.path already from a .pth file

for path in sys.path:
    if 'setuptools' in path:
        setuptools_path = os.path.join(path, 'setuptools')
        __path__.insert(0, setuptools_path)
        break
else:
    raise ImportError(
        'Cannot find setuptools on sys.path; is setuptools.pth missing?')

execfile(os.path.join(setuptools_path, '__init__.py'))
import setuptools.command.easy_install as easy_install

def get_script_header(script_text, executable=easy_install.sys_executable):
    from distutils.command.build_scripts import first_line_re
    first, rest = (script_text+'\\n').split('\\n',1)
    match = first_line_re.match(first)
    options = ''
    if match:
        script_text = rest
        options = match.group(1) or ''
        if options:
            options = ' '+options
    if options.find('-S') == -1:
        options += ' -S'
    shbang = \"#!%%(executable)s%%(options)s\\n\" %% locals()
    shbang += ("import sys, os\\n"
               "join, dirname = os.path.join, os.path.dirname\\n"
               "lib_dir = join(dirname(dirname(__file__)), 'lib', 'python%%s.%%s' %% tuple(sys.version_info[:2]))\\n"
               "sys.path.insert(0, lib_dir)\\n"
               "import site\\n")
    return shbang

def install_site_py(self):
    # to heck with this, we gots our own site.py and we'd like
    # to keep it, thank you
    pass

easy_install.get_script_header = get_script_header
easy_install.easy_install.install_site_py = install_site_py
"""

distutils_cfg = """\
[install]
prefix = __WORKING__/

[easy_install]
install_dir = __WORKING__/%(python_dir)s
site_dirs = __WORKING__/%(python_dir)s
script_dir = __WORKING__/bin/
""" % {'python_dir': python_dir}

files_to_write['bin/activate'] = """\
# This file must be used with "source bin/activate" *from bash*
# you cannot run it directly
export WORKING_ENV="%(working_env)s"
if [ -n "$_WE_OLD_WORKING_PATH" ] ; then
    PATH="$_WE_OLD_WORKING_PATH"
else
    _WE_OLD_WORKING_PATH="$PATH"
fi
PATH="$WORKING_ENV/bin:$PATH"
export PATH
if [ -n "$_WE_OLD_PYTHONPATH" ] ; then
    PYTHONPATH="$_WE_OLD_PYTHONPATH"
else
    _WE_OLD_PYTHONPATH="$PYTHONPATH"
fi
PYTHONPATH="$WORKING_ENV/lib/python%(python_version)s:$PYTHONPATH"
export PYTHONPATH

function deactivate {
    if [ -n "$_WE_OLD_WORKING_PATH" ] ; then
        PATH="$_WE_OLD_WORKING_PATH"
        export PATH
        unset _WE_OLD_WORKING_PATH
    fi
    if [ -n "$_WE_OLD_PYTHONPATH" ] ; then
        PYTHONPATH="$_WE_OLD_PYTHONPATH"
        export PYTHONPATH
        unset _WE_OLD_PYTHONPATH
    fi
    # Self destruct!
    unset deactivate
}
"""

if __name__ == '__main__':
    try:
        main()
    except BadCommand, e:
        print e
        sys.exit(2)
    


