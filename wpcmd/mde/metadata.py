#########################################
# mdx_metadata.py
#
# metadata handing for markdown using sorteddict.
#
# Modifier zrong(zengrong.net)
# Creation 2015-06-07
# Modification 2015-06-10
#########################################

"""
Meta Data Extension for Python-Markdown
=======================================

This extension adds Meta Data handling to markdown.

See <https://pythonhosted.org/Markdown/extensions/meta_data.html> for documentation.

Original code Copyright 2007-2008 [Waylan Limberg](http://achinghead.com).

All changes Copyright 2008-2014 The Python Markdown Project

License: [BSD](http://www.opensource.org/licenses/bsd-license.php) 

"""

import re
from collections import OrderedDict
from markdown import Extension
from markdown.preprocessors import Preprocessor

# Global Vars
META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
META_MORE_RE = re.compile(r'^[ ]{4,}(?P<value>.*)')

class MetadataExtension (Extension):
    """ Meta-Data extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add MetaPreprocessor to Markdown instance. """

        md.preprocessors.add("metadata", MetadataPreprocessor(md), ">normalize_whitespace")

class Metadata(OrderedDict):

    # def __getattr__(self, name):
    #     return self[name]

    # def __setattr__(self, name, value):
    #     self[name] = value
    #     
    # def __delattr__(self, name):
    #     del self[name]

    def text(self):
        lines = []
        for key, value in self.items():
            lines.append('%s: %s'%(key, ",".join(value)))
        return '\n'.join(lines)

class MetadataPreprocessor(Preprocessor):
    """ Get Meta-Data. """

    def run(self, lines):
        """ Parse Meta-Data and store in Markdown.Meta. """
        meta = Metadata()
        key = None
        while lines:
            line = lines.pop(0)
            if line.strip() == '':
                break # blank line - done
            m1 = META_RE.match(line)
            if m1:
                key = m1.group('key').lower().strip()
                value = m1.group('value').strip()
                try:
                    meta[key].append(value)
                except KeyError:
                    meta[key] = [value]
            else:
                m2 = META_MORE_RE.match(line)
                if m2 and key:
                    # Add another line to existing key
                    meta[key].append(m2.group('value').strip())
                else:
                    lines.insert(0, line)
                    break # no meta data - done
        self.markdown.metadata = meta
        return lines
        

def makeExtension(*args, **kwargs):
    return MetadataExtension(*args, **kwargs)

