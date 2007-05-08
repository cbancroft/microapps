from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("tasty", "release.py"))

setup(
    name="Tasty",
    version=version,
    
    # uncomment the following lines if you fill them out in release.py
    description=description,
    author=author,
    author_email=email,
    url=url,
    #download_url=download_url,
    license=license,
    
    install_requires = [
        "TurboGears >= 1.0b1",
        "restresource >= 0.1",
        "restclient >= 0.9.5"
    ],
    scripts = ["start-tasty.py"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='tasty',
                                     package='tasty'),
    keywords = [
        'turbogears.app',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Applications',
    ],
    test_suite = 'nose.collector',
    )
    
