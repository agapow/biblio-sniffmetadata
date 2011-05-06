#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Listing epub ebook metadata and perhaps renaming the book appropriately.

This script should be called::

	python epubmetareader.py [list|rename] book1.epub book2.epub ...
	
Due to some variations in the way metadata is actually written, this script
does a a bit of searching and cleaning up to best extract book information. If
the "list" command is used, this metadata is dumped to the screen. If "rename"
is used, the original file is renamed in the format::

	<first author surname> (<publication year>) <short title> (isbn<isbn>).epub
	
This only uses the standard Python library to do its magic and should be easily
modifiable.
"""

__author__ = "Paul-Michael Agapow (pma@agapow.net)"
__version__ = '0.1'


### IMPORTS

from xml.etree import ElementTree as et
from zipfile import ZipFile
from xml.dom.minidom import parseString
import copy
import re
from StringIO import StringIO
import types
import os 

from biblio.bibrecord.dublin import fields as DUBLIN_FIELDS


### CONSTANTS & DEFINES

OPF_NS = "http://www.idpf.org/2007/opf"
DC_NS = "http://purl.org/dc/elements/1.1/"

DENAMESPACE_RE = re.compile (r'^.+\}')

YEAR_RE = re.compile (r'^\d\d\d\d')

CLEAN_ISBN_RE = re.compile (r'[\- ]+')


### IMPLEMENTATION ###

def strip_namespace(tag):
	"""
	Remove the namespace portion of an Etree tagname.
	"""
	return DENAMESPACE_RE.sub ('', tag)
	

def clean_attribs (attrib_dict):
	return dict ([(strip_namespace(k).lower(), v) for k,v in attrib_dict.iteritems()])
	

def tag_to_metval (xml_tag):
	if xml_tag.text:
		val_name = xml_tag.text.strip()
	else:
		val_name = ''
	return MetaValue (val_name, clean_attribs(xml_tag.attrib))


class EpubMetaReader (object):
	def __init__ (self, path):
		self.zip = ZipFile (path, mode='r')
		
	def get_metadata (self):
		"""
		Search for and return metadata within the ebook.
		
		:Returns:
			A hash of the metadata tags found or `None` if nothing found.
			
		Note that if the metadata is found but is empty, an empty hash is returned.
		We follow this philosophy for the individual fields as well - if a field
		is not found, it doesn't appear in the metadata, but if it appears but is
		empty or cannot be parsed, an empty field appears in the metadata.
		
		"""
		# NOTE: a contents file with malformed XML will error, which is acceptable
		# XXX: other fields to looks at
		# - subject, type
		# - date (YYYY[-MM[-DD]]: a required 4-digit year, an optional 2-digit
		# month, and if the month is given, an optional 2-digit day of month.
		# The date element has one optional OPF event attribute. The set of values
		# for event are not defined by this specification; possible values may
		# include: creation, publication, and modification.)
		# Possible roles for creastors & contributors include:
		# Artist [art]	 Use for a person (e.g., a painter) who conceives, and perhaps also implements, an original graphic design or work of art, if specific codes (e.g., [egr], [etr]) are not desired. For book illustrators, prefer Illustrator [ill].
		# Author [aut]	 Use for a person or corporate body chiefly responsible for the intellectual or artistic content of a work. This term may also be used when more than one person or body bears such responsibility.
		# Editor [edt]	 Use for a person who prepares for publication a work not primarily his/her own, such as by elucidating text, adding introductory or other critical matter, or technically directing an editorial staff.
		# Illustrator [ill]	 Use for the person who conceives, and perhaps also implements, a design or illustration, usually to accompany a written text.
		# Translator [trl]
		contents = self.read_contents_file()
		if contents:
			con_tree = et.fromstring(contents)
			metadata_tag = "{%s}metadata" % OPF_NS
			m = con_tree.find(metadata_tag)
			if m:
				md_dict = MetadataDict()
				for t in ['creator', 'contributor', 'identifier', 'date', 'publisher', 'language', 'title', 'description']:
					elems = m.findall("{%s}%s" % (DC_NS, t))
					if elems != []:
						md_dict[t] = [tag_to_metval (x) for x in elems]
				return md_dict
		# no file, no xml or no metadata tag
		return None
		
	def read_contents_file (self):
		"""
		Find and return the contents of the ebook table of contents.
		"""
		contents_path = self.find_contents_file()
		if contents_path:
			return self.zip.read (self.find_contents_file())
		else:
			return None

	def find_contents_file (self):
		"""
		Return the path of the table of contents within the epub zip.
		
		:Returns:
			The location of the table of contents or `None` if it cannot be found
			
		While the location of the TOC is prescribed by the epub standard, in practice
		this is much violated. Therefore we looks for it in the variety of locations:
		
		1. The location given in the container file
		2. Within the OEBPS directory
		3. On the top level
		
		"""
		# possible locations for the toc
		possible_paths = [
			self.contents_path_from_container(),
			'OEBPS/content.opf',
			'OEBPS/Content.opf',
			'content.opf',
			'Content.opf',
		]
		# is there a file at any of these?
		zip_contents = self.zip.namelist()
		for p in possible_paths:
			if p in zip_contents:
				return p
		# unsucessful
		return None
		
	def read_container_file (self):
		"""
		Return the contents of the container file.
		"""
		# XXX: it *should* be here. Are there any variants?
		# TODO: need to cope with failure?
		return self.zip.read ('META-INF/container.xml')
		
	def contents_path_from_container (self):
		"""
		Return the location of the TOC file as given in the container file.
		
		:Returns:
			A path within the zip, or `None` if not found.
			
		"""
		# TODO: can we cope with namespace variants (but synonyms)?
		# XXX: are there any actual variants?
		container_text = self.read_container_file()
		if container_text:
			container_tree = et.fromstring(container_text)
			ns = "urn:oasis:names:tc:opendocument:xmlns:container"
			rootfile = container_tree.find("{%s}rootfiles/{%s}rootfile" % (ns, ns))
			if rootfile != None:
				return rootfile.attrib.get("full-path", None)
		return None
	
	
### END #######################################################################
