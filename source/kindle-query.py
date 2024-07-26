#!/usr/bin/env python3
#Sunny ☀️   🌡️+44°F (feels +39°F, 41%) 🌬️↘2mph 🌗 Tue Feb 14 06:18:23 2023
#W7Q1 – 45 ➡️ 319 – 279 ❇️ 85

import os
import sqlite3
import json
from config import  log, KINDLE_APP, XML_CACHE,KINDLE_CONTENT, BOOK_CONTENT_SYMBOL,GHOST_RESULTS, CACHE_FOLDER_IMAGES,MY_URL_STRING, SEARCH_SCOPE, Book, IBOOKS_PATH, TARGET_LIBRARY
from time import time
import xmltodict
import urllib.request
import sys
import base64
import biplist
import pickle
from kindle_fun import buildKindleNew


MYINPUT = sys.argv[1].casefold()


#initializing JSON output
result = {"items": [], "variables":{}}





def getDownloadedBooks(basepath):
	
	myContentBooks = []
	
	# List all subdirectories using scandir()
	try:
		with os.scandir(basepath) as entries:
			for entry in entries:
				if entry.is_dir():
					myContentBooks.append(entry.name.split("_")[0])
		return myContentBooks
	except:
		result= {"items": [{
		"title": "Error: Cannot find Kindle directory",
		"subtitle": basepath,
		"arg": "",
		"icon": {

				"path": "icons/Warning.png"
			}
		}]}
		print (json.dumps(result))

def getXML(myFile, downloaded):
	## Importing the XML table

	with open(myFile) as xml_file:
		data_dict = xmltodict.parse(xml_file.read())
		xml_file.close()


	result = {"items": []}
	myBooks = data_dict['response']['add_update_list']['meta_data']

	for myBook in myBooks:
		if isinstance(myBook['authors']['author'], list):
			myBook ['authorString'] = " - ".join (str(auth['#text']) for auth in myBook['authors']['author'])

		else:
			myBook ['authorString'] = myBook['authors']['author']['#text']


	if SEARCH_SCOPE == "Title":
		myFilteredBooks = [i for i in myBooks if MYINPUT in i['title']['#text'].casefold()]

	elif SEARCH_SCOPE == "Author":
		myFilteredBooks = [i for i in myBooks if (MYINPUT in i['authorString'].casefold())]    
	elif SEARCH_SCOPE == "Both":
		myFilteredBooks = [i for i in myBooks if (MYINPUT in i['authorString'].casefold()) or (MYINPUT in i['title']['#text'].casefold())]


	if GHOST_RESULTS == '0':
		myFilteredBooks = [i for i in myFilteredBooks if (i['ASIN'] in downloaded)]

	if MYINPUT and not myFilteredBooks:
		result["items"].append({
			"title": "No matches in your library",
			"subtitle": "Try a different query",
			"arg": "",
			"icon": {
				"path": "icons/Warning.png"
				}

				})


	totalLibrary = (len(myFilteredBooks))
	myCounter = 0

	for book in myFilteredBooks:


		if book['ASIN'] in downloaded:
			BookSymbol = BOOK_CONTENT_SYMBOL
			bookURL = f"{KINDLE_CONTENT}{book['ASIN']}_EBOK/{book['ASIN']}_EBOK.azw"
			ICON_PATH = f"{CACHE_FOLDER_IMAGES}{book['ASIN']}.01"
			if not os.path.exists(ICON_PATH):
				log ("retrieving image" + ICON_PATH)
				try:
					urllib.request.urlretrieve(f"{MY_URL_STRING}{book['ASIN']}.01", ICON_PATH)
				except urllib.error.URLError as e:
					log("Error retrieving image:", e.reason)  # Log the specific error reason


		elif GHOST_RESULTS == '1':
			BookSymbol = ""
			bookURL = f"https://www.amazon.com/dp/{book['ASIN']}"
			ICON_PATH = f"{CACHE_FOLDER_IMAGES}{book['ASIN']}.01"
			if not os.path.exists(ICON_PATH):
				log ("retrieving image" + ICON_PATH)
				try:
					urllib.request.urlretrieve(f"{MY_URL_STRING}{book['ASIN']}.01", ICON_PATH)
				except urllib.error.URLError as e:
					log("Error retrieving image:", e.reason)  # Log the specific error reason

		else:
			continue


		myCounter += 1
		result["items"].append({
			"title": book['title']['#text']+BookSymbol,
			'subtitle': f"{myCounter}/{totalLibrary} {book['authorString']}",
			'valid': True,

			"icon": {
				"path": ICON_PATH    
			},
			'arg': bookURL
				}) 



	print (json.dumps(result))









