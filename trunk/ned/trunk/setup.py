from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='ned',
      version=version,
      description="N.etwork E.vent D.ispatch",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='webob microapp dispatch event hub',
      author='whit',
      author_email='whit at openplans.org',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'PasteDeploy',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = ned.wsgiapp:make_app
      """,
      )
