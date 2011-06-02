#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
"""


### IMPORTS

from datetime import datetime

from biblio.bibrecord.dublin import DublinCoreCollection

from basemetadatareader import BaseMetadataReader


### CONSTANTS & DEFINES

# map fields from one schema to other
DOCINFO_TO_DUBLIN = {
	'Author': 'authors',
	'Title': 'titles',
	'CreationDate': 'date_created',
	'ModDate': 'date_modified',
	'Creator': 'creator',
	'Producer': 'publishers',
}


### IMPLEMENTATION ###

def date_from_string (s):
	return datetime.strptime(s[:8].replace("-", ""), "%Y%m%d").date()
	

class PdfMetaReader (BaseMetadataReader):
	def _open_file (self, path):
		from pyPdf import PdfFileReader
		return PdfFileReader(open(path, 'rb'))
		
	def _close_file (self):
		pass
		
	def read_metadata (self):
		return self._file.documentInfo, self._file.xmpMetadata
	
	def munge_docinfo_to_dublincore (self, docinfo):
		clean_dict = {}
		for k, v in docinfo.iteritems():
			if k.startswith('/'):
				k = k[1:]
			if v.startswith ('D:'):
				v = date_from_string (v[2:])
			
			clean_dict[k] = v
		return clean_dict
		
	def munge_metadata_to_dublincore (self, md):
		docinfo, xmp = md
		print self.munge_docinfo_to_dict (docinfo)
		DublinCoreCollection


### END #######################################################################
