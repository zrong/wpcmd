#########################################
# write.py
#
# Author zrong(zengrong.net)
# Creation 2014-11-18
# Modification 2015-06-20
#########################################

import os
import re
import markdown
import shutil
from operator import (attrgetter, itemgetter)
from datetime import date
from rookout import slog
from rookout.base import read_file, list_dir
from wpcmd.base import Action

class WriteAction(Action):

    def _write_list(self, adir, rf):
        rf.write('\n\n# '+adir+'\n\n')
        is_post = adir == 'post'
        dir_path = self.conf.get_path(adir)
        names = []
        for adir, name, fpath in self.conf.get_mdfiles(adir):
            title, time = self._get_title_and_date(os.path.join(dir_path, name+'.md'))
            if not title or not time:
                continue
            names.append({'name':name,'title':title,'time':time})
        if is_post:
            for item in names:
                item['index'] = int(item['name'])
                t = item['time'].split('-')
        else:
            for item in names:
                t = item['time'].split('-')
                item['index'] = date(int(t[0]), int(t[1]), int(t[2]))
        #names.sort(key=lambda item : item['index'])
        names.sort(key=itemgetter('index'))
        names = ['1. {time} \[**{name}**\] [{title}]'
        '(http://zengrong.net/post/{name}.htm)'.format(**item) for item in names]
        rf.write('\n'.join(names))

    def _get_title_and_date(self, path):
        title = None
        time = None
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.lower().startswith('title:'):
                    title = line[6:].strip()
                    title = title.replace('_', r'\_')
                    continue
                if line.lower().startswith('date:'):
                    time = line[6:16]
                    continue
                if time and title:
                    break
        if not time or not title:
            slog.error('There is NOT title or date in this article: [%s]!'%path)
            return None, None
        return title, time

    def _write_readme(self):
        with open(self.conf.get_path('README.md'), 'w', encoding='utf-8', newline='\n') as f:
            f.write("[zrong's blog](http://zengrong.net) 中的所有文章\n")
            f.write('==========\n\n----------')
            self._write_list('page', f)
            self._write_list('post', f)

    def _rewrite_url(self, dirname):
        """
        Get wrong URL form articles, then convert them to a correct pattern.
        """

        url = re.compile(r'\]\(/\?p=(\d+)\)', re.S)
        for adir, name, fpath in self.conf.get_mdfiles(dirname):
            content = None
            fpath = os.path.join(adir, afile)
            with open(fpath, 'r', encoding='utf-8', newline='\n') as f:
                content = f.read()
                matchs = url.findall(content)
                if len(matchs) > 0:
                    print(afile, matchs)
                    for num in matchs:
                        content = content.replace('](/?p=%s'% num,
                                '](http://zengrong.net/post/%s.htm'%num)
                else:
                    content = None
            if content:
                with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
                    print(fpath)

    def _rewrite_category(self):
        md = markdown.Markdown(extensions=[
            'markdown.extensions.meta',
            ])
        num = 0
        for adir,name,fpath in self.conf.get_mdfiles('post'):
            md.convert(read_file(fpath))
            cats = [cat.strip() for cat in md.Meta['category'][0].split(',')]
            if len(cats)>1:
                print(name, cats)
                num = num + 1
        print(num)

    def _write_analytic(self):
        if args.name:
            match = re.match(r'^(\d*)-(\d*)$', args.name)
            a,b = None,None
            if match:
                if match.group(1):
                    a = int(match.group(1))
                if match.group(2):
                    b = int(match.group(2))
                dirlist = []
                for f in list_dir(conf.get_path(args.dirname)):
                    if not f.endswith('.md'):
                        continue
                    fname = int(f.split('.')[0])
                    if a != None:
                        if fname < a:
                            continue
                    if b != None:
                        if fname > b:
                            continue
                    dirlist.append(fname)
                abc = sorted(dirlist)
                slog.info('\n'.join([str(item) for item in sorted(dirlist)]))

    # rewrite Action._update_site_config
    def _update_site_config(self):
        pass

    def build(self):
        print(self.args)
        noAnyArgs = True
        if self.args.readme:
            self._write_readme()
            noAnyArgs = False
        if self.args.category:
            self._rewrite_category()
            noAnyArgs = False
        if self.args.analytic:
            _write_analytic()
            noAnyArgs = False

        if noAnyArgs and self.parser:
            self.parser.print_help()

def build(gconf, gcache, gargs, parser=None):
    action = WriteAction(gconf, gcache, gargs, parser)
    action.build()
