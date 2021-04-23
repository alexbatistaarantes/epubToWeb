#!/bin/env python3

from os import path, getcwd, mkdir, scandir, listdir
from sys import argv
from bs4 import BeautifulSoup
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from shutil import copy, rmtree

from functions import *

__location__ = path.realpath( path.join( getcwd(), path.dirname(__file__) ) )

BOOK_MAIN_FILE_NAME = 'book.html'
BOOK_INDEX_FILE_NAME = 'bookIndex.html'
BOOK_CONTENT_FOLDER_NAME = 'bookContent'
EXTRACTED_EPUB_FOLDER_NAME = 'extractedEpub'
FAVICON_FILE_NAME = 'favicon.png'

class WebBook():
	
	# self.
	#	epub: epub file
	#	absPath: absolute path of the web book
	#	bookContentAbsPath: absolute path of the book content folder inside the web book folder
	#	extractedEpubAbsPath: absolute path of the extracted epub content inside the web book folder
	#

	def __init__(self, epubFileAbsPath, webBookAbsPath):
		
		# Loading epub file / verifying path is valid
		try:
			self.epub = loadEpub( epubFileAbsPath )
		except:
			raise

		# Defining paths of folders of the webBook
		self.absPath = webBookAbsPath
		self.bookContentAbsPath = path.join( self.absPath, BOOK_CONTENT_FOLDER_NAME )
		self.extractedEpubAbsPath = path.join( self.absPath, EXTRACTED_EPUB_FOLDER_NAME )
		# Creating root folders
		try:
			createFolder( self.absPath )
		except:
			raise
		createFolder( self.bookContentAbsPath )
		createFolder( self.extractedEpubAbsPath )
		
		# Extracting epub files
		try:
			extractEpub( self.epub, self.extractedEpubAbsPath )
		except:
			deleteFolder( self.absPath )
			raise

		# Coppying the content of the extracted epub to the web book folder, and getting list of all the files
		self.filesAbsPathList = copyFolderRecursively( self.extractedEpubAbsPath, self.bookContentAbsPath )
		
		# Getting the spine
		ncxFileAbsPath = findFileByExtension( self.filesAbsPathList, '.ncx')
		with open( ncxFileAbsPath, 'r') as ncxFile:
			self.spine = getSpineFromNcx( ncxFile.read() )

		# Getting paths (relatives to the content.opf folder where found) from every item
		##	self.epubContentsInfos, self.epubSpineIds = self.loadInfoFromContentOpf()
		
		# Copying book.html to web book
		copy( path.join(__location__, BOOK_MAIN_FILE_NAME), self.absPath )
		copy( path.join(__location__, BOOK_INDEX_FILE_NAME), self.absPath )
		copy( path.join(__location__, FAVICON_FILE_NAME), self.absPath )
		
		self.modifyContent( getRelativePath( self.absPath+'/', path.split(ncxFileAbsPath)[0]), path.split(ncxFileAbsPath)[0] )

	def modifyContent(self, ncxRelPath, ncxAbsPath):

		# Getting the bookIndex.html content
		bookIndexAbsPath = path.join( self.absPath, BOOK_INDEX_FILE_NAME )
		with open( bookIndexAbsPath, 'r') as temp_bookIndex:
			bookIndexSoup = BeautifulSoup( temp_bookIndex.read(), 'html.parser')
		
		# Copying and modifying the spine files
		for spineIndex in range(0, len(self.spine)):
			
			contentTitle = self.spine[ spineIndex ][0]
			contentRelPath = self.spine[ spineIndex ][1]
			contentAbsPath = path.join( ncxAbsPath, contentRelPath )

			# Creating the soup object for the content
			with open( contentAbsPath, 'r') as temp_contentFile:
				contentSoup = BeautifulSoup( temp_contentFile.read(), 'html.parser' )
			
			# Getting paths for navigations links
			previousContentRelPath = ''
			nextContentRelPath = ''
			if( spineIndex - 1 >= 0 ):
				previousContent = self.spine[ spineIndex - 1 ][1]
				previousContentRelPath = getRelativePath( contentRelPath, previousContent )
			if( spineIndex + 1 < len(self.spine) ):
				nextContent = self.spine[ spineIndex + 1 ][1]
				nextContentRelPath = getRelativePath( contentRelPath, nextContent )
			bookIndexRelPath = getRelativePath( contentAbsPath, bookIndexAbsPath )

			# Modifying the content Html
			contentSoup = self.addContainers( contentSoup, bookIndexRelPath, previousContentRelPath, nextContentRelPath )
			with open( contentAbsPath, 'w') as temp_contentFile:
				temp_contentFile.write( str(contentSoup) )
		
			# Adding content at the book index
			contentIndexLiTag = bookIndexSoup.new_tag('li')
			contentIndexLinkTag = bookIndexSoup.new_tag('a', href= path.join(ncxRelPath, contentRelPath ) )
			contentIndexLinkTag.string = contentTitle
			contentIndexLiTag.append(contentIndexLinkTag)
			bookIndexSoup.find(id='bookIndexUl').append( contentIndexLiTag )

	# Writing book index content
		with open( bookIndexAbsPath, 'w') as temp_bookIndex:
			temp_bookIndex.write( bookIndexSoup.prettify() )

