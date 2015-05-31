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

# gvdir = graphviz directory
def convert(txt, gv_odir, gv_bdir='media/draft', gv_namepre=""):
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

    md = markdown.Markdown(
            extensions=[
                'markdown.extensions.meta',
                'markdown.extensions.tables',
                fencedcode,
                codehilite,
                'graphviz',
                ],
            extension_configs={
                'graphviz':{
                    'FORMAT':'png', 
                    'OUTPUT_DIR':gv_odir, 
                    'BASE_DIR':gv_bdir,
                    'NAME_PRE':gv_namepre}
                }
            )

    html = md.convert(txt)
    return html, md, '\n'.join(md.lines)
