#!/usr/bin/env python2

##########
# IMPORTS
##########

import argparse, os, sys, logging, subprocess, time, threading
from manga import __all__ as mangaModuleList
mangadb = []
for mangamodule in mangaModuleList:
	mangadb.append( __import__( 'manga.%s'%mangamodule, fromlist=['manga']) )

##########
# CONSTANTS
##########

MMFILE = '.mminfo'
MMTMP = '.mmtmp'
MMDIR = os.path.join( os.path.expanduser('~'), '.manga-manger' )
MMLOG = os.path.join( MMDIR, 'mmlog' )
MMCFG = os.path.join( MMDIR, 'mmcfg' )
MAXTHREADS = 5
DEFAULTOPTS = {
		'pdfbin':'evince',
		}

##########
# FUNCTIONS
##########

def mangaStatus():#{{{
	"""
	Print/return a list of manga and current reading status
	Dont display ones who are up to date on reading
	"""
	if os.path.isfile( MMFILE ):
		folders = [ os.getcwd() ]
	else:
		folders = sorted(filter( lambda x: os.path.isfile(os.path.join(x,MMFILE)), os.listdir(os.getcwd()) ))

	result = []
	n = 1
	for folder in folders:
		mmfile = open(os.path.join( folder, MMFILE ), 'r')
		mmfile.readline()
		for line in mmfile.readlines():
			chapter, status = line.rstrip().split(' = ')
			if status == 'unread':
				print '[%d] %s - %s' % (n,os.path.basename(folder), chapter)
				result.append( (folder,chapter) )
				n += 1
				break
	return result
	#}}}

def listDB():#{{{
	"""
	List all available manga databases
	"""
	print 'available databases:'
	for mangamodule in mangadb:
		print '\t'+mangamodule.NAME#}}}

def getDB( url ):#{{{
	"""
	Return the database associated with a given url
	"""
	for db in mangadb:
		if db.URLBASE in url:
			return db
	print 'Cannot determine database for: %s' % url
	logging.warn( 'Cannot determine database for: %s' % url )
	return #}}}

def downloadChapter( db, url, folder, chapters ):#{{{
	"""
	Download a chapter

	arguments:
	db -- manga database to use
	url -- url to manga's first page
	folder -- the tmpfolder which is a subfolder of the target destination
	chapters -- list of successfully downloaded chapters
	"""
	filename = db.URLtoFilename(url)
	try:
		## download to the tmpfolder
		db.downloadChapter( url, folder )

		## convert to pdf and move to parent dir
		infile = os.path.join( folder, filename+'*' )
		outfile = os.path.join( os.path.dirname(folder), filename+'.pdf' )
		subprocess.call( ['convert', infile, outfile] )
	except Exception as e:
		## Should really create a manga exception which wraps urllib2 exceptions
		logging.warn( 'Chapter %s failed with %s' % (url,e) )
		print 'Chapter %s failed with %s' % (url,e)
	else:
		## success, write to the mmfile
		chapters.append( filename )

	## cleanup tmpdir
	for tmpfile in os.listdir( folder ):
		if filename not in tmpfile: continue
		os.remove(os.path.join(folder,tmpfile))#}}}

