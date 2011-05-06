

def rename_file (p, md):
	# tmpl = <1st author surname> (<year>) <short title> (ISBN<isbn>)
	UNKNOWN = 'UNKNOWN'
	
	# grab the first author or creator
	auths = md.authors() or md.creators()
	if auths:
		# extract their surname
		first_auth = auths[0]
		name = first_auth.attribs.get('file-as', '').split(',')[0] \
			or first_auth.value.split(' ')[-1] \
			or UNKNOWN
		
	# get year
	pubdate = None
	dateval = md.publication_date() or md.get('date')
	if dateval:
		earliest_date = sorted (dateval, cmp=lambda x, y: cmp (x.value, y.value))[0]
		m = YEAR_RE.match (earliest_date.value)
		if m:
			pubdate = m.group(0)
	if not pubdate:
		pubdate = UNKNOWN
		
	# get title
	short_title = None
	title = md.get('title')
	if title:
		short_title = title.value.split(':')[0]
	else:
		short_title = UNKNOWN
	
	# get isbn
	isbn = None
	ids = md.isbn()
	if ids:
		isbn = CLEAN_ISBN_RE.sub ('', ids[0].value).upper()
	else:
		isbn = UNKNOWN
		for x in md.identifiers():
			id_val = CLEAN_ISBN_RE.sub ('', x.value).upper()
			if len(id_val) in [10, 13]:
				isbn = id_val
				break
	
	# build name
	new_file_name = u"%(name)s (%(pubdate)s) %(short_title)s (isbn%(isbn)s).epub" % {
		'name': name,
		'pubdate': pubdate,
		'short_title': short_title,
		'isbn': isbn,
	}
	print new_file_name
	os.rename (p, new_file_name)
	

def pretty_print(element):
	txt = et.tostring(element)
	return parseString(txt).toprettyxml()

