#########################################
# base.py
#
# Author zrong(zengrong.net)
# Creation 2014-12-04
# Modification 2015-10-18
#########################################

import os
import re
import platform
import shutil
from xmlrpc.client import Fault
from string import Template
from datetime import (datetime, timedelta)
import configparser
from wordpress_xmlrpc import (Client, 
        WordPressPost, WordPressPage, WordPressTerm, WordPressMedia)
from wordpress_xmlrpc.exceptions import InvalidCredentialsError 
from wordpress_xmlrpc.methods.taxonomies import (GetTerms)
from pkg_resources import (resource_filename, resource_string)
from rookout import slog
from rookout.base import (list_dir, read_file, write_file)
from rookout.conf import PYConf


class Conf(object):

    TPL_FILE = 'wpcmd.ini.tpl'
    PRE_NAME = '_' if platform.system() == 'Windows' else '.'
    INI_FILE = PRE_NAME+'wpcmd.ini'
    CACHE_FILE = PRE_NAME+'wpcmd.cache.py'

    ARTICLE_TYPES = ('post', 'page', 'draft')

    def __init__(self, conffile, cachefile, gcache):
        self.conffile = conffile
        self.cachefile = cachefile
        self.ini = configparser.ConfigParser()
        self.cache = gcache

    def init(self, workdir):
        if os.path.exists(self.conffile):
            self.read_from_file()
            return True

        tplstr = read_file(resource_filename('wpcmd', Conf.TPL_FILE))
        inistr = Template(tplstr).substitute(
            {'CONFFILE':self.conffile, 
            'CACHEFILE':self.cachefile,
            'WORK':workdir,
            })
        self.save_to_file(inistr)
        self.read_from_file()
        slog.info('Please modify %s !'%self.conffile)
        return False

    def __missing__(self, key):
        return None

    def __getattr__(self, name):
        return self.ini[name]

    def get(self, section, option):
        return self.ini.get(section, option, raw=True, fallback=None)

    def get_site(self, option):
        return self.get(self.site, option)

    def get_user(self):
        return self.get_site('user')

    def get_password(self):
        return self.get_site('password')

    def get_url(self, only_site=False):
        url = self.get_site('url')
        site = None
        if url.endswith('/xmlrpc.php'):
            site = url[:-11]
        elif url.endswith('/'):
            site = url[:-1]
            url = url + 'xmlrpc.php'
        else:
            site = url
            url = url + '/xmlrpc.php'
        if only_site:
            return site
        return url

    def save_to_file(self, inistr):
        write_file(self.conffile, inistr)

    def read_from_file(self):
        self.ini.read(self.conffile)

    def is_article(self, posttype):
        return posttype in Conf.ARTICLE_TYPES

    def get_draft(self, name):
        """
        There are two kind of draft file in draft directory.
        One has published to wordpress and in draft status;
        One has not been published to wordpress yet.
        """
        draftname = (self.get_site('draftfmt') % str(name))+self.get_site('ext')
        return self.get_work_path('draft', draftname), draftname

    def get_new_draft(self, name=None):
        draftdir = self.get_work_path('draft')
        if not os.path.exists(draftdir):
            os.makedirs(draftdir)
        draftnames = list(list_dir(draftdir))
        draftfile, draftname = None, None
        if name:
            draftfile, draftname = self.get_draft(name)
            if draftname in draftnames:
                raise WPError('The draft file "%s" is already existence!'%
                        draftname)
        else:
            name = 1
            draftfile, draftname = self.get_draft(name)
            while os.path.exists(draftfile):
                name += 1
                draftfile, draftname = self.get_draft(name)
        return draftfile, draftname

    def get_article(self, name, posttype):
        postname = name+self.get_site('ext')
        if self.is_article(posttype):
            return self.get_work_path(posttype, postname), postname
        return None, None

    def get_path(self, name, *path):
        workdir = os.path.join(self.get_site('work'), name)
        if path:
            return os.path.abspath(os.path.join(workdir, *path))
        return workdir

    def get_work_path(self, dirname, *path):
        workpath = self.get_path(self.get_site(dirname))
        if path:
            return os.path.join(workpath, *path)
        return workpath

    def get_mdfiles(self, posttype):
        for afile in os.listdir(self.get_work_path(posttype)):
            if afile.endswith(self.get_site('ext')):
                name = afile.split('.')[0]
                yield (posttype, name, os.path.join(posttype, afile))


