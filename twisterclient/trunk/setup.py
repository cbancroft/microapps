from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='twisterclient',
      version=version,
      description="Twister client interface",
      long_description="""\
Convenient python client interface to a Twister server.""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='REST microapp twister',
      author='Anders Pearson',
      author_email='anders@columbia.edu',
      url='http://code.google.com/p/microapps/wiki/TwisterClient',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
         "restclient","httplib2","simplejson"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
