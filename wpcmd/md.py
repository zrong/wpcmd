#########################################
# md.py
#
# Author zrong(zengrong.net)
# Creation 2015-05-28
# Modification 2015-05-28
#########################################

import re
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import (FencedCodeExtension,
        FencedBlockPreprocessor)

def convert(txt):
    FencedBlockPreprocessor.FENCED_BLOCK_RE = re.compile(r'''
(?P<fence>^(?:~{3,}|`{3,}))[ ]*         # Opening ``` or ~~~
# Optional {, lang="lang" or lang
(\{?\.?(?:lang=")?(?P<lang>[a-zA-Z0-9_+-]*)"?)?[ ]*
# Optional highlight lines, single- or double-quote-delimited
(hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]*
}?[ ]*\n                                # Optional closing }
(?P<code>.*?)(?<=\n)
(?P=fence)[ ]*$''', re.MULTILINE | re.DOTALL | re.VERBOSE)
    fencedcode = FencedCodeExtension()
    codehilite = CodeHiliteExtension(linenums=False, guess_lang=False)
    md = markdown.Markdown(extensions=[
        'markdown.extensions.meta',
        'markdown.extensions.tables',
        fencedcode,
        codehilite,
        ])

    html = md.convert(txt)
    return html, md