class Action(object):

    def __init__(self, gconf, gtermcache, gargs, gparser):
        self.conf = gconf
        self.conf.site = gargs.site
        self.cache = gtermcache
        self.args = gargs
        self.parser = gparser
        self._wp = None

    def get_postid(self, as_list=False):
        if not self.args.query:
            return None
        if as_list:
            postids = []
            for postid in self.args.query:
                match = re.match(r'^(\d+)-(\d+)$', postid)
                if match:
                    a = int(match.group(1))
                    b = int(match.group(2))
                    for i in range(a,b+1):
                        postids.append(str(i))
                else:
                    postids.append(postid)
            return postids
        return self.args.query[0]

    def get_dict_from_query(self, query):
        if query:
            d = {}
            for v in query:
                value = v.split('=')
                d[value[0]] = value[1]
            return d
        return None

    def get_term_query(self):
        typ = self.args.type
        q = self.args.query
        query = []
        if typ == 'term':
            query = q
        else:
            if typ == 'tag':
                typ = 'post_tag'
            query.append(typ)
            if q and len(q)>0:
                query.append(q[0])
        return query

    def get_terms_from_wp(self, query, force=False):
        if not query or len(query)== 0:
            slog.error('Please provide a taxonomy name! You can use '
                    '"show -t tax" to get one.')
            return None
        taxname = query[0]
        slug = query[1] if len(query)>1 else None
        terms = self.cache[taxname]
        if not terms or force:
            results = self.wpcall(GetTerms(taxname))
            if results:
                self.cache.save_terms(results, taxname)
        if terms and slug:
            return terms[slug]
        return terms

    def print_result(self, result):
        if isinstance(result, WordPressTerm):
            slog.info('id=%s, group=%s, '
                    'taxnomy_id=%s, name=%s, slug=%s, '
                    'parent=%s, count=%d', 
                    result.id, result.group, 
                    result.taxonomy_id, result.name, result.slug,
                    result.parent, result.count)
        elif isinstance(result, WordPressPost):
            slog.info('id=%s, date=%s, date_modified=%s, '
                    'slug=%s, title=%s, post_status=%s, post_type=%s', 
                    result.id, str(result.date), str(result.date_modified), 
                    result.slug, result.title,
                    result.post_status, result.post_type)
        elif isinstance(result, WordPressMedia):
            slog.info('id=%s, parent=%s, title=%s, '
                    'description=%s, caption=%s, date_created=%s, link=%s, '
                    'thumbnail=%s, metadata=%s', 
                    result.id, result.parent, result.title, 
                    result.description, result.caption, str(result.date_created), 
                    result.link,
                    result.thumbnail, result.metadata)
        else:
            slog.info(result)

    def print_results(self, results):
        if isinstance(results, list):
            for result in results:
                self.print_result(result)
        elif isinstance(results, dict):
            for k,v in results.items():
                slog.info('%s %s'%(k, str(v)))
        else:
            self.print_result(results)

    def get_datetime(self, datestring):
        dt = datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')
        return dt - timedelta(hours=8)

    def wpcall(self, method):
        if not self._wp:
            self._wp = Client(self.conf.get_url(),
                    self.conf.get_user(),
                    self.conf.get_password())
        try:
            results = self._wp.call(method)
        except InvalidCredentialsError as e:
            slog.error(e)
            return None
        except Fault as e:
            slog.error(e)
            return None
        return results

    def go(self):
        pass

    def build(self):
        if self.args.type:
            self.go()
        elif self.parser:
            self.parser.print_help()


class TermCache(PYConf):
    """ A cache for terms.
    """

    def __init__(self, filepath):
        self.cachefile = filepath

    def init(self):
        if os.path.exists(self.cachefile):
            super().read_from_file(self.cachefile)

    def save_to_file(self):
        super().save_to_file(self.cachefile)

    def save_terms(self, terms, taxname):
        termdict = PYConf()
        for term in terms:
            self.save_term(term, taxname, termdict)
        self[taxname] = termdict
        self.save_to_file()

    def save_term(self, term, taxname, termdict=None):
        if termdict == None:
            termdict = self[taxname]
        termdict[term.slug] = PYConf({
            'id':term.id,
            'group':term.group,
            'taxonomy':term.taxonomy,
            'taxonomy_id':term.taxonomy_id,
            'name':term.name,
            'slug':term.slug,
            'description':term.description,
            'parent':term.parent,
            'count':term.count,
                })

    def get_term(self, taxname, slug):
        if not self[taxname]:
            return None
        if not self[taxname][slug]:
            return None
        termdict = self[taxname][slug]
        term = WordPressTerm()
        term.id = termdict['id']
        term.group = termdict['group']
        term.taxonomy = termdict['taxonomy']
        term.taxonomy_id = termdict['taxonomy_id']
        term.name = termdict['name']
        term.slug = termdict['slug']
        term.description = termdict['description']
        term.parent = termdict['parent']
        term.count = termdict['count']
        return term

    def get_terms_from_meta(self, categories, tags):
        terms = []
        if categories:
            for cat in categories:
                term = self.get_term('category', cat)
                if not term:
                    slog.error('The category "%s" is not in wordpress.'
                            ' Please create it first.'%cat)
                    return None
                terms.append(term)
        if tags:
            for tag in tags:
                term = self.get_term('post_tag', tag)
                if not term:
                    slog.error('The tag "%s" is not in wordpress.'
                            'Please create it first'%tag)
                    return None
                terms.append(term)
        return terms
