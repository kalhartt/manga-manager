#!/usr/bin/env python2
"""
Provides standardized interface to animea manga site
"""
import urllib2, os
import common
from bs4 import BeautifulSoup

##########
# CONSTANTS
##########
NAME = 'AnimeA'
log = common.LOG
URLBASE = 'http://manga.animea.net/'
URLSEARCH = 'search.html?title=%s'

##########
# FUNCTIONS
##########

openURL = common.openURL
soupURL = common.soupURL
downloadImage = common.downloadImage
downloadChapters = common.downloadChapters
URLSafe = common.URLSafe
filenameSafe = common.filenameSafe

## beautiful soup helper filter
chaptersearch = lambda x: x.has_key('href') and x.has_key('id') and x.has_key('title')

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
	for link in soup.find_all( 'a', 'manga_title' ):
		result.append( ( link.get_text(), URLBASE+link.get('href')[1:] ) )
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
	for link in soup.find_all(chaptersearch):
		result.append( ( link.get_text(), (URLBASE+link.get('href')[1:]).replace(' ','%20') ) )
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
	baseurl = url.rsplit('.',1)[0]
	(soup, headers) = soupURL( url )
	
	## Get total number of pages
	pagelist = soup.find('select', {'class':'mangaselecter pageselect', 'name':'page'})
	maxpages = len(list(pagelist.children))-1
	log.debug('Chapter has pages: %d' % maxpages)
	impathbase = URLtoFilename(url)+'_%0' + str(len(str(maxpages))) + 'd%s'

	## start saving pages
	for page in range(1, maxpages):
		log.debug('Downloading page: %d/%d' % (page,maxpages))
		try:
			(soup, headers) = soupURL( '%s-page-%d.html' % (baseurl,page) )
			imgurl = soup.find('img', {'class':'mangaimg'}).get('src')
			imgpath = os.path.join( path, impathbase % (page,os.path.splitext(imgurl)[1]) )
			downloadImage( imgurl, imgpath )
		except Exception as e:
			log.error('Downloading page %d failed with %s' % (page,e))
			raise e
	#}}}

def URLtoFilename( url ):#{{{
	"""
	Helper to extract animea's naming scheme from a chapter's firstpage url

	arguments:
	url -- url to first page of a chapter

	return:
	valid filename from animea's naming scheme
	"""
	split = url.split('/')[-1]
	if '-page-' in split:
		name = split.split('-page-')[0].replace('-','_').replace(' ','')
	else:
		name = split.split('.html')[0].replace('-','_').replace(' ','')
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
	name = url.split('/')[-1][:-5]
	return name
	#}}}
