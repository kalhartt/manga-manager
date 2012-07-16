#!/usr/bin/env python2
import urllib2
from bs4 import BeautifulSoup

class site(object):
	"""
	Base class for all mangasite backends
	"""

	def __init__(self):#{{{
		"""
		Constructor creates urlopeners and base variables
		"""
		self.maxRetries = 5
		self.opener = urllib2.build_opener()#}}}
	
	def search(self, query):#{{{
		"""
		Search the database for a manga

		arguments:
		query -- string to search

		return:
		list of (name, url) tuples of matches
		"""
		pass#}}}

	def listChapters(self, url):#{{{
		"""
		List all chapters of a given manga

		arguments:
		url - url to manga's chapter list page

		return:
		list of (name, url) tuples of chapters
		"""
		pass#}}}

	def downloadChapter(self, url, path):#{{{
		"""
		Download a specific chapter 

		arguments:
		url -- url to first page of chapter to download
		path -- folder to save into
		"""
		pass#}}}

	def downloadChapters(self, urls, path):#{{{
		"""
		Download a range of chapters

		arguments:
		urls -- list of urls to first page of each chapter to download
		path -- folder to save into
		"""
		for url in urls:
			self.downloadChapter( url, path )
		#}}}

	def openURL(self, url):#{{{
		"""
		Helper to open urls

		arguments:
		url - url to open

		return:
		(html, headers) of the requested page
		"""
		request = urllib2.Request( url )
		retry = 0
		maxRetry = 5
		while retry < maxRetry:
			try:
				page = self.opener.open( request )
			except urllib2.URLError as err:
				retry += 1
				if retry == maxRetry:
					raise err
			else:
				break
		html = page.read()
		return (html, page.headers.items())#}}}
	
	def soupURL(self, url):#{{{
		"""
		Helper to open urls as beautifulsoup object

		arguments:
		url - url to open

		return:
		(soup, headers) of the requested page
		"""
		(html, headers) = self.openURL(url)
		soup = BeautifulSoup( html )
		return (soup, headers)#}}}

	def downloadImage(self, url, filename):#{{{
		"""
		Helper to save an img at a given url

		arguments:
		url -- path to image
		filename -- path+filename to save image to
		"""
		(image, header) = self.openURL( url )
		imagefile = file(filename, 'wb')
		imagefile.write( image )
		imagefile.close()#}}}

