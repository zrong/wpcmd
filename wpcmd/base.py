#########################################
# base.py
#
# Author zrong(zengrong.net)
# Creation 2014-12-04
#########################################

import os
import re
import platform
import shutil
from xmlrpc.client import Fault
from datetime import (datetime, timedelta)
from zrong import slog
from zrong.base import DictBase, list_dir
from wordpress_xmlrpc import (Client, 
        WordPressPost, WordPressPage, WordPressTerm, WordPressMedia)
from wordpress_xmlrpc.exceptions import InvalidCredentialsError 
from wordpress_xmlrpc.methods.taxonomies import (GetTerms)

class Action(object):

    def __init__(self, gconf, gargs, gparser, gtermcache):
        self.conf = gconf
        self.args = gargs
        self.parser = gparser
        self.termcache = gtermcache
        self._wp = None
        self._update_site_config()

    def _update_site_config(self):
        if self.args.user:
            self.conf.site.user = self.args.user
        if self.args.password:
            self.conf.site.password = self.args.password
        if self.args.site:
            if self.args.site.rfind('xmlrpc.php')>0:
                self.conf.site.url = self.args.site
            else:
                removeslash = self.args.site.rfind('/')
                if removeslash == len(self.args.site)-1:
                    removeslash = self.args.site[0:removeslash]
                else:
                    removeslash = self.args.site
                self.conf.site.url = '%s/xmlrpc.php'%removeslash


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
        terms = self.conf[taxname]
        if not terms or force:
            results = self.wpcall(GetTerms(taxname))
            if results:
                self.termcache.save_terms(results, taxname)
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

    def get_terms_from_meta(self, categories, tags):
        terms = []
        if categories:
            for cat in categories:
                term = self.conf.get_term('category', cat)
                if not term:
                    slog.error('The category "%s" is not in wordpress.'
                            ' Please create it first.'%cat)
                    return None
                terms.append(term)
        if tags:
            for tag in tags:
                term = self.conf.get_term('post_tag', tag)
                if not term:
                    slog.error('The tag "%s" is not in wordpress.'
                            'Please create it first'%tag)
                    return None
                terms.append(term)
        return terms

    def wpcall(self, method):
        if not self._wp:
            self._wp = Client(self.conf.site.url, 
                    self.conf.site.user, 
                    self.conf.site.password)
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

class Conf(DictBase):

    ARTICLE_TYPES = ('post', 'page', 'draft')

    def save_to_file(self):
        super().save_to_file(self.conffile)

    def init(self, workDir, confFile):
        self.confile = confFile
        self.site = DictBase(
        {
            'user': 'user',
            'password': 'password',
            'url': 'http://you-wordpress-blog/xmlrpc.php',
        })
        self.directory = DictBase(
        {
            'work': workDir,
            'draft': 'draft',
            'post': 'post',
            'page': 'page',
            'media': 'media',
        })
        self.files = DictBase(
        {
            'ext': '.md',
            'draftfmt': 'draft_%s',
        })
        self.save_to_file()


    def is_article(self, posttype):
        return posttype in Conf.ARTICLE_TYPES

    def get_draft(self, name):
        """
        There are two kind of draft file in draft directory.
        One has published to wordpress and in draft status;
        One has beed not published to wordpress yet.
        """
        draftname = (self.files.draftfmt % str(name))+self.files.ext
        return self.get_path(self.directory.draft, draftname), draftname

    def get_new_draft(self, name=None):
        draftnames = list(list_dir(self.get_path(self.directory.draft)))
        draftfile, draftname = None, None
        if name:
            draftfile, draftname = self.get_draft(name)
            if draftname in draftnames:
                raise BlogError('The draft file "%s" is already existence!'%
                        draftname)
        else:
            name = 1
            draftfile, draftname = self.get_draft(name)
            while os.path.exists(draftfile):
                name += 1
                draftfile, draftname = self.get_draft(name)
        return draftfile, draftname

    def get_article(self, name, posttype):
        postname = name+self.files.ext
        if self.is_article(posttype):
            return self.get_path(self.directory[posttype], postname), postname
        return None, None

    def get_path(self, name, *path):
        workdir = os.path.join(self.directory.work, name)
        if path:
            return os.path.abspath(os.path.join(workdir, *path))
        return workdir

    def get_media(self, *path):
        mediadir = self.get_path(self.directory.media)
        if path:
            return os.path.join(mediadir, *path)
        return mediadir

    def get_mdfiles(self, posttype):
        for afile in os.listdir(self.get_path(posttype)):
            if afile.endswith('.md'):
                name = afile.split('.')[0]
                yield (posttype, name, os.path.join(posttype, afile))

class TermCache(DictBase):
    """ A cache for terms.
    """

    def __init__(self, filepath):
        self.cachefile = filepath

    def save_to_file(self):
        super().save_to_file(self.cachefile)

    def save_terms(self, terms, taxname):
        termdict = DictBase()
        for term in terms:
            self.save_term(term, taxname, termdict)
        self[taxname] = termdict
        self.save_to_file()

    def save_term(self, term, taxname, termdict=None):
        if termdict == None:
            termdict = self[taxname]
        termdict[term.slug] = DictBase({
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

