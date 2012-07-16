#!/usr/bin/env python2
import os, logging
from manga import animea
from manga import mangafox

## show logging output
logging.basicConfig( level=logging.DEBUG )

## choose a manga database
mangadb = animea

## Search for a manga, returns a list of 2-tuples
searchresults = mangadb.search( 'myst' )
for result in searchresults:
	print result[0], result[1]

## for example we will take the first result
name, url = searchresults[0]

## Get the chapter list
chapters = mangadb.listChapters( url )
for chapter in chapters:
	print chapter[0], chapter[1]

## Lets download the first chapter
## I'm using unix paths, we just need the folder to download to
## the mangadb's provide a way to get filenamesafe chapter names
chapterURL = chapters[0][1]
downloadPath = os.path.expanduser( '~/manga' )
nicename = mangadb.URLtoFilename( chapterURL )
foldername = os.path.join( downloadPath, nicename )
if not os.path.exists( foldername ): os.makedirs( foldername )

## Begin download
mangadb.downloadChapter( chapterURL, foldername )