# Add the navigation links
	def addContainers(self, soup, bookIndexPath, previousHref='', nextHref=''):
	
	# Divs
		buttonsDivTag = soup.new_tag('div', id='contentButtonDiv', style="position: sticky; top: 0;")
		soup.body.insert(0, buttonsDivTag )

		topNavigationTag = soup.new_tag('div', id='topNavigationDiv')
		soup.body.insert(1, topNavigationTag )
		bottomNavigationTag = soup.new_tag('div', id='bottomNavigationDiv')
		soup.body.append( bottomNavigationTag )

	# Buttons 
		buttonIncreaseFontTag = soup.new_tag('button', onclick='increaseFont(5)')
		buttonIncreaseFontTag.string = "Increase font"
		buttonDecreaseFontTag = soup.new_tag('button', onclick='increaseFont(-5)')
		buttonDecreaseFontTag.string = "Decrease font"
		soup.body.find(id='contentButtonDiv').append( buttonIncreaseFontTag )
		soup.body.find(id='contentButtonDiv').append( buttonDecreaseFontTag )
		
		scriptFontTag = soup.new_tag('script', type='text/javascript')
		scriptFontTag.string = """
	function increaseFont(size){
		var body = document.getElementsByTagName('body')[0];
		size += parseInt(window.getComputedStyle(body)['font-size']);
		body.style.fontSize = size.toString() + 'px';
	}

	function increaseFont_shortcut(e){
		increaseFont(e.data);
	}
	window.addEventListener("message", increaseFont_shortcut, false);
		"""
		soup.body.insert_after( scriptFontTag )
	
	# Book Index
		topBookIndexTag = soup.new_tag('a', href=bookIndexPath)
		topBookIndexTag.string = 'Book Index'
		bottomBookIndexTag = soup.new_tag('a', href=bookIndexPath)
		bottomBookIndexTag.string = 'Book Index'
		soup.body.find(id='topNavigationDiv').append(topBookIndexTag)
		soup.body.find(id='bottomNavigationDiv').append(bottomBookIndexTag)

	# Previous
		if( previousHref != '' ):
			topPreviousTag = soup.new_tag('a', href=previousHref)
			topPreviousTag.string = 'Previous'
			bottomPreviousTag = soup.new_tag('a', href=previousHref)
			bottomPreviousTag.string = "Previous"
			soup.find(id='topNavigationDiv').append(topPreviousTag)
			soup.find(id='bottomNavigationDiv').append(bottomPreviousTag)
	# Next
		if( nextHref != '' ):
			topNextTag = soup.new_tag('a', href=nextHref)
			topNextTag.string = 'Next'
			bottomNextTag = soup.new_tag('a', href=nextHref)
			bottomNextTag.string = "Next"
			soup.find(id='topNavigationDiv').append(topNextTag)
			soup.find(id='bottomNavigationDiv').append(bottomNextTag)

		return soup

"""
# Returns a dic with the path (relative) to every item. separates xhtml from other types
	def loadInfoFromContentOpf(self):
		
		contentOpfFile = open( path.join(self.contentOpfInfos[0], self.contentOpfInfos[1]) )
		root = ET.fromstring( contentOpfFile.read() )
	# Getting and setting the namespace
		ns = {'ns': root.tag[1: root.tag.find('}')]}
	# Getting the manifest items
		manifest = root.find('ns:manifest', ns)
		epubContentItems = manifest.findall('ns:item', ns)
	# Getting spine items refs
		spine = root.find('ns:spine', ns)
		epubSpineIds = [ item.attrib['idref'] for item in spine.findall('ns:itemref', ns) ]

	# Getting the path (href) to every item
		epubContentsInfos = {'xhtml': {}, 'other': {}}
		for item in epubContentItems:
			if( item.attrib['media-type'] == 'application/xhtml+xml' and item.attrib['id'] in epubSpineIds):
				epubContentsInfos['xhtml'][ item.attrib['id'] ] = item.attrib['href']
			else:
				epubContentsInfos['other'][ item.attrib['id'] ] = item.attrib['href']
		return epubContentsInfos, epubSpineIds
"""


if __name__ == '__main__':
	WebBook( argv[1], argv[2] )
