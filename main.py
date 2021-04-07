#!/bin/env python3

from os import path, getcwd, mkdir, scandir, listdir
from sys import argv
from bs4 import BeautifulSoup
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from shutil import copy

__location__ = path.realpath( path.join( getcwd(), path.dirname(__file__) ) )

class WebBook():
	
	def __init__(self, epubAbsPath, webBookAbsPath):
	
	# Loading file epub before creating folder
		self.epub = self.loadEpub( epubAbsPath )
	# Creating web book folder
		self.createFolder( webBookAbsPath )
		self.absPath = webBookAbsPath
	# Creating the folder where the book contents will be
		self.bookContentFolderName = 'bookContent'
		self.createFolder( path.join(self.absPath, self.bookContentFolderName) )
	# Creating temporary folder inside web book folder to extract epub files
		extractedEpubFolderName = 'extractedEpub'
		self.createFolder( path.join(self.absPath, extractedEpubFolderName) )
	# Extracting epub files
		self.extractEpub( self.epub, path.join(self.absPath, extractedEpubFolderName) )
	# Getting tree of files from epub
		self.epubTree = self.createTreeOfContent( path.join(self.absPath, extractedEpubFolderName) )
	# Getting paths (relatives to the content.opf folder where found) from every item
		self.epubContentsInfos, self.epubSpineIds = self.loadInfoFromContentOpf()
	# Copying book.html to web book
		copy( path.join(__location__, 'book.html'), self.absPath )

		self.copyEpubContent()

	def copyEpubContent(self):
		bookRelativePath = self.contentOpfInfos[0]
		bookContentAbsPath = path.join( self.absPath, self.bookContentFolderName )
		
	# Copying contents that are not from the spine
		for contentId in self.epubContentsInfos['other'].keys():
			contentPath = self.epubContentsInfos['other'][ contentId ]
			contentPaths = contentPath.split('/')
			if( len(contentPaths) > 1):
				temp_path = bookContentAbsPath
				for index in range(0, len(contentPaths)-1):
					temp_path = path.join(temp_path, contentPaths[index] )
					self.createFolder( temp_path )
			copy( path.join( bookRelativePath, contentPath ), path.join(bookContentAbsPath, contentPath ))
	
	# Getting the bookIndex.html content
		with open( path.join(__location__, 'bookIndex.html'), 'r' ) as temp_bookIndex:
			bookIndexSoup = BeautifulSoup( temp_bookIndex.read(), 'html.parser')
		bookContentsAbsPath = path.join( self.absPath, self.bookContentFolderName )
		
	# Copying and modifying the spine files
		for contentSpineIndex in range(0, len(self.epubSpineIds)):
			contentId = self.epubSpineIds[ contentSpineIndex ]
			contentPath = self.epubContentsInfos['xhtml'][ contentId ]
			contentPaths = contentPath.split('/')
		# Creating folders
			if( len(contentPaths) > 0 ):
				temp_path = bookContentAbsPath
				for index in range(0, len(contentPaths)-1):
					temp_path = path.join( temp_path, contentPaths[ index ])
					self.createFolder( temp_path )
		# Creating the soup object for the content
			with open(path.join(bookRelativePath, contentPath), 'r') as temp_contentFile:
				contentSoup = BeautifulSoup( temp_contentFile.read(), 'html.parser' )
			
		# Getting href for navigations links
			previousHref = ''
			nexttHref = ''
			if( contentSpineIndex-1 >= 0 ):
				previousHref = self.epubContentsInfos['xhtml'][ self.epubSpineIds[ contentSpineIndex-1] ]
				previousHref = self.getRelativePath( contentPath, previousHref )
			if( contentSpineIndex+1 < len(self.epubSpineIds) ):
				nextHref = self.epubContentsInfos['xhtml'][ self.epubSpineIds[ contentSpineIndex+1] ]
				nextHref = self.getRelativePath( contentPath, nextHref )
			bookIndexPath = ''
			for i in contentPaths: bookIndexPath += '../'

		# Modifying the content Html
			contentSoup = self.addContainers( contentSoup, bookIndexPath, previousHref, nextHref )
			with open(path.join(bookContentsAbsPath, contentPath), 'w') as temp_contentFile:
				temp_contentFile.write( contentSoup.prettify() )
		
		# Adding content at the book index
			contentIndexLiTag = bookIndexSoup.new_tag('li')
			contentIndexLinkTag = bookIndexSoup.new_tag('a', href= path.join(self.bookContentFolderName, contentPath ) )
			contentIndexLinkTag.string = contentSoup.find('title').string
			contentIndexLiTag.append(contentIndexLinkTag)
			bookIndexSoup.find(id='bookIndexUl').append( contentIndexLiTag )

	# Writing book index content
		with open( path.join(self.absPath, 'bookIndex.html'), 'w' ) as temp_bookIndex:
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
		"""
		soup.body.insert_after( scriptFontTag )
	
	# Book Index
		topBookIndexTag = soup.new_tag('a', href= path.join(bookIndexPath, 'bookIndex.html'))
		topBookIndexTag.string = 'Book Index'
		bottomBookIndexTag = soup.new_tag('a', href= path.join(bookIndexPath, 'bookIndex.html'))
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

# Get the relative path for the first path link the second one
	def getRelativePath(self, firstPath, secondPath):
		
		splittedFirstPath = firstPath.split('/')
		splittedSecondPath = secondPath.split('/')

		while( len(splittedFirstPath) > 1 ):
			if splittedFirstPath[0] == splittedSecondPath[0]:
				del splittedFirstPath[0]
				del splittedSecondPath[0]
			else:
				break

		relativePath = ''

	# Second path is above
		if len(splittedFirstPath) > 1:
			for index in range( len(splittedFirstPath) ): relativePath += '../'
			for folder in splittedSecondPath: relativePath = path.join(relativePath, folder)
	# Second path is a neighbour or is under the first
		else:
			for folder in splittedSecondPath: relativePath = path.join(relativePath, folder)

		return relativePath

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

# Creating a dict that represents the tree of content for the extracted epub
	def createTreeOfContent(self, absPath):
		tree = {'/':{}}
		scanDir = scandir(absPath)
		for scanFile in scanDir:
			if( scanFile.is_file() ):
				tree['/'][scanFile.name] = scanFile
			# Verifying if it's the [content].opf file
				if( (path.splitext(scanFile.name)[1]).lower() == '.opf' ):
					self.contentOpfInfos = (absPath, scanFile.name)
			else:
				scanFileAbsPath = path.join( absPath, scanFile.name )
				tree[scanFile.name] = self.createTreeOfContent( scanFileAbsPath )
		return tree
	def extractEpub(self, epub, extractedEpubAbsPath ):
		epub.extractall( extractedEpubAbsPath )
	def loadEpub(self, epubAbsPath ):
		epub = ZipFile( epubAbsPath )
		return epub
	def createFolder(self, path):
		try:
			mkdir( path )
		except:
			pass

	def formatData(self,t,s):
		if not isinstance(t,dict) and not isinstance(t,list):
			print("\t"*s+str(t))
		else:
			for key in t:
				print("\t"*s+str(key))
				if not isinstance(t,list):
					self.formatData(t[key],s+1)

if __name__ == '__main__':
	WebBook( argv[1], argv[2] )
