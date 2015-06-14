#########################################
# __main__.py
#
# Author zrong(zengrong.net)
# Creation 2014-11-18
#########################################

import os
import sys


if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)

import wpcmd

wpcmd.main()
