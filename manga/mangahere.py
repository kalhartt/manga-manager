#!/usr/bin/env python2
"""
Provides standardized interface to anymanga manga site
"""
import urllib2, os
import common
from bs4 import BeautifulSoup

##########
# CONSTANTS
##########
NAME = 'MangaHere'
log = common.LOG
URLBASE = 'http://www.mangahere.com/'
URLSEARCH = 'search.php?name=%s'


##########
# FUNCTIONS
##########

openURL = common.openURL
soupURL = common.soupURL
downloadImage = common.downloadImage
downloadChapters = common.downloadChapters
URLSafe = common.URLSafe
filenameSafe = common.filenameSafe

# Useful beautifulsoup filters
chapterresult = lambda x: x.has_key('class') and x.has_key('href') and x.has_key('title')

def search(query):#{{{
	"""
	Search the database for a manga

	arguments:
	query -- string to search

	return:
	list of (name, url) tuples of matches
	"""
	print  URLBASE + URLSEARCH % URLSafe(query).replace('%20','+') 
	(soup, headers) = soupURL( URLBASE + URLSEARCH % URLSafe(query).replace('%20','+') )
	searchresults = soup.find( 'div', {'class':'result_search'})
	if searchresults is None: return []
	result = []
	for link in searchresults.find_all('a', {'class':'name_one'}):
		name = link.get_text().lstrip()
		url = link.get('href')
		result.append( ( name, url  ) )
	return result
	#}}}

def listChapters(url):#{{{
	"""
	List all chapters of a given manga

	arguments:
	url - url to manga's chapter list page

	return:
	list of (name, url) tuples of chapters
	"""
	(soup, headers) = soupURL( url )
	chapterdiv = soup.find('div', {'class':'detail_list'}).find('ul')
	if chapterdiv is None: return []
	result = []
	for link in chapterdiv.find_all('a'):
		name = link.get_text().lstrip().rstrip()
		url = link.get('href')
		result.append( ( name, url  ) )
	return result[::-1]
	#}}}

def downloadChapter(url, path):#{{{
	"""
	Download a specific chapter 

	arguments:
	url -- url to first page of chapter to download
	path -- folder to save into
	"""
	assert os.path.isdir( path ), "path does not exist"
	log.debug('Downloading Chapter at: %s' % url)
	baseurl = url.rsplit('/',1)[0]
	(soup, headers) = soupURL( url ) ## First page
	
	## get pagelist
	pageselect = soup.find( 'select', {'onchange':'change_page(this)'} )
	pagelist = [ x.get('value') for x in pageselect.find_all('option') ]
	print pagelist

	## Get total number of pages
	maxpages = len(pagelist)
	log.debug('Chapter has pages: %d' % maxpages)
	impathbase = URLtoFilename(url)+'_%0' + str(len(str(maxpages))) + 'd%s'

	## start saving pages
	for n in xrange(maxpages):
	 	log.debug('Downloading page: %d/%d' % (n+1,maxpages))
	 	(soup, headers) = soupURL(pagelist[n])
	 	try:
			img = soup.find('a', {'onclick': 'return enlarge();'}).img
			imgurl = img.get('src')
	 		imgpath = os.path.join( path, impathbase % (n,os.path.splitext(imgurl)[1]) )
			downloadImage( imgurl, imgpath )
	 	except Exception as e:
	 		log.error('Downloading page %d failed with %s' % (n,e))
	 		raise e
	#}}}

def URLtoFilename( url ):#{{{
	"""
	Helper to extract mangahere's naming scheme from a chapter's firstpage url

	arguments:
	url -- url to first page of a chapter

	return:
	valid filename from mangafox's naming scheme
	"""
	split = url.split('/')
	name = ('%s_%s_%s' % (split[4],split[5],split[6])).replace('-','_').replace(' ','')
	name = filenameSafe(name)
	return name
	#}}}

def URLtoFoldername( url ):#{{{
	"""
	Helper to extract mangafox's naming scheme from a chapter's mainpage url

	arguments:
	url -- url to mainpage of a manga 

	return:
	valid filename from mangafox's naming scheme
	"""
	name = url.split('/')[-2]
	return name
	#}}}
