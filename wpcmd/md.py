#########################################
# md.py
#
# Author zrong(zengrong.net)
# Creation 2015-05-28
# Modification 2015-06-11
#########################################

import re
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension

# gvdir = graphviz directory
def convert(txt, gv_odir, gv_bdir='media/draft', gv_namepre=""):
    codehilite = CodeHiliteExtension(linenums=False, guess_lang=False)

    md = markdown.Markdown(
            extensions=[
                'wpcmd.mde.metadata',
                'markdown.extensions.tables',
                codehilite,
                'wpcmd.mde.fenced_code_extra',
                ],
            extension_configs={
                'fenced_code_extra':{
                    'graphviz':{
                        'OUTPUT_DIR':gv_odir,
                        'BASE_URL':gv_bdir,
                        'NAME_PRE':gv_namepre},
                    }
                }
            )

    html = md.convert(txt)

    graphviz = _get_extra_output(md, 'graphviz')
    if graphviz:
        # The text will inclued a content with all converted image from graphviz codes.
        # We need replace original text use this text to avoid the repeted conversion from graphviz codes.
        txt = graphviz['text']

    return html, md, txt

def _get_extra_output(md, name):
    extra_output = getattr(md, 'fenced_code_extra_output', None)
    if not extra_output:
        return None
    return extra_output.get(name)

