#!/usr/bin/env python2
import urllib2, os
from bs4 import BeautifulSoup
from .site import site

class mangafox(site):
	"""
	Mangafox backend
	"""

	def __init__(self):
		"""
		Set appropriate defaults for mangafox
		"""
		super( mangafox, self ).__init__()
		self.urlbase = 'http://www.mangafox.me/'
		self.urlsearch = 'search.php?name='
		
		# Useful beautifulsoup filters
		self.searchresult = lambda x: x.has_key('class') and x.has_key('href') and x.has_key('rel') and not x.has_key('onclick')
		self.chapterresult = lambda x: x.has_key('class') and x.has_key('href') and x.has_key('title')

	def search(self, query):#{{{
		"""
		Search the database for a manga

		arguments:
		query -- string to search

		return:
		list of (name, url) tuples of matches
		"""
		(soup, headers) = self.soupURL( self.urlbase + self.urlsearch + query )
		result = []
		for link in soup.find_all( self.searchresult ):
			result.append( ( link.get_text(), link.get('href') ) )
		return result
		#}}}
	
	def listChapters(self, url):#{{{
		"""
		List all chapters of a given manga

		arguments:
		url - url to manga's chapter list page

		return:
		list of (name, url) tuples of chapters
		"""
		(soup, headers) = self.soupURL( url )
		result = []
		for link in soup.find_all( self.chapterresult):
			result.append( ( link.get_text(), link.get('href') ) )
		return result
		#}}}
	
	def downloadChapter(self, url, path):#{{{
		"""
		Download a specific chapter 

		arguments:
		url -- url to first page of chapter to download
		path -- folder to save into
		"""
		assert os.path.isdir( path ), "path does not exist"
		baseurl = url.rsplit('/',1)[0]
		(soup, headers) = self.soupURL( url ) ## First page
		
		## Get total number of pages
		pagelist = soup.find('select', {'class':'m', 'onchange':'change_page(this)'})
		maxpages = len(list(pagelist.children))-3
		impathbase = '%0' + str(len(str(maxpages))) + 'd%s'

		## start saving pages
		for page in range(1, maxpages):
			(soup, headers) = self.soupURL( '%s/%d.html' % (baseurl,page) )
			imgurl = soup.img.get('src')
			imgpath = os.path.join( path, impathbase % (page,os.path.splitext(imgurl)[1]) )
			self.downloadImage( imgurl, imgpath )
		#}}}
