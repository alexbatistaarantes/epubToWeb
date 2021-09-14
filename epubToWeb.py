#!/bin/env python3

from os import path, getcwd, mkdir, scandir, listdir
from bs4 import BeautifulSoup
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from shutil import copy, rmtree
import argparse

from functions import *

__location__ = path.realpath( path.join( getcwd(), path.dirname(__file__) ) )

BOOK_MAIN_FILE_NAME = 'book.html'
BOOK_INDEX_FILE_NAME = 'bookIndex.html'
BOOK_CONTENT_FOLDER_NAME = 'bookContent'
EXTRACTED_EPUB_FOLDER_NAME = 'extractedEpub'
FAVICON_FILE_NAME = 'favicon.png'
ITEMS_SCRIPT_FILE_NAME = 'itemsScript.js'

class WebBook():
    
    # self.
    #   epub: epub file
    #   absPath: absolute path of the web book
    #   bookContentAbsPath: absolute path of the book content folder inside the web book folder
    #   extractedEpubAbsPath: absolute path of the extracted epub content inside the web book folder
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
        try:
            opfFileAbsPath = findFileByExtension( self.filesAbsPathList, '.opf')
            opfSpine = getSpineFromOpf( opfFileAbsPath )
        except:
            print("An error ocurred when reading the opf file.")
            print("Aborting execution.")
            deleteFolder( self.absPath )
        
        self.spine = opfSpine
        self.infos = {'title': '', 'author': []}

        # Getting info from ncx file to get titles for paths, if they exist in the ncx
        try:
            ncxFileAbsPath = findFileByExtension( self.filesAbsPathList, '.ncx')
            with open( ncxFileAbsPath, 'r') as ncxFile:
                ncxSpine, self.infos = getSpineFromNcx( ncxFile.read(), path.split(ncxFileAbsPath)[0] )
            
            for spineItem in self.spine:
                for ncxSpineItem in ncxSpine:
                    if( strStartsWith(ncxSpineItem[1], spineItem[1]) ):
                        spineItem[0] = ncxSpineItem[0]
        except:
            self.spine = opfSpine
        
        # Getting paths (relatives to the content.opf folder where found) from every item
        ##  self.epubContentsInfos, self.epubSpineIds = self.loadInfoFromContentOpf()
        
        # Copying files to web book
        copy( path.join(__location__, BOOK_MAIN_FILE_NAME), self.absPath )
        copy( path.join(__location__, BOOK_INDEX_FILE_NAME), self.absPath )
        copy( path.join(__location__, FAVICON_FILE_NAME), self.absPath )
        copy( path.join(__location__, ITEMS_SCRIPT_FILE_NAME), self.absPath )
        copy( epubFileAbsPath, self.absPath )
      
        # If infos was loaded
        if( self.infos['title'] != '' ):
            self.addInfos()
    
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
            bookRootRelPath = getRelativePath( contentAbsPath, path.join(self.absPath,'') )
            
            # Modifying the content Html
            contentSoup = self.addContainers( contentSoup, bookRootRelPath, previousContentRelPath, nextContentRelPath )
            with open( contentAbsPath, 'w') as temp_contentFile:
                temp_contentFile.write( str(contentSoup) )
        
            # Adding content at the book index
            contentIndexLiTag = bookIndexSoup.new_tag('li')
            contentIndexLinkTag = bookIndexSoup.new_tag('a', attrs={'class':'navLink', 'href':path.join(ncxRelPath, contentRelPath ), 'value':path.join(ncxRelPath, contentRelPath) } )
            contentIndexLinkTag.string = contentTitle
            contentIndexLiTag.append(contentIndexLinkTag)
            bookIndexSoup.find(id='bookIndexUl').append( contentIndexLiTag )

    # Writing book index content
        with open( bookIndexAbsPath, 'w') as temp_bookIndex:
            temp_bookIndex.write( bookIndexSoup.prettify() )

