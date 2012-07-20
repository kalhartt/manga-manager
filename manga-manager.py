#!/usr/bin/env python2

##########
# IMPORTS
##########

import argparse, os, logging, csv, subprocess, time, threading
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

##########
# FUNCTIONS
##########

def listDB():
	print 'available databases:'
	for mangamodule in mangadb:
		print '\t'+mangamodule.NAME

def downloadChapter( db, url, folder, csvr ):
	filename = db.URLtoFilename(url)
	try:
		db.downloadChapter( url, folder )
		infile = os.path.join( folder, filename+'*' )
		outfile = os.path.join( os.path.dirname(folder), filename+'.pdf' )
		subprocess.call( ['convert', infile, outfile] )
		csvr.writerow( [filename, 'unread'] )
	except Exception as e:
		logging.warn( 'Chapter %s failed with %s' % (url,e) )
		print 'Chapter %s failed with %s' % (url,e)
	for tmpfile in os.listdir( folder ):
		if filename not in tmpfile: continue
		os.remove(os.path.join(folder,tmpfile))

def getManga( urls ):#{{{
	for url in urls:
		## Determine the database
		db = filter( lambda x: x.URLBASE in url, mangadb )
		if not db:
			print 'Cannot determine database for: %s' % url
			logging.warn( 'Cannot determine database for: %s' % url )
			continue
		else:
			db = db[0]

		print 'Downloading %s' % url
		logging.info( 'Downloading %s' % url )

		## Setup files/folders
		folder = os.path.join( os.getcwd(), db.URLtoFoldername(url) )
		tmpfolder = os.path.join( folder, MMTMP )
		if not os.path.isdir( tmpfolder ): os.makedirs( tmpfolder )
		mmfile = open(os.path.join( folder, MMFILE ), 'w+')
		csvfile = csv.writer( mmfile, delimiter='\t' )
		csvfile.writerow( [url] )

		## Download all chapters
		chlist = db.listChapters( url )
		for n in xrange( len(chlist) ):
			while threading.activeCount() > MAXTHREADS: time.sleep(1)
			print '%d/%d: %s' % (n,len(chlist),chlist[n][0])
			thread = threading.Thread( target=downloadChapter, args=[db, chlist[n][1], tmpfolder, csvfile] )
			thread.start()
		while threading.activeCount() > 1: time.sleep(1)
		os.rmdir( tmpfolder )
		mmfile.close()
	print 'done'
	logging.info( 'done' )#}}}

def query( searchq, databases=None ):#{{{
	if databases == None:
		databases = mangadb
	for db in databases:
		results = db.search( searchq )
		for result in results:
			print '%s\t%s' % (result[0],result[1])#}}}

def update():#{{{
	if os.path.isfile( os.path.join( os.getcwd(), MMFILE ) ):
		updateFolder( os.getcwd() )
	else:
		mangaFolders = [os.path.join(os.getcwd(),x) for x in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(),x,'.mminfo'))]
		for folder in mangaFolders: updateFolder( folder )#}}}

def updateFolder( folder ):
	mmfile = open(os.path.join( folder, MMFILE ), 'r+')
	csvr = csv.reader( mmfile, delimiter='\t' )
	chapters = []
	status = []
	row = csvr.next()
	url = row[0]
	while row:
		chapters.append( row[0] )
		status.append( row[1] )
		row = csvr.next()
	print 'updating %s' % folder
	logging.info( 'updating %s' % folder )
	chlist = db.listChapters( url )
	for name, churl in chlist:
		pass

##########
# MAIN SCRIPT
##########

## Check for config stuff and setup logger
if not os.path.isdir( MMDIR ): os.makedirs( MMDIR )
#if not os.path.isfile( MMCFG )
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
		help = 'list of manga URLs to download',)
parser.add_argument(
		'-l', '--list',
		action = 'store_true',
		help = 'List available manga databases')
parser.add_argument(
		'-q', '--query',
		action = 'store',
		help = 'Query database(s) for a manga')
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
	logging.info( 'Queried - %s' % args.query )
	query( args.query, databases )
	exit()

if args.get:
	getManga( args.get )
	exit()

if args.update:
	update()
	exit()
