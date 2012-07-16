#!/usr/bin/env python2
import os, subprocess, threading, time, logging
from manga import animea
from manga import mangafox

logging.basicConfig( level=logging.DEBUG )

url = 'http://mangafox.me/manga/1_2_prince/'
path = os.expandUser('~/manga/1_2_prince')
tmppaths = [ os.path.join( path, 'tmp%d' % n ) for n in range(1,6) ]
for tmppath in tmppaths:
	if not os.path.exists( tmppath ):
		os.makedirs( tmppath )
failed = []

def getChapter( name, url ):
	tmppath = tmppaths.pop()

	try:
		print "Downloading chapter: " + name
		mangafox.downloadChapter( chapterURL, tmppath )
	except Exception as err:
		print "Downloading chapter %s failed widh %s" % (name, err)
		failed.append( name )
	else:
		print "Converting to pdf"
		infile = os.path.join( tmppath, '*' )
		nicename = mangafox.URLtoFilename( url )
		outfile = os.path.join( path, nicename+'.pdf' )
		subprocess.call([ 'convert', infile, outfile ])

	print "Cleaning tmp directory"
	for afile in os.listdir( tmppath ):
		os.unlink( os.path.join( tmppath, afile ) )
	
	tmppaths.append( tmppath )

for name, chapterURL in mangafox.listChapters(url):
	while len(tmppaths)==0:
		time.sleep(0.2)
	thread = threading.Thread( target=getChapter, args=[name,chapterURL] )
	thread.start()
	time.sleep(0.1)

while threading.activeCount() > 1:
	time.sleep(0.2)

if failed:
	print "completed with errors"
	for name in failed:
		print name
else:
	print "completed"

