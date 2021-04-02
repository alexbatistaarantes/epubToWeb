#!/bin/env python3

from bs4 import BeautifulSoup
from os import path, scandir, listdir, mkdir
import sys

newFilesDirName = 'pages'

class Book():
	
	def __init__(self, filesPath, newBookPath):
		
		self.filesPath = filesPath
		if( self.getFiles() == 0 ):
			raise ValueError("Couldn't access the file's directory.")
		
		self.newBookPath = newBookPath
		if( self.createNewBookDir() == 0 ):
			raise ValueError("Couldn't create the new book's directory.")

		self.createNewBook()
	
	def createNewBook(self):
		
		with open( path.join(self.newBookPath, 'book.html'), 'w') as book:
			book.write(
"""
	<!DOCTYPE html>
	<html lang="en">
	<head>
		<meta charset="UTF-8">
		<title> Book </title>
	</head>
	<body>
		<button onclick="increaseWidth(-10)"> Decrease Width 10% </button>
		<button onclick="increaseWidth(10)"> Increase Width 10% </button>
		<button onclick="increaseHeight(-20)"> Decrease Height 20px </button>
		<button onclick="increaseHeight(20)"> Increase Height 20px </button>
		<br><br>
		<iframe id="book" src="bookIndex.html" frameborder="0" style="width: 50%; height: 300px;"></iframe>
	</body>
	<script type="text/javascript">
		function increaseWidth(size){
			var width = parseInt(document.getElementById('book').style.width);
			width += size;
			document.getElementById('book').style.width = width.toString() + '%';
		}
		function increaseHeight(size){
			var height = parseInt(document.getElementById('book').style.height);
			height += size;
			document.getElementById('book').style.height = height.toString() + 'px';
		}
	</script>

	</html>
"""
			)

		bookIndexContent = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title> Book Index </title>
</head>
<body>
	<div id="bookIndex">
		
	</div>
</body>
</html>
"""
		bookIndexSoup = BeautifulSoup( bookIndexContent, 'html.parser' )
		
		for fileIndex in range(0, self.filesLen) :
			fileName = self.files[fileIndex].name
			newFileAbsPath = path.join( self.newFilesAbsPath, fileName )

			newFile = open( newFileAbsPath, 'w' )
			newFileContent = self.addPageLinks( fileIndex )
			newFile.write( newFileContent )
			
			newFilePath = path.join( newFilesDirName, fileName )
			newFileIndexTag = bookIndexSoup.new_tag('a', href=newFilePath )
			newFileIndexTag.string = fileName
			bookIndexSoup.find(id="bookIndex").append( newFileIndexTag )
			brTag = bookIndexSoup.new_tag('br')
			bookIndexSoup.find(id='bookIndex').append( brTag )

		with open( path.join( self.newBookPath, 'bookIndex.html'), 'w' ) as bookIndex:
			bookIndex.write( bookIndexSoup.prettify() )

	def addPageLinks(self, fileIndex):
		
		# Getting content
		with open( self.files[ fileIndex ].path, 'r' ) as filePage:
			fileContent = filePage.read()
		
		pageSoup = BeautifulSoup( fileContent, 'html.parser')
	
		topNavLinksTag = pageSoup.new_tag('div', id='topNavigationLinks')
		pageSoup.body.insert(1, topNavLinksTag )
		bottomNavLinksTag = pageSoup.new_tag('div', id='bottomNavigationLinks')
		pageSoup.body.append( bottomNavLinksTag )

		# PREVIOUS PAGE LINK
		previousFileIndex = fileIndex - 1
		if( previousFileIndex >= 0 ):
			previousPageTag = pageSoup.new_tag('a', href=self.files[previousFileIndex].name )
			previousPageTag.string = '  Previous chapter  '
			pageSoup.find(id='topNavigationLinks').append(previousPageTag)
			pageSoup.find(id='bottomNavigationLinks').append( previousPageTag )

		# NEXT PAGE LINK
		nextFileIndex = fileIndex + 1
		if( nextFileIndex < self.filesLen ):
			nextPageTag = pageSoup.new_tag('a', href=self.files[nextFileIndex].name )
			nextPageTag.string = '  Next chapter  '
			pageSoup.find(id='topNavigationLinks').append( nextPageTag )
			pageSoup.find(id='bottomNavigationLinks').append( nextPageTag )
		
		# INDEX PAGE LINK
		indexPageTag = pageSoup.new_tag('a', href='../bookIndex.html')
		indexPageTag.string = "  Book Index  "
		pageSoup.find(id='topNavigationLinks').insert(0, indexPageTag)
		pageSoup.find(id='bottomNavigationLinks').append(indexPageTag)

		return pageSoup.prettify()

	def getFiles(self):
		try:
			self.files = sorted( scandir( self.filesPath ), key=lambda x: (x.is_dir(), x.name) )
			self.filesLen = len( self.files )
			return 1
		except:
			return 0
	def createNewBookDir(self):
		try:
			mkdir( self.newBookPath )
		except FileExistsError:
			pass
		except:
			return 0

		self.newFilesAbsPath = path.join( self.newBookPath, newFilesDirName )
		try:
			mkdir( self.newFilesAbsPath )
		except:
			raise ValueError("Please delete the "+ self.newFilesAbsPath +" folder.")

		return 1

if __name__ == '__main__':

	if( len(sys.argv) == 3 ):
		book = Book( sys.argv[1], sys.argv[2] )
	else:
		print("""
	main.py HTML_FILES_PATH NEW_BOOK_PATH

	Extract the .epub file and find the folder where the .html files are stored.
		""")