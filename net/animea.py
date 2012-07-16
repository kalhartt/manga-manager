#!/usr/bin/env python2
import urllib2, os
from bs4 import BeautifulSoup
from .site import site

class animea(site):
	"""
	Mangafox backend
	"""

	def __init__(self):
		"""
		Set appropriate defaults for mangafox
		"""
		super( animea, self ).__init__()
		self.urlbase = 'http://manga.animea.net/'
		self.urlsearch = 'search.html?title='
		
		# Useful beautifulsoup filters
		self.chapterresult = lambda x: x.has_key('id') and x.has_key('href') and x.has_key('title')

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
		for link in soup.find_all( 'a', 'manga_title' ):
			result.append( ( link.get_text(), self.urlbase+link.get('href')[1:] ) )
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
		for link in soup.find_all( self.chapterresult ):
			result.append( ( link.get_text(), (self.urlbase+link.get('href')[1:]).replace(' ','%20') ) )
		return result[::-1]
		#}}}
	
	def downloadChapter(self, url, path, verbose=False):#{{{
		"""
		Download a specific chapter 

		arguments:
		url -- url to first page of chapter to download
		path -- folder to save into
		"""
		assert os.path.isdir( path ), "path does not exist"
		baseurl = url.rsplit('.',1)[0]
		(soup, headers) = self.soupURL( url ) ## First page
		
		## Get total number of pages
		pagelist = soup.find('select', {'class':'mangaselecter pageselect', 'name':'page'})
		maxpages = len(list(pagelist.children))-1
		impathbase = '%0' + str(len(str(maxpages))) + 'd%s'

		## start saving pages
		for page in range(1, maxpages):
			if verbose: print "Downloading page:\t%d" % page
			(soup, headers) = self.soupURL( '%s-page-%d.html' % (baseurl,page) )
			try:
				imgurl = soup.find('img', {'class':'mangaimg'}).get('src')
				imgpath = os.path.join( path, impathbase % (page,os.path.splitext(imgurl)[1]) )
			except Exception as e:
				print '%s-%d.html' % (baseurl,page)
				raise e
			self.downloadImage( imgurl, imgpath )
		#}}}
