#!/bin/env python3

from os import path, mkdir, scandir, listdir, getcwd
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from shutil import copy, rmtree

__location__ = path.realpath( path.join( getcwd(), path.dirname(__file__) ) )

def getSpineFromNcx( ncxContent ):
	# spine is the files and their order that will appear in the book index

	spine = []
	metadata = {'title':'', 'author':[]}

	root = ET.fromstring( ncxContent )
	ns = {'ns': root.tag[ 1: root.tag.find('}') ] }
	
	navMap = root.find('ns:navMap', ns)
	for navPoint in navMap.findall('ns:navPoint', ns):
		
		# in cases where there is navpoints inside one another
		childNavPoints = navPoint.findall('ns:navPoint', ns)
		if( len(childNavPoints) > 0 ):
			for navPoint_2 in childNavPoints:
				pointId = str( navPoint_2.attrib['id'] )

				try: # in case there isn't any content to get the path
					content = navPoint_2.find('ns:content', ns)
					pointPath = content.attrib['src']
					
					# in cases where the id is appended at the end of the paths
					pointPath = endsWith( pointPath, '#'+pointId )

					try: # in case there isn't any navLabel or text to get the title
						navLabel = navPoint_2.find('ns:navLabel', ns)
						pointTitle = navLabel.find('ns:text', ns).text
					except:
						pointTitle = pointPath

					spine.append( [ pointTitle, pointPath ] )
				except:
					print( "An exception ocurred and some content could be lost in the book index." )
		else:
			pointId = str(navPoint.attrib['id'])

			try: # in case there isn't any content to get the path
				content = navPoint.find('ns:content', ns)
				pointPath = content.attrib['src']
					
				# in cases where the id is appended at the end of the paths
				pointPath = endsWith( pointPath, '#'+pointId )

				try: # in case there isn't any navLabel or text to get the title
					navLabel = navPoint.find('ns:navLabel', ns)
					pointTitle = navLabel.find('ns:text', ns).text
				except:
					pointTitle = pointPath

				spine.append( [ pointTitle, pointPath ] )
			except:
				print( "An exception ocurred and some content could be lost in the book index." )		
	return spine

# if str1 ends with str2, return str1 cutting str2
def endsWith( str1, str2 ):
	len1 = len(str1)
	len2 = len(str2)

	if( str1[ len1-len2: len1 ] == str2 ):
		return str1[0:len1-len2]
	return str1

# Get the relative path for the first path link the second one
def getRelativePath( firstPath, secondPath ):
	
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
		for index in range( len(splittedFirstPath) - 1): relativePath += '../'
		for folder in splittedSecondPath: relativePath = path.join(relativePath, folder)
	# Second path is a neighbour or is under the first
	else:
		for folder in splittedSecondPath: relativePath = path.join(relativePath, folder)

	return relativePath

# Returns the path of the first file found with the extensions passed
def findFileByExtension( filesPathList, extension ):
	if( extension[0] != '.'):
		extension = '.' + extension.lower()

	for filePath in filesPathList:
		fileExtension = path.splitext( filePath )[1].lower()
		if( fileExtension == extension ):
			return filePath
	return ''

# Copy a folder and every content in it to the destiny folder
def copyFolderRecursively( originFolderPath, destinyFolderPath ):
	
	try:
		listdir( destinyFolderPath )
	except FileNotFoundError:
		try:
			createFolder( destinyFolderPath )
		except:
			raise

	scanFiles = scandir( originFolderPath )
	paths = [ destinyFolderPath ]
	for scanFile in scanFiles:
		if( scanFile.is_file() ):
			originFilePath = path.join( originFolderPath, scanFile.name )
			destinyFilePath = path.join( destinyFolderPath, scanFile.name )
			copy( originFilePath, destinyFilePath )

			paths.append( destinyFilePath )
		elif( scanFile.is_dir() ):
			temp_originFolderPath = path.join( originFolderPath, scanFile.name )
			temp_destinyFolderPath = path.join( destinyFolderPath, scanFile.name )
			temp_paths = copyFolderRecursively( temp_originFolderPath, temp_destinyFolderPath )
			paths.extend( temp_paths )
	
	return paths

"""
# Creating a dict that represents the tree of content for the extracted epub
def getTreeOfContent(self, absPath):
	tree = {'/':{}}
	scanDir = scandir(absPath)
	for scanFile in scanDir:
		if( scanFile.is_file() ):
			tree['/'][scanFile.name] = scanFile

			# Verifying if it's the [toc].ncx file
			if( (path.splitext(scanFile.name)[1]).lower() == '.ncx' ):
				self.tocInfos = (absPath, scanFile.name)
			# Verifying if it's the [content].opf file
			elif( (path.splitext(scanFile.name)[1]).lower() == '.opf' ):
				self.contentOpfInfos = (absPath, scanFile.name)
		else:
			scanFileAbsPath = path.join( absPath, scanFile.name )
			tree[scanFile.name] = getTreeOfContent( scanFileAbsPath )
	return tree
"""

def extractEpub( epub, extractedEpubAbsPath ):
	try:
		epub.extractall( extractedEpubAbsPath )
	except:
		print("Couldn't extract the epub.")
		print("Aborting the execution.")
		raise

def loadEpub( epubAbsPath ):
	try:
		epub = ZipFile( epubAbsPath )
		return epub
	except:
		print("Couldn't load the epub file {}.".format(epubAbsPath))
		print("Aborting the execution.")
		raise

def createFolder( path ):
	try:
		mkdir( path )
	except:
		print("Couldn't create {} folder.".format(path))
		print("Aborting the execution.")
		raise

def deleteFolder( path ):
	rmtree( path )

### nao lembro oque e isso
def formatData(t,s):
	if not isinstance(t,dict) and not isinstance(t,list):
		print("\t"*s+str(t))
	else:
		for key in t:
			print("\t"*s+str(key))
			if not isinstance(t,list):
				self.formatData(t[key],s+1)

if __name__ == '__main__':
	pass
