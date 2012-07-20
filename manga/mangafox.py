#!/usr/bin/env python2
"""
Provides standardized interface to mangafox manga site
"""
import urllib2, os
import common
from bs4 import BeautifulSoup

##########
# CONSTANTS
##########
NAME = 'MangaFox'
log = common.LOG
URLBASE = 'http://mangafox.me/'
URLSEARCH = 'search.php?name=%s'


##########
# FUNCTIONS
##########

openURL = common.openURL
soupURL = common.soupURL
downloadImage = common.downloadImage
downloadChapters = common.downloadChapters
URLSafe = common.URLSafe

# Useful beautifulsoup filters
searchresult = lambda x: x.has_key('class') and x.has_key('href') and x.has_key('rel') and not x.has_key('onclick')
chapterresult = lambda x: x.has_key('class') and x.has_key('href') and x.has_key('title')

def search(query):#{{{
	"""
	Search the database for a manga

	arguments:
	query -- string to search

	return:
	list of (name, url) tuples of matches
	"""
	(soup, headers) = soupURL( URLBASE + URLSEARCH % URLSafe(query) )
	result = []
	for link in soup.find_all( searchresult ):
		name = link.get_text()
		url = link.get('href')
		# If it's liscenced, dont return it
		# Only return urls to downloadable manga
		(mangasoup, mangaheaders) = soupURL( url )
		warningdiv = mangasoup.find( 'div', { 'class':'warning' } )
		if not warningdiv or 'liscensed' not in warningdiv.get_text():
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
	result = []
	for link in soup.find_all( chapterresult ):
		result.append( ( link.get_text(), link.get('href').replace(' ','%20') ) )
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
	
	## Get total number of pages
	pagelist = soup.find('select', {'class':'m', 'onchange':'change_page(this)'})
	maxpages = len(list(pagelist.children))-3
	log.debug('Chapter has pages: %d' % maxpages)
	impathbase = URLtoFilename(url)+'_%0' + str(len(str(maxpages))) + 'd%s'

	## start saving pages
	for page in range(1, maxpages):
		log.debug('Downloading page: %d/%d' % (page,maxpages))
		(soup, headers) = soupURL( '%s/%d.html' % (baseurl,page) )
		try:
			imgurl = soup.img.get('src')
			imgpath = os.path.join( path, impathbase % (page,os.path.splitext(imgurl)[1]) )
			downloadImage( imgurl, imgpath )
		except Exception as e:
			log.error('Downloading page %d failed with %s' % (page,e))
			raise e
	#}}}

def URLtoFilename( url ):#{{{
	"""
	Helper to extract mangafox's naming scheme from a chapter's firstpage url

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
