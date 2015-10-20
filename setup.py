#!/usr/bin/env python
########################################
# setup.py
#
# Author        zrong(zengrong.net)
# Creation      2015-04-19
# Modification  2015-10-15
########################################

import os
import re
from setuptools import (setup, find_packages)


here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    content = None
    with open(os.path.join(here, *parts), 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def find_requires(*file_paths):
    require_file = read(*file_paths)
    return require_file.splitlines()

entry_points = {
    'console_scripts': [
        'wpcmd = wpcmd:main',
    ]
}

classifiers = [
    'Programming Language :: Python :: 3.4',
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Operating System :: OS Independent',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
    'Topic :: Utilities',
    'License :: OSI Approved :: BSD License',
]

package_data = {
    'wpcmd':[],
}

#data_files = [(root, [os.path.join(root, f) for f in files])
#    for root, dirs, files in os.walk('bin')]

setup(
    name="wpcmd",
    version=find_version('wpcmd', '__init__.py'),
    url='http://zengrong.net/wpcmd',
    author='zrong',
    author_email='zrongzrong@gmail.com',
    description="A command-line tool for WordPress.",
    long_description=read('README.md'),
    packages=find_packages(exclude=['test']),
    install_requires=find_requires('requirements.txt'),
    keywords = "utils development zrong wpcmd rookout wordpress xmlrpc",
    classifiers=classifiers,
    include_package_data = True,
    #data_files=['wpcmd/wpcmd.ini.tpl'],
    entry_points=entry_points,
    license = "BSD",
    #include_package_data=True,
    #package_data=package_data,
    #dependency_links = [],
    #test_suite='wpcmd.test',
)
