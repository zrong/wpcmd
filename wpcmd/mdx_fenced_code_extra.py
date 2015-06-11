#########################################
# mdx_fenced_extra.py
#
# Author zrong(zengrong.net)
# Creation 2015-06-07
# Modification 2015-06-07
#########################################

"""
Fenced Code Extra for Fenced Code Extension of Python Markdown
===============================================================

This extension adds some extra functions to Fenced Code Blocks.

See <http://zengrong.net> for documentation.

Original code Copyright 2015 [Jacky Tsang](http://zengrong.net/).

The code of Fenced Code Extension Copyright 2007-2008 [Waylan Limberg](http://achinghead.com/).

All changes Copyright 2008-2014 The Python Markdown Project

License: [BSD](http://www.opensource.org/licenses/bsd-license.php) 
"""

import os
import re
import subprocess
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import (FencedCodeExtension,
        FencedBlockPreprocessor)

class FencedCodeExtraExtension(FencedCodeExtension):

    def __init__(self, **kwargs):
        self.config = {
                'graphviz':{},
                }
        if kwargs:
            for key, value in kwargs.items():
                self.config[key] = value

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockExtraPreprocessor to the Markdown instance. """
        md.registerExtension(self)

        md.preprocessors.add('fenced_code_extra',
                                 FencedBlockExtraPreprocessor(self, md),
                                 ">normalize_whitespace")

class CommentProcessor(object):
    # Opening ``` or ~~~ , start from # is a comment
    RE = re.compile(r'(?P<fence>^(?:~{3,}|`{3,}))[ ]*\#.*?(?<=\n)(?P=fence)[ ]*$', 
            re.MULTILINE | re.DOTALL)

    def __init__(self,  lines, config):
        self.lines = lines
        self.config = config

    def run(self):
        text = "\n".join(self.lines)
        m = self.RE.search(text)
        if not m:
            return None
        while True:
            if m:
                # Remove comment codes
                text = '%s\n%s'% (text[:m.start()], text[m.end():])
            else:
                break
            m = self.RE.search(text)

        return text.split("\n")

class GraphvizProcessor(object):
    RE = re.compile(r'''
# Opening ```graphviz or ~~~graphviz
(?P<fence>^(?:~{3,}|`{3,}))[ ]*graphviz_*
# Optional {, and lang
(\{?\.?(?P<lang>[a-zA-Z0-9_+-]*))?[ ]*
# Optional show type, name type, single- or double-quote-delimited
(config=(?P<quot>"|')(?P<config>.*?)(?P=quot))?[ ]*
}?[ ]*\n                                # Optional closing }
(?P<code>.*?)(?<=\n)
(?P=fence)[ ]*$''', re.MULTILINE | re.DOTALL | re.VERBOSE)
    FORMATTERS = ["dot", "neato", "lefty", "dotty"]
    SHOW_TYPES = ['image', 'code', 'codeandimage']

    def __init__(self,  lines, config):
        self.lines = lines
        self.config = config
        self.charts = []

    def get_graph_config(self, m, num):
        conf = {}
        codearg = m.group('config' or '')
        conf['config'] = codearg
        argdict = {}
        if codearg:
            argslist = codearg.split(',')
            for arg in argslist:
                arglist = arg.split('=')
                argdict[arglist[0]] = arglist[1]
        conf['type'] = argdict.get('type', 'png')
        conf['show'] = argdict.get('show', 'image').lower()
        conf['name'] = argdict.get('name', 'graphviz')

        conf['formatter'] = m.group('lang') or 'dot'
        conf['code'] = m.group('code')
        conf['output_dir'] = self.config.get('OUTPUT_DIR')
        conf['base_url'] = self.config.get('BASE_URL')
        conf['binary_path'] = self.config.get('BINARY_PATH', '')
        conf['name_pre'] = self.config.get('NAME_PRE', '')

        assert(conf['output_dir'] or conf['base_url'])
        assert(conf['show'] in self.SHOW_TYPES)
        assert(conf['formatter'] in self.FORMATTERS)

        conf['graph_num'] = num
        if conf['name_pre']:
            filename = '%s-%s-%s.%s'%(conf['name_pre'], conf['name'], num, conf['type'])
        else:
            filename = '%s-%s.%s'%(conf['name'], num, conf['type'])
        filepath = os.path.join(conf['output_dir'], filename)
        fileurl = conf['base_url'] + filename

        conf['filename'] = filename
        conf['filepath'] = filepath
        conf['fileurl'] = fileurl

        return conf

    def run(self):
        text = "\n".join(self.lines)
        self.graph_num = 0
        m = self.RE.search(text)
        if not m:
            return None
        while True:
            if m:
                graph_conf = self.get_graph_config(m, self.graph_num)
                # print(graph_conf)

                placeholder = self.graph(graph_conf)
                graph_conf['placeholder'] = placeholder
                self.charts.append(graph_conf)
                text = '%s\n%s\n%s'% (text[:m.start()], placeholder, text[m.end():])
            else:
                break

            self.graph_num += 1
            m = self.RE.search(text)

        return text.split("\n")

    def graph(self, conf):
        "Generates a graph from code and returns a string containing n image link to created graph."
        show = conf['show']
        image = ''
        code = ''
        has_image = 'image' in show
        if has_image:
            cmd = "%s%s -T%s" % (conf['binary_path'], conf['formatter'], conf['type'])
            # print('cmd', cmd)
            p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
            p.stdin.write(conf['code'].encode())
            p.stdin.close()
            # p.wait()
            with open(conf['filepath'], 'wb') as fout:
                fout.write(p.stdout.read())
            image = "![Graphviz chart %s](%s)" % (conf['filename'], conf['fileurl'])
            # Set graphviz to comment
            code = '``` #graphviz %s\n%s\n```'%(conf['config'], conf['code'])
        if show in ('code', 'codeandimage'):
            # Remove graphviz's flag, avoid to reinterpret
            code = '```\n%s\n```'%conf['code']
        return '%s%s%s'%(code, ('\n' if image else ''), image)

class FencedBlockExtraPreprocessor(FencedBlockPreprocessor):
    FENCED_BLOCK_RE = re.compile(r'''
(?P<fence>^(?:~{3,}|`{3,}))[ ]*         # Opening ``` or ~~~
# Optional {, lang="lang" or lang
(\{?\.?(?:lang=")?(?P<lang>[a-zA-Z0-9_+-]*)"?)?[ ]*
# Optional highlight lines, single- or double-quote-delimited
(hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]*
}?[ ]*\n                                # Optional closing }
(?P<code>.*?)(?<=\n)
(?P=fence)[ ]*$''', re.MULTILINE | re.DOTALL | re.VERBOSE)

    def __init__(self, extension_instance, md):
        super(FencedBlockExtraPreprocessor, self).__init__(md)
        self.md_inst = md
        self.ext_inst = extension_instance
        self.extra_output = {}

    def run(self, lines):
        # Process comment fence
        processor = CommentProcessor(lines, self.ext_inst.config.get('comment'))
        new_lines = processor.run()
        if new_lines != None:
            lines = new_lines

        #  graphviz fence
        processor = GraphvizProcessor(lines, self.ext_inst.config.get('graphviz'))
        new_lines = processor.run()
        if new_lines != None:
            lines = new_lines
            self.extra_output['graphviz'] = {
                    "charts":processor.charts,
                    "text":'\n'.join(lines)
                    }

        # Save extra_output dictionary into markdown instance.
        if self.extra_output:
            self.md_inst.fenced_code_extra_output = self.extra_output

        # Process original fenced_code
        return super(FencedBlockExtraPreprocessor, self).run(lines)

def makeExtension(*args, **kwargs):
    return FencedCodeExtraExtension(*args, **kwargs)
