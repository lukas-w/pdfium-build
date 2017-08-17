#!/usr/bin/env python
# coding=utf8

# Script to patch BUILD.gn
# Inserts the FPDFSDK_EXPORTS define into "pdfium_common_config"

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals, print_function

import json
import re
import tatsu
import os.path

from shutil import copyfile

# Minimal grammar that allows us splitting the file into words and '{' blocks '}'
grammar = r'''
@@eol_comments :: /#.*?$/

start = StatementList $ ;
Statement     = call:Word block:Block | statement:Word | /\s+/;
Block = "{" statements:StatementList "}" ;
Word = /[^\s\{\}]+/ ;
StatementList = { Statement } ;
'''

define = '  defines += ["FPDFSDK_EXPORTS"]\n'

parser = tatsu.compile(grammar, asmodel=True)

fo_name = 'BUILD.gn'
fi_name = fo_name + '.bak'

# Keep a backup
if not os.path.isfile(fi_name):
	copyfile(fo_name, fi_name)

with open(fi_name, 'r') as fi, open(fo_name, 'w') as fo:
	text = fi.read()
	model = parser.parse(text, parseinfo=True)

	# Find config("pdfium_common_config")
	for statement in model:
		if 'call' in statement and statement.call == 'config("pdfium_common_config")':
			block = statement.block

			pos = block.parseinfo.endpos - 1;
			mod_text = text[:pos] + define + text[pos:]
			fo.write(mod_text)
			print("Patched BUILD.gn at line", text[:pos].count('\n') + 1)
			exit(0)

	print("Failed patching BUILD.gn. Couldn't find pdfium_common_config block")
