from setuptools import find_packages, setup

NAME = 'dynamic-rest-client'
DESCRIPTION = 'Python client for dynamic-rest with minimal dependencies'
URL = 'http://github.com/AltSchool/dynamic-rest-client'
VERSION = '0.0.4'
SCRIPTS = []

setup(
    description=DESCRIPTION,
    include_package_data=True,
    dependency_links=open('dependency_links.txt').readlines(),
    install_requires=open('install_requires.txt').readlines(),
    long_description=open('README.rst').read(),
    name=NAME,
    packages=find_packages(),
    scripts=SCRIPTS,
    url=URL,
    version=VERSION
)
