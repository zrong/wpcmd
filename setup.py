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
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.4',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries :: Python Modules',
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
    classifiers=classifiers,
    entry_points=entry_points
    #include_package_data=True,
    #package_data=package_data,
    #data_files=data_files,
    #dependency_links = [],
    #test_suite='wpcmd.test',
)