def getManga( urls ):#{{{
	"""
	Download a manga to a subfolder of the cwd
	Present a list of mangas to choose from if the argument is a query

	arguments:
	urls -- a list of urls to download
	"""
	if 'http://' not in urls[0]:
		## Got a query, so search the query
		results = query(urls)

		## Prompt for a list to download
		selection = None
		while not selection:
			sys.stdout.write( 'Select manga(s): ' )
			selection = raw_input()
			try:
				selection = [ int(x) for x in selection.split(',') ]
				urls = [ results[n-1][1] for n in selection ]
			except ValueError:
				selection = None
			except IndexError:
				selection = None

	for url in urls:
		## Determine the database
		db = getDB( url )
		if db is None: continue

		## Setup files/folders
		folder = os.path.join( db.URLtoFoldername(url) )
		if os.path.isdir( folder ):
			print 'Folder already exists: %s' % folder 
			logging.warn('Folder already exists: %s' % folder)
			continue
		tmpfolder = os.path.join( folder, MMTMP )
		if not os.path.isdir( tmpfolder ): os.makedirs( tmpfolder )
		mmlist = []

		## Download all chapters
		print 'Downloading %s' % url
		logging.info( 'Downloading %s' % url )
		chlist = db.listChapters( url )
		for n in xrange( len(chlist) ):
			while threading.activeCount() > MAXTHREADS: time.sleep(1)
			print '%d/%d: %s' % (n,len(chlist),chlist[n][0])
			thread = threading.Thread( target=downloadChapter, args=[db, chlist[n][1], tmpfolder, mmlist] )
			thread.start()
		while threading.activeCount() > 1: time.sleep(1)

		## Write mminfo file from mmlist
		## keep the order
		mmfile = open(os.path.join( folder, MMFILE ), 'w+')
		print>>mmfile, url
		for name, url in chlist:
			filename = db.URLtoFilename(url)
			if filename in mmlist: print>>mmfile, filename+' = unread'
		mmfile.close()

		## Cleanup tmp dir
		for tmpfile in os.listdir(tmpfolder): os.remove(os.path.join(tmpfolder,tmpfile))
		os.rmdir(tmpfolder)

	print 'done'
	logging.info( 'done' )#}}}

def readManga( folder ):#{{{
	"""
	Read next unread manga in list,
	"""
	if folder is None:
		if os.path.isfile( MMFILE ):
			folder = ''
		else:
			unreadManga = mangaStatus()
			if not unreadManga:
				print 'Cannot find unread manga'
				return
			sys.stdout.write( 'Select manga: ' )
			selection = raw_input()
			try:
				folder = unreadManga[ int(selection)-1 ][0]
			except ValueError:
				return
			except IndexError:
				return
	else:
		if not os.path.isfile( os.path.join(folder,MMFILE) ):
			print 'Cannot find manga'
			return

	## Get manga status
	mmfile = open(os.path.join( folder, MMFILE ), 'r')
	url = mmfile.readline().rstrip()
	chapters = []
	status = []
	for line in mmfile.readlines():
		try:
			split = line.rstrip().split(' = ')
			chapters.append( split[0] )
			status.append( split[1] )
		except IndexError:
			continue

	for n in xrange(len(chapters)):
		if status[n] == 'read': continue
		filename = os.path.join(folder,chapters[n]+'.pdf')
		if not os.path.isfile(filename):
				print 'Missing unread chapter: %s' % chapters[n]
				continue

		print 'Continue Reading %s?' % chapters[n]
		sys.stdout.write( 'Yes, No, Skip, Skip and mark read (default=Yes) [y/n/s/m]' )
		selection = raw_input().lower()
		if selection in ['n','no']:
			break
		elif selection in ['s','skip']:
			continue
		elif selection in ['m','mark']:
			status[n] = 'read'
			continue
		else:
			subprocess.call( [opts['pdfbin'], filename ] )
			status[n] = 'read'

	## Update mminfo file
	mmfile = open(os.path.join( folder, MMFILE ), 'w+')
	print>>mmfile, url
	for n in xrange(len(chapters)): print>>mmfile, '%s = %s' % (chapters[n],status[n])
	mmfile.close()#}}}