def get_ibooks(search_string):
	conn = sqlite3.connect(IBOOKS_PATH)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	c.execute('''SELECT "_rowid_",* FROM "main"."ZBKLIBRARYASSET" ORDER BY "_rowid_" ASC LIMIT 0, 49999;''')
	data = c.fetchall()
	books = []
	for row in data:
		row = dict(row)
		if checkMatch(search_string, row['ZAUTHOR'], row['ZTITLE']):
			book = Book(
				title=row['ZTITLE'],
				path=row['ZPATH'],
				author=row['ZAUTHOR'],
				book_desc=row['ZBOOKDESCRIPTION'],
				read_pct=row['ZREADINGPROGRESS'],
				
			)
			books.append(book)
	conn.close()

	if GHOST_RESULTS == '0':
		books = [book for book in books if book.path is not None]

	return books


def get_all_ibooks():
	conn = sqlite3.connect(IBOOKS_PATH)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	c.execute('''SELECT "_rowid_",* FROM "main"."ZBKLIBRARYASSET" ORDER BY "_rowid_" ASC LIMIT 0, 49999;''')
	data = c.fetchall()
	books = []
	for row in data:
		row = dict(row)
		
		book = Book(
			title=row['ZTITLE'],
			path=row['ZPATH'],
			author=row['ZAUTHOR'],
			book_desc=row['ZBOOKDESCRIPTION'],
			read_pct=row['ZREADINGPROGRESS'],
			
			)
		books.append(book)
	conn.close()
	# Save the list of books to a file
	with open('books.pkl', 'wb') as file:
		pickle.dump(books, file)
	
	



def serveiBooks(books, result):
    #result = {"items": []}
    for myBook in books:
        
        booksN = len(books)
        result["items"].append({
                "title": myBook.title,
                'subtitle': f"{booksN} – {myBook.author}",
                'valid': True,
                
                
                "icon": {
                    "path": 'icons/ibooks.png'
                },
                'arg': "resultString"
                    }) 
    return result




def main():
	main_start_time = time()
	

	if KINDLE_APP == "classic":

		myContentBooks = getDownloadedBooks(KINDLE_CONTENT) # output is a list of downloaded book ASINs
		log(myContentBooks)
		getXML(XML_CACHE, myContentBooks)

	elif KINDLE_APP == "new":

		mySQL = f"SELECT * FROM ZBOOK WHERE ZDISPLAYTITLE LIKE '%{MYINPUT}%'"
		mySQL = f"SELECT * FROM ZBOOK WHERE ZSYNCMETADATAATTRIBUTES LIKE '%{MYINPUT}%'"
		#log(mySQL)
		
		db_path = '/Users/giovanni/Library/Containers/com.amazon.Lassen/Data/Library/Protected/BookData.sqlite'
		table = 'ZBOOK'
		column = 'ZSYNCMETADATAATTRIBUTES'
		# eliminate leading and traling spaces from MYINPUT
		search_string = MYINPUT.strip()
		
		
		#result = search_blob_in_db_biplist(db_path, table, column, search_string)

		

		# Load the list of books from the file
		# with open('kindle_books.pkl', 'rb') as file:
		# 	result = pickle.load(file)
	
		# ibooks section
		#books = get_ibooks(search_string)
		#books = get_all_ibooks()
    # Load the list of books from the file
		# with open('books.pkl', 'rb') as file:
		# 	books = pickle.load(file)
		
	
		# serveiBooks(books, result)

		# print (json.dumps(result))
		buildKindleNew(KINDLE_CONTENT)



	main_timeElapsed = time() - main_start_time
	log(f"\nscript duration: {round (main_timeElapsed,3)} seconds")

if __name__ == '__main__':
	main ()



