from setuptools import setup, find_packages

setup(
    name="restclient",
    version="0.9.4",
    author="Anders Pearson",
    author_email="anders@columbia.edu",
    url="http://code.thraxil.org/restclient/",
    description="convenient library for writing REST clients",
    long_description="makes it easy to invoke REST services properly",
    scripts = [],
    license = "BSD",
    platforms = ["any"],
    zip_safe=False,
    packages=find_packages()
    )
    
