#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
An abstract base class for ebook metadata readers.

This exists soley to ensure some conformity in the interface of readers, and
provides two functions:

* read: read the metadata structure(s) within the document. Different documents
  may return different structures.
  
* munge: read the metadata and convert it to a universal form. This should call
  read and may mangle or transform the data based on heuristics.

"""

__author__ = "Paul-Michael Agapow (pma@agapow.net)"


### IMPORTS

### CONSTANTS & DEFINES

### IMPLEMENTATION ###

class BaseMetadataReader (object):
	
	# override in subclass
	handled_exts = []
	
	def __init__ (self, path_or_hndl):
		self._file = self._open_file (path_or_hndl)
		
	def __del__ (self):
		"""
		D'tor, which cleans up including closing ebook file, if necessary.
		"""
		self._close_file()
		
	def _open_file (self, path_or_hndl):
		"""
		Open and prep ebook file, if necessary.
		"""
		if has_attr (path_or_hndl, 'read'):
			self._opened_file = False
			return path_or_hndl
		else:
			self._opened_file = True
			return open (path_or_hndl, 'rb')
			
		
	def _close_file (self):
		"""
		Close the ebook file, if necessary.
		"""
		if self._opened_file:
			self._file.close()
		
	def read_metadata (self):
		"""
		Search for and return metadata within the ebook.
		
		:Returns:
			Format dependant metadata.
			
		"""
		pass
	
	def read_metadata_as_dublincore (self):
		return self.munge_metadata_to_dublincore (self.read_metadata())
		
	def munge_metadata_to_dublincore (self, raw_metadata):
		pass
	
	
	
### END #######################################################################
