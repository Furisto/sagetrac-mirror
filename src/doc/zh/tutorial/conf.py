# -*- coding: utf-8 -*-
#
# Sage documentation build configuration file, created by
# sphinx-quickstart on Thu Aug 21 20:15:55 2008.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys, os
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append(os.environ['SAGE_DOC'])
from common.conf import *

# General information about the project.
project = u"Sage Tutorial in Chinese"
name = u'tutorial-zh'
language = "zh"

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = project + " v"+release

# Output file base name for HTML help builder.
htmlhelp_basename = 'SageTutorial_zh'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
  ('index', 'SageTutorial.tex', u'Sage教程',
   u'Sage开发组', 'manual'),
]

#latex_preamble='\input{../../../../zh/tutorial/custom.sty}'
#latex_preamble = '\usepackage{ctex}\n\punctstyle{CCT}'

