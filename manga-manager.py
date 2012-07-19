#!/usr/bin/env python2

##########
# IMPORTS
##########

import argparse, os, csv
from manga import __all__ as mangaModuleList
mangadb = []
for mangamodule in mangaModuleList:
	mangadb.append( __import__( 'manga.%s'%mangamodule, fromlist=['manga']) )

##########
# CONSTANTS
##########

MMFILE = '.mminfo'

##########
# FUNCTIONS
##########

def listDB():
	print 'available databases:'
	for mangamodule in mangadb:
		print '\t'+mangamodule.NAME

def query( searchq, databases=None ):
	if databases == None:
		databases = mangadb
	for db in databases:
		results = db.search( searchq )
		for result in results:
			print '%s\t%s' % (result[0],result[1])

def update():
	pass

##########
# MAIN SCRIPT
##########


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
	query( args.query, databases )
	exit()
