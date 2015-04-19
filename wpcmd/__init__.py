#########################################
# __init__.py
#
# Author zrong(zengrong.net)
# Creation 2014-11-18
#########################################

__all__ = ['write', 'wordpress']

import os
import sys
import logging
import importlib
import argparse
from zrong import slog, add_log_handler
import wpcmd.base

add_log_handler(slog,
    handler=logging.StreamHandler(sys.stdout),
    debug=logging.DEBUG)

class BlogError(Exception):
    pass

def check_args(argv=None):
    parser = argparse.ArgumentParser(prog='wpcmd')
    subParsers = parser.add_subparsers(dest='sub_name', help='sub-commands')

    pw = subParsers.add_parser('write', 
        help='Write *.md files.')
    pw.add_argument('-r', '--readme', action='store_true', 
        help='Build README.md.')
    pw.add_argument('-u', '--url', action='store_true', 
        help='Rewrite url.')
    pw.add_argument('-c', '--category', action='store_true', 
        help='Rewrite category.')
    pw.add_argument('-d', '--dirname', type=str, default='post',
        choices = ['post', 'page', 'draft', 'all'],
        help='Rewrite articles by type. The value is [post|page|draft|all].')
    pw.add_argument('-a', '--analytic', action='store_true',
        help='Analytic the articles.')
    pw.add_argument('--name', type=str,
        help='Provide a article name.')

    pn = subParsers.add_parser('new', 
        help='Create some new content.')
    pn.add_argument('-u', '--user', type=str, 
        help='Login username.')
    pn.add_argument('-p', '--password', type=str, 
        help='Login password.')
    pn.add_argument('-s', '--site', type=str, 
        help='Site url.')
    pn.add_argument('-t', '--type', type=str,
        choices=['post', 'page', 'tag', 'category'],
        default='post',
        help='Create a new content in wordpress.')
    pn.add_argument('-q', '--query', nargs='*',
        help='The options for query.')

    ps = subParsers.add_parser('show', 
        help='Show wordpress contents.')
    ps.add_argument('-u', '--user', type=str, 
        help='Login username.')
    ps.add_argument('-p', '--password', type=str, 
        help='Login password.')
    ps.add_argument('-s', '--site', type=str, 
        help='Site url.')
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
    pu.add_argument('-u', '--user', type=str, 
        help='Login username.')
    pu.add_argument('-p', '--password', type=str, 
        help='Login password.')
    pu.add_argument('-s', '--site', type=str, 
        help='Site url.')
    pu.add_argument('-t', '--type', type=str,
        choices=['post', 'page', 'draft', 'option', 'tag', 'category'],
        default='post',
        help='Content type of wordpress.')
    pu.add_argument('-q', '--query', nargs='*',
        help='The options for query.')

    args = parser.parse_args(args=argv)
    if args.sub_name:
        return args, subParsers.choices[args.sub_name]
    parser.print_help()
    return None, None

def main():
    gconf = wpcmd.base.Conf()
    workDir = os.path.abspath(
        os.path.join(os.path.split(
        os.path.abspath(__file__))[0], os.pardir))
    conffile = os.path.join(workDir, "build.conf.py")
    if os.path.exists(conffile):
        gconf.read_from_file(conffile)
    else:
        gconf.init(workDir, conffile)
        slog.info('Please modify build.conf.py!')
        exit(1)

    gargs, subParser = check_args()
    if gargs:
        _build(gargs.sub_name, gconf, gargs, subParser)
        pack = importlib.import_module(gargs.sub_name)
        pack.build(gconf, gargs, subParsers)
