#!/usr/bin/env python2
"""
This provides some basic functions useful for all manga fetching backends
But more serves as a skeleton file for default function names/args/returns
"""
import urllib2, logging
from bs4 import BeautifulSoup

##########
# LOGGING
##########
LOG = logging.getLogger('manga')

##########
# CONSTANTS
##########
MAXRETRIES = 5

##########
# FUNCTIONS
##########

def search(query):#{{{
	"""
	Search the database for a manga

	arguments:
	query -- string to search

	return:
	list of (name, url) tuples of matches
	return urls are compatibile with listChapters( url )
	"""
	return []#}}}

def listChapters(url):#{{{
	"""
	List all chapters of a given manga

	arguments:
	url - url to manga's chapter list page

	return:
	list of (name, url) tuples of chapters
	return urls are compatibile with downloadChapter/downloadChapters
	"""
	return []#}}}

def downloadChapter(url, path):#{{{
	"""
	Download a specific chapter 

	arguments:
	url -- url to first page of chapter to download
	path -- folder to save into
	"""
	pass#}}}

def downloadChapters(urls, path):#{{{
	"""
	Download a range of chapters

	arguments:
	urls -- list of urls to first page of each chapter to download
	path -- folder to save into
	"""
	for url in urls:
		downloadChapter( url, path )
	#}}}

def openURL(url):#{{{
	"""
	Helper to open urls

	arguments:
	url - url to open

	return:
	(html, headers) of the requested page
	"""
	request = urllib2.Request( url )
	retry = 0
	while retry < MAXRETRIES:
		try:
			page = urllib2.urlopen( request )
		except urllib2.URLError as err:
			retry += 1
			if retry == MAXRETRIES:
				LOG.error('Open %s failed with %s, aborting' % (url, err))
				raise err
			else:
				LOG.warn('Open %s failed with %s, retrying' % (url, err))
		else:
			break
	html = page.read()
	return (html, page.headers.items())#}}}

def soupURL(url):#{{{
	"""
	Helper to open urls as beautifulsoup object

	arguments:
	url - url to open

	return:
	(soup, headers) of the requested page
	"""
	(html, headers) = openURL(url)
	soup = BeautifulSoup( html )
	return (soup, headers)#}}}

def downloadImage(url, filename):#{{{
	"""
	Helper to save an img at a given url

	arguments:
	url -- path to image
	filename -- path+filename to save image to
	"""
	(image, header) = openURL( url )
	imagefile = file(filename, 'wb')
	imagefile.write( image )
	imagefile.close()#}}}
