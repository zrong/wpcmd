#########################################
# show.py
#
# Author zrong(zengrong.net)
# Creation 2014-12-01
# Modification  2015-10-18
#########################################

from rookout import slog
from wpcmd.base import Action
from functools import wraps
from wordpress_xmlrpc import (WordPressPost, WordPressPage)
from wordpress_xmlrpc.methods.posts import (GetPosts, GetPost)
from wordpress_xmlrpc.methods.options import GetOptions
from wordpress_xmlrpc.methods.taxonomies import (GetTaxonomies)
from wordpress_xmlrpc.methods.media import (GetMediaLibrary, GetMediaItem)

class ShowAction(Action):

    def _print_results(fn):
        def _real_print(self):
            method = fn(self)
            if not method:
                return
            results = self.wpcall(method)
            if results:
                self.print_results(results)
            else:
                slog.warning('No results.')
        return _real_print

    @_print_results
    def _show_page(self):
        field = {'post_type':'page'}
        field['number'] = self.args.number
        field['orderby'] = self.args.orderby
        field['order'] = self.args.order

        if self.args.query:
            return GetPost(self.get_postid(), result_class=WordPressPage)
        return GetPosts(field, result_class=WordPressPage)

    @_print_results
    def _show_post(self):
        field = {}
        field['number'] = self.args.number
        field['orderby'] = self.args.orderby
        field['order'] = self.args.order

        if self.args.query:
            return GetPost(self.get_postid())
        return GetPosts(field)

    @_print_results
    def _show_options(self):
        return GetOptions([])

    @_print_results
    def _show_tax(self):
        return GetTaxonomies()

    def _show_term(self):
        query = self.get_term_query()
        info = str(query)
        terms = self.get_terms_from_wp(query)
        if terms:
            self.print_results(terms)
        else:
            slog.warning('No term %s!'%info)

    @_print_results
    def _show_medialib(self):
        field = {}
        field['number'] = self.args.number
        extra = self.get_dict_from_query(self.args.query)
        if extra:
            for k,v in extra.items():
                field[k] = v
        slog.info("field:%s", field)
        return GetMediaLibrary(field)

    @_print_results
    def _show_mediaitem(self):
        if not self.args.query or len(self.args.query) == 0:
            slog.error('Please provide a attachment_id!')
            return None
        return GetMediaItem(self.args.query[0])

    def go(self):
        print(self.args)
        if self.args.type == 'post':
            self._show_post()
        elif self.args.type == 'page':
            self._show_page()
        elif self.args.type == 'draft':
            for adir, aname, afile in self.conf.get_mdfiles('draft'):
                slog.info(afile)
        elif self.args.type == 'option':
            self._show_options()
        elif self.args.type == 'tax':
            self._show_tax()
        elif self.args.type in ('term', 'category', 'tag'):
            self._show_term()
        elif self.args.type == 'medialib':
            self._show_medialib()
        elif self.args.type == 'mediaitem':
            self._show_mediaitem()


def build(gconf, gcache, gargs, parser=None):
    action = ShowAction(gconf, gcache, gargs, parser)
    action.build()