def updateFolder( folder ):#{{{
	"""
	Update the given folder
	"""
	## Get current local status
	mmfile = open(os.path.join( folder, MMFILE ), 'r')
	url = mmfile.readline().rstrip()
	chapters = []
	status = []
	for line in mmfile.readlines():
		try:
			split = line.rstrip().split(' = ')
			chapters.append( split[0] )
			status.append( split[1] )
		except IndexError:
			continue
	mmfile.close()
	db = getDB(url)
	if db is None: return
	
	## Get current list of missing chapters
	chapterlist = db.listChapters(url)
	urls = filter( lambda x: db.URLtoFilename(x[1]) not in chapters, chapterlist ) 
	if not urls:
		print '%s up to date' % folder
		logging.info( '%s up to date' % folder )
		return

	print 'updating %s' % folder
	logging.info( 'updating %s' % folder )
	## Setup folders/vars
	tmpfolder = os.path.join( folder, MMTMP )
	if not os.path.isdir( tmpfolder ): os.makedirs( tmpfolder )
	mmlist = []

	## Download missing chapters
	for n in xrange( len(urls) ):
		while threading.activeCount() > MAXTHREADS: time.sleep(1)
		print '%d/%d: %s' % (n,len(urls), urls[n][0])
		thread = threading.Thread( target=downloadChapter, args=[db, urls[n][1], tmpfolder, mmlist] )
		thread.start()
	while threading.activeCount() > 1: time.sleep(1)
	
	## Update mminfo file
	chapters.extend( mmlist )
	status.extend( ['unread']*len(mmlist) )
	mmfile = open(os.path.join( folder, MMFILE ), 'w+')
	print>>mmfile, url
	for name, url in chapterlist:
		try:
			index = chapters.index( db.URLtoFilename(url) )
			line = '%s = %s' % (chapters[index],status[index])
			print>>mmfile, line
		except ValueError:
			continue
	mmfile.close()#}}}

def query( searchq, databases=None ):#{{{
	if databases == None:
		databases = mangadb
	results = []
	for db in databases: results.extend( db.search( ' '.join(searchq) ) )
	for n in range(len(results)): print '[%d] %s\t%s' % (n+1,results[n][0],results[n][1])
	return results#}}}

def update():#{{{
	"""
	Call updatefolder on currentfolders or subfolders depending on which is a managed directory
	"""
	if os.path.isfile( MMFILE ):
		updateFolder('')
	else:
		mangaFolders = filter( lambda x: os.path.isfile(os.path.join(x,MMFILE)), os.listdir(os.getcwd()) )
		for folder in mangaFolders: updateFolder( folder )#}}}

##########
# MAIN SCRIPT
##########

## Check for config stuff and setup logger
if not os.path.isdir( MMDIR ): os.makedirs( MMDIR )
if not os.path.isfile(MMCFG):
	mmcfg = open( MMCFG, 'w+' )
	for key,value in DEFAULTOPTS.items(): print>>mmcfg, '%s = %s' % (key,value)
	mmcfg.close()
	opts = DEFAULTOPTS
else:
	mmcfg = open( MMCFG, 'r' )
	opts = {}
	for line in mmcfg.readlines():
		split = line.rstrip().split(' = ')
		opts[split[0]] = split[1]
	for key in DEFAULTOPTS:
		if key not in opts: opts[key] = DEFAULTOPTS[key]
logging.basicConfig( filename=MMLOG, level=logging.DEBUG)

parser = argparse.ArgumentParser(
		description='Manga management and download utility')
parser.add_argument(
		'-d', '--database',
		metavar = 'DB',
		nargs = '+',
		action = 'store',
		help = 'list of manga database(s) to use',)
parser.add_argument(
		'-g', '--get',
		metavar = 'URL',
		nargs = '+',
		action = 'store',
		help = 'list of manga URLs to download or a query to perform',)
parser.add_argument(
		'-l', '--list',
		action = 'store_true',
		help = 'List available manga databases')
parser.add_argument(
		'-q', '--query',
		nargs = '+',
		action = 'store',
		help = 'Query database(s) for a manga')
parser.add_argument(
		'-r', '--read',
		action = 'store_true',
		help = 'Read a managed manga')
parser.add_argument(
		'-s', '--status',
		action = 'store_true',
		help = 'Print reading status')
parser.add_argument(
		'-u', '--update',
		action = 'store_true',
		help = 'Download missing chapters of manga in current directory or all subdirectories')
args = parser.parse_args()

# check for valid database list
if args.database:
	databases = []
	for db in set(args.database):
		match = filter( lambda x: x.NAME.lower()==db.lower(), mangadb )
		if match:
			databases.extend( match )
		else:
			print 'Unrecognized Database: %s' % db
			listDB()
			exit()
else:
	databases = None

if args.query:
	query( args.query, databases )
	exit()

if args.get:
	getManga( args.get )
	exit()

if args.update:
	update()
	exit()

if args.read:
	readManga(None)
	exit()

if args.list:
	listDB()
	exit()

if args.status:
	mangaStatus()
	exit()
