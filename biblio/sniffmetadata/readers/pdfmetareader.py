#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
"""


### IMPORTS

### CONSTANTS & DEFINES

### IMPLEMENTATION ###

class PdfMetaReader (object):
	def __init__ (self, path):
		from pyPdf import PdfFileReader
		self.doc = PdfFileReader(open(p, 'rb'))
		
	def get_metadata (self):
		return self.rdr.documentInfo, self.rdr.xmpMetadata


### END #######################################################################