# Add the navigation links
    def addContainers(self, soup, bookRootPath, previousHref='', nextHref=''):
    
    # Divs
        buttonsDivTag = soup.new_tag('div', id='contentButtonDiv', style="position: sticky; top: 0;")
        soup.body.insert(0, buttonsDivTag )

        topNavigationTag = soup.new_tag('div', id='topNavigationDiv', class_='navigationDiv')
        soup.body.insert(1, topNavigationTag )
        bottomNavigationTag = soup.new_tag('div', id='bottomNavigationDiv', class_='navigationDiv')
        soup.body.append( bottomNavigationTag )
        
        # Buttons
        buttonShiftThemeTag = soup.new_tag('button', id='shiftTheme_button', onclick='shiftTheme()', value='dark')
        buttonShiftThemeTag.string = 'Shift Theme'
        buttonIncreaseFontTag = soup.new_tag('button', onclick='increaseFont(5)')
        buttonIncreaseFontTag.string = "Increase font"
        buttonDecreaseFontTag = soup.new_tag('button', onclick='increaseFont(-5)')
        buttonDecreaseFontTag.string = "Decrease font"
        soup.body.find(id='contentButtonDiv').append( buttonIncreaseFontTag )
        soup.body.find(id='contentButtonDiv').append( buttonDecreaseFontTag )
        soup.body.find(id='contentButtonDiv').append( buttonShiftThemeTag )
        
        scriptPath = path.join(bookRootPath, ITEMS_SCRIPT_FILE_NAME)
        scriptLinkTag = soup.new_tag('script', type='text/javascript', src=scriptPath)
        soup.head.append( scriptLinkTag )
        
    # Navigation Links
        linksStyle = 'margin-right: 5px;'

    # Book Index
        bookIndexPath = path.join(bookRootPath, BOOK_INDEX_FILE_NAME)
        topBookIndexTag = soup.new_tag('a', attrs={'class':'bookIndexLink navLink', 'href':bookIndexPath, 'value':bookIndexPath, 'style':linksStyle} )
        topBookIndexTag.string = 'Book Index'
        bottomBookIndexTag = soup.new_tag('a', attrs={'class':'bookIndexLink navLink', 'href':bookIndexPath, 'value':bookIndexPath, 'style':linksStyle} )
        bottomBookIndexTag.string = 'Book Index'
        soup.body.find(id='topNavigationDiv').append(topBookIndexTag)
        soup.body.find(id='bottomNavigationDiv').append(bottomBookIndexTag)

    # Previous
        if( previousHref != '' ):
            topPreviousTag = soup.new_tag('a', attrs={'class':'previousPageLink navLink', 'href':previousHref, 'value': previousHref, 'style':linksStyle} )
            topPreviousTag.string = 'Previous'
            soup.find(id='topNavigationDiv').append(topPreviousTag)

            bottomPreviousTag = soup.new_tag('a', attrs={'class':'previousPageLink navLink', 'href':previousHref, 'value':previousHref, 'style':linksStyle} )
            bottomPreviousTag.string = "Previous"
            soup.find(id='bottomNavigationDiv').append(bottomPreviousTag)

    # Next
        if( nextHref != '' ):
            topNextTag = soup.new_tag('a', attrs={'class':'nextPageLink navLink', 'href':nextHref, 'value':nextHref, 'style':linksStyle} )
            topNextTag.string = 'Next'
            soup.find(id='topNavigationDiv').append(topNextTag)

            bottomNextTag = soup.new_tag('a', attrs={'class':'nexPagetLink navLink', 'href':nextHref, 'value':nextHref, 'style':linksStyle} )
            bottomNextTag.string = "Next"
            soup.find(id='bottomNavigationDiv').append(bottomNextTag)

        return soup

    def addInfos(self):
        bookMainPath = path.join(self.absPath, BOOK_MAIN_FILE_NAME)
        with open( bookMainPath, 'r' ) as bookFile:
            bookSoup = BeautifulSoup( bookFile.read(), 'html.parser' )
        
        bookSoup.find('title').string = self.infos['title']
            
        with open( bookMainPath, 'w' ) as bookFile:
            bookFile.write( str(bookSoup) )


if __name__ == '__main__':

    parser = argparse.ArgumentParser( prog = 'epubToWeb' )
    parser.add_argument( 'epubFile',  help="Defines the path of the epub file." )
    parser.add_argument( 'webBookFolder',  help="Defines the path of the web book folder." )
    args = parser.parse_args()

    epubFilePath = args.epubFile #argv[1]
    webBookPath = args.webBookFolder #argv[2]
    if( webBookPath[-1] == '/' ):
        webBookPath = webBookPath[0:-1]
    WebBook( epubFilePath, webBookPath )
