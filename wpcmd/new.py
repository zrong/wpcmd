########################################
# new.py
# 
# Author zrong(zengrong.net)
# Creation 2014-12-01
# Modification 2015-10-18
########################################
import shutil
import datetime
from collections import OrderedDict
from rookout import slog
from rookout.base import (write_file)
from wpcmd.base import Action
from wordpress_xmlrpc import (WordPressTerm)
from wordpress_xmlrpc.methods.taxonomies import (NewTerm,GetTerm)
from wpcmd import WPError

metatpl = [
    ('title', ''),
    ('date', ''),
    ('modified', ''),
    ('author', ''),
    ('postid', '$POSTID'),
    ('slug', '$SLUG'),
    ('nicename', ''),
    ('attachments', '$ATTACHMENTS'),
    ('posttype', ''),
    ('poststatus', 'draft'),
    ]

class NewAction(Action):

    def _new_draft(self):
        name = None
        if self.args.query:
            name = self.args.query[0]
        try:
            dfile, dname = self.conf.get_new_draft(name)
        except WPError as e:
            slog.critical(e)
            return
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        metatxt = []
        tpl = OrderedDict(metatpl)
        tpl['date'] = dt
        tpl['modified'] = dt
        tpl['author'] = self.conf.get_user()
        tpl['posttype'] = self.args.type
        if self.args.type == 'post':
            tpl['tags'] = ''
            tpl['category'] = 'technology'

        for k,v in tpl.items():
            metatxt.append('%s: %s'%(k, v))

        write_file(dfile, '\n'.join(metatxt))
        slog.info('The draft file "%s" has created.'%dfile)

    def _new_term(self):
        if not self.args.query or len(self.args.query)<1:
            slog.error('Provide 1 arguments at least please.')
            return
        query = self.get_term_query()
        print('query:', query)
        term = self.get_terms_from_wp(query, force=True)
        print(term)
        if term:
            slog.error('The term "%s" has been in wordpress.'%self.args.query[0])
            return
        taxname = query[0]
        slug = self.args.query[0]
        name = self.args.query[1] if len(self.args.query)>1 else slug
        term = WordPressTerm()
        term.slug = slug
        term.name = name
        term.taxonomy = taxname
        if len(self.args.query)>2:
            term.description = self.args.query[2]
        termid = self.wpcall(NewTerm(term))
        if not termid:
            return
        term = self.wpcall(GetTerm(taxname, termid))
        if not term:
            return
        slog.info('The term %s(%s) has created.'%(name, termid))
        self.cache.save_term(term, taxname)
        self.cache.save_to_file()
        slog.info('The term %s has saved.'%name)

    def go(self):
        print(self.args)
        if self.args.type in ('post','page'):
            self._new_draft()
        elif self.args.type in ('category', 'tag'):
            self._new_term()


def build(gconf, gcache, gargs, parser=None):
    action = NewAction(gconf, gcache, gargs, parser)
    action.build()

