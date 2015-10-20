#########################################
# __init__.py
#
# Author zrong(zengrong.net)
# Creation 2014-11-18
# Modification 2015-05-28
#########################################

import sys
import os
import logging
import importlib
import argparse

__all__ = ['util', 'new', 'show', 'update']
__version__ = '0.1.4'

try:
    import rookout
except ImportError:
    sys.path.insert(0, os.getenv('rookout'))

from rookout import slog, add_log_handler
from wpcmd.base import (Conf, TermCache)

add_log_handler(slog,
    handler=logging.StreamHandler(sys.stdout),
    debug=logging.DEBUG)

class WPError(Exception):
    pass

def check_args(argv=None):
    parser = argparse.ArgumentParser(prog='wpcmd')
    subParsers = parser.add_subparsers(dest='sub_name', help='sub-commands')

    put = subParsers.add_parser('util', 
        help='Some utils.')
    put.add_argument('-r', '--readme', action='store_true', 
        help='Build README.md.')
    put.add_argument('-u', '--url', action='store_true', 
        help='Rewrite url.')
    put.add_argument('-c', '--category', action='store_true', 
        help='Rewrite category.')
    put.add_argument('-d', '--dirname', type=str, default='post',
        choices = ['post', 'page', 'draft', 'all'],
        help='Rewrite articles by type. The value is [post|page|draft|all].')
    put.add_argument('-a', '--analytic', action='store_true',
        help='Analytic the articles.')
    put.add_argument('-k', '--check', action='store_true',
        help='Check articles.')
    put.add_argument('-q', '--query', nargs='*',
        help='The options for query.')

    pn = subParsers.add_parser('new', 
        help='Create some new content.')
    pn.add_argument('-t', '--type', type=str,
        choices=['post', 'page', 'tag', 'category'],
        help='Create a new content in wordpress.')
    pn.add_argument('-q', '--query', nargs='*',
        help='The options for query.')

    ps = subParsers.add_parser('show', 
        help='Show wordpress contents.')
    ps.add_argument('-t', '--type', type=str,
        choices=['post', 'page', 'draft',
            'option','tax','term',
            'category','tag',
            'medialib', 'mediaitem'],
        default='option',
        help='Content type of wordpress.')
    ps.add_argument('-n', '--number', type=int,
        default=10,
        help='The amount for GetPosts.')
    ps.add_argument('-o', '--orderby',
        choices=['post_modified', 'post_id'],
        default='post_id',
        help='To sort the result-set by one column.')
    ps.add_argument('-d', '--order',
        choices=['ASC', 'DESC'],
        default='DESC',
        help='To sort the records in a descending or a ascending order.')
    ps.add_argument('-q', '--query', nargs='*',
        help='The options for query.')

    pu = subParsers.add_parser('update', 
        help='Update wordpress contents.')
    pu.add_argument('-t', '--type', type=str,
        choices=['post', 'page', 'draft', 'option', 'tag', 'category'],
        default='post',
        help='Content type of wordpress.')
    pu.add_argument('-q', '--query', nargs='*',
        help='The options for query.')
    pu.add_argument('-o', '--output', type=str,
        help='Write output text to a file.')

    # Add site argument to new/update/show.
    for subp in (pn, ps, pu, put):
        subp.add_argument('-s', '--site', type=str, default='site',
            help='Set the site section in ini config files. Default value is "site".')

    args = parser.parse_args(args=argv)
    if args.sub_name:
        return args, subParsers.choices[args.sub_name]
    parser.print_help()
    return None, None

def main():
    homedir = os.path.expanduser('~')
    workdir = os.path.join(homedir, 'blog')
    conffile = os.path.join(homedir, Conf.INI_FILE)
    cachefile = os.path.join(homedir, Conf.CACHE_FILE)

    gcache = TermCache(cachefile)
    gcache.init()
    gconf = Conf(conffile, cachefile, gcache)
    if not gconf.init(workdir):
        exit(1)

    gargs, subParser = check_args()
    if gargs:
        modname = __package__ + '.' + gargs.sub_name
        mod = importlib.import_module(modname)
        mod.build(gconf, gcache, gargs, subParser)
