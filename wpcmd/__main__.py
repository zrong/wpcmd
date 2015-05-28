#########################################
# __main__.py
#
# Author zrong(zengrong.net)
# Creation 2014-11-18
#########################################

import os
import sys


try:
    import zrong
except ImportError:
    sys.path.insert(0, os.getenv('zrongpy'))

if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)

import wpcmd

wpcmd.main()
