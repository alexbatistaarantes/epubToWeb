#!/bin/env python3

from bs4 import BeautifulSoup
from os import path, getcwd, scandir, listdir, mkdir
import sys

## to extract epub content
## epub = zipFile.ZipFile('epubpath')
## epub.extractall()

__location__ = path.realpath( path.join(getcwd(), path.dirname(__file__)))

class Book():
	
	# files: xhtml files of the book
	# path: path from within folder. Used from <a> tags from the html files
	# AbsPath (absolute path): absolute file. Used for this code purpose

	def __init__(self, filesAbsPath, newBookAbsPath):
		
		self.files = [] # files from scandir of old files
		self.filesLen = 0 
		self.newFilesAbsPath = '' # new files (xhtml) absolute path

		self.filesAbsPath = filesAbsPath # path of old files
		if( self.getFiles() == 0 ):
			raise ValueError("Couldn't access the file's directory.")
		
		self.newBookAbsPath = newBookAbsPath
		if( self.createNewBookDir() == 0 ):
			raise ValueError("Couldn't create the new book's directory.")

		self.createNewBook()
	
	def createNewBook(self):
		
		with open( path.join( __location__, 'book.html'), 'r' ) as bookFile:
			newBookFile = open( path.join( self.newBookAbsPath, 'book.html' ), 'w' )
			newBookFile.write( bookFile.read() )
			newBookFile.close()
		
		with open( path.join( __location__, 'bookIndex.html'), 'r' ) as bookIndexFile:
			bookIndexContent = bookIndexFile.read()

		bookIndexSoup = BeautifulSoup( bookIndexContent, 'html.parser' )
		
		# Iterating over book files
		for fileIndex in range(0, self.filesLen) :
			fileName = self.files[fileIndex].name
			# Absolute path from this python file
			newFileAbsPath = path.join( self.newFilesAbsPath, fileName )
			
			# Creating a copy of the file to the new book
			newFile = open( newFileAbsPath, 'w' )
			newFileContent, fileTitle = self.addPageLinks( fileIndex )
			newFile.write( newFileContent )
						
			newFilePath = path.join( 'pages', fileName )
			# Link Tag from this chapter in the book index
			newFileIndexTag = bookIndexSoup.new_tag('a', href=newFilePath )
			newFileIndexTag.string = fileTitle
			bookIndexSoup.find(id="bookIndex").append( newFileIndexTag )
			brTag = bookIndexSoup.new_tag('br')
			bookIndexSoup.find(id='bookIndex').append( brTag )

		with open( path.join( self.newBookAbsPath, 'bookIndex.html'), 'w' ) as bookIndexFile:
			bookIndexFile.write( bookIndexSoup.prettify() )


	def addPageLinks(self, fileIndex):
		
		# Getting content
		with open( self.files[ fileIndex ].path, 'r' ) as filePage:
			fileContent = filePage.read()
		
		pageSoup = BeautifulSoup( fileContent, 'html.parser')
		
		increaseFontButton = pageSoup.new_tag('button', onclick="increaseFont(5)", style="position: sticky; top: 0;")
		increaseFontButton.string = "Increase Font"
		decreaseFontButton = pageSoup.new_tag('button', onclick="increaseFont(-5)", style="position: sticky; top: 0;")
		decreaseFontButton.string = "Decrease Font"
		pageSoup.body.insert(0, increaseFontButton)
		pageSoup.body.insert(1, decreaseFontButton)

		scriptFontTag = pageSoup.new_tag('script', type='text/javascript')
		scriptFontTag.string = """
	function increaseFont(size){
		size = parseInt( window.getComputedStyle( document.getElementsByTagName('body')[0] )['font-size'] ) + size;
		document.getElementsByTagName('body')[0].style.fontSize = size.toString()+'px';
	}
"""		
		pageSoup.body.insert_after( scriptFontTag )
		
		topNavLinksTag = pageSoup.new_tag('div', id='topNavigationLinks')
		pageSoup.body.insert(2, topNavLinksTag )
		bottomNavLinksTag = pageSoup.new_tag('div', id='bottomNavigationLinks')
		pageSoup.body.append( bottomNavLinksTag )

		# PREVIOUS PAGE LINK
		previousFileIndex = fileIndex - 1
		if( previousFileIndex >= 0 ):
			previousPageTopTag = pageSoup.new_tag('a', href=self.files[previousFileIndex].name )
			previousPageTopTag.string = '  Previous chapter  '

			previousPageBottomTag = pageSoup.new_tag('a', href=self.files[previousFileIndex].name )
			previousPageBottomTag.string = '  Previous chapter  '

			pageSoup.find(id='topNavigationLinks').append(previousPageTopTag)
			pageSoup.find(id='bottomNavigationLinks').append( previousPageBottomTag )

		# NEXT PAGE LINK
		nextFileIndex = fileIndex + 1
		if( nextFileIndex < self.filesLen ):
			nextPageTopTag = pageSoup.new_tag('a', href=self.files[nextFileIndex].name )
			nextPageTopTag.string = '  Next chapter  '
			nextPageBottomTag = pageSoup.new_tag('a', href=self.files[nextFileIndex].name )
			nextPageBottomTag.string = '  Next chapter  '

			pageSoup.find(id='topNavigationLinks').append( nextPageTopTag )
			pageSoup.find(id='bottomNavigationLinks').append( nextPageBottomTag )
		
		# INDEX PAGE LINK
		indexPageTopTag = pageSoup.new_tag('a', href='../bookIndex.html')
		indexPageTopTag.string = "  Book Index  "
		indexPageBottomTag = pageSoup.new_tag('a', href='../bookIndex.html')
		indexPageBottomTag.string = "  Book Index  "
		pageSoup.find(id='topNavigationLinks').insert(0, indexPageTopTag)
		pageSoup.find(id='bottomNavigationLinks').append(indexPageBottomTag)

		pageTitle = pageSoup.find('title').string

		return pageSoup.prettify(), pageTitle

	def getFiles(self):
		try:
			self.files = sorted( scandir( self.filesAbsPath ), key=lambda x: (x.is_dir(), x.name) )
			self.filesLen = len( self.files )
			return 1
		except:
			return 0
	def createNewBookDir(self):
		try:
			mkdir( self.newBookAbsPath )
		except FileExistsError:
			raise ValueError("The folder already exist.")
		except:
			return 0
		self.newFilesAbsPath = path.join( self.newBookAbsPath, 'pages' )
		mkdir( self.newFilesAbsPath )

		return 1

if __name__ == '__main__':

	if( len(sys.argv) == 3 ):
		book = Book( sys.argv[1], sys.argv[2] )
		print("""
	Verify the extracted folder for any aditional folders and files referentiated by the files, like /CSS /Images. Copy them to the equivalent directory in the new book folder.
		""")
	else:
		print("""
	main.py HTML_FILES_PATH NEW_BOOK_PATH

	Extract the .epub file and find the folder where the .html files are stored.
		""")
