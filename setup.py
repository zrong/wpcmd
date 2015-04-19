#!/usr/bin/env python
########################################
# setup.py
#
# Author        zrong(zengrong.net)
# Creation      2015-04-19
########################################

import os
from setuptools import setup

requires = []

dependency_links = [
    'https://github.com/zrong/python/releases/download/v0.2.9/zrong-0.2.9.tar.gz',
]

entry_points = {
    'console_scripts': [
        'wpcmd = wpcmd:call',
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
    'wpcmd':['build.conf'],
}

#data_files = [(root, [os.path.join(root, f) for f in files])
#    for root, dirs, files in os.walk('bin')]

setup(
    name="wpcmd",
    version="0.1.0",
    url='http://zengrong.net/',
    author='zrong',
    author_email='zrongzrong@gmail.com',
    description="A command-line tool for WordPress.",
    packages=['wpcmd'],
    classifiers=classifiers,
    entry_points=entry_points,
    #include_package_data=True,
    #package_data=package_data,
    #data_files=data_files,
    #install_requires=requires,
    #dependency_links = dependency_links,
    #test_suite='hhlb.test',
)
