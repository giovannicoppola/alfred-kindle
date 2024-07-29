## support functions for the alfred-eBook workflow

from datetime import datetime, date
from config import log, Book, KINDLE_PICKLE, IBOOKS_PICKLE, KINDLE_PATH,CACHE_FOLDER_IMAGES_KINDLE, CACHE_FOLDER_IMAGES_IBOOKS, MY_URL_STRING
import os
import sqlite3
import biplist
import pickle
import xmltodict
import json
import urllib.request
import shutil



			
def checkMatch (search_string, authorName, title):
				for s in search_string.split():
					if s not in authorName.casefold() and s not in title.casefold():
						return False
				return True


def checkTimeStamp (myFile, timestamp):
	# a function to check the timestamp of the kindle library file and update if it is different from the one stored in a file

	
	new_time = int(os.path.getmtime(myFile))
	
	if not os.path.exists(timestamp):
		with open(timestamp, "w") as f:
			f.write(str(new_time))
			f.close
	
	## checking the timestamp
	with open(timestamp) as f:
		old_time = int(f.readline()) #getting the old UNIX timestamp
		f.close


	if new_time != old_time:
		
		with open(timestamp, "w") as f:
			f.write(str(new_time))
			f.close
		return True
	else:
		return False
	
def getDownloadedASINs(basepath):
	
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

def get_kindleClassic (myFile, downloaded):
	## Importing the XML table

	with open(myFile) as xml_file:
		data_dict = xmltodict.parse(xml_file.read())
		xml_file.close()


	
	myBooks = data_dict['response']['add_update_list']['meta_data']
	books = []

	for myBook in myBooks:
		if isinstance(myBook['authors']['author'], list):
			myBook ['authorString'] = "; ".join (str(auth['#text']) for auth in myBook['authors']['author'])

		else:
			myBook ['authorString'] = myBook['authors']['author']['#text']


	
		if myBook['ASIN'] in downloaded:
			
			bookURL = f"{KINDLE_PATH}{myBook['ASIN']}_EBOK/{myBook['ASIN']}_EBOK.azw"
			ICON_PATH = f"{CACHE_FOLDER_IMAGES_KINDLE}{myBook['ASIN']}.01"
			isDownloaded = 1
			loaned = 0
			if not os.path.exists(ICON_PATH):
				log ("retrieving image" + ICON_PATH)
				try:
					urllib.request.urlretrieve(f"{MY_URL_STRING}{myBook['ASIN']}.01", ICON_PATH)
				except urllib.error.URLError as e:
					log("Error retrieving image:", e.reason)  # Log the specific error reason


		else:
			isDownloaded = 0
			loaned = 1
			bookURL = f"https://www.amazon.com/dp/{myBook['ASIN']}"
			ICON_PATH = f"{CACHE_FOLDER_IMAGES_KINDLE}{myBook['ASIN']}.01"
			if not os.path.exists(ICON_PATH):
				log ("retrieving image" + ICON_PATH)
				try:
					urllib.request.urlretrieve(f"{MY_URL_STRING}{myBook['ASIN']}.01", ICON_PATH)
				except urllib.error.URLError as e:
					log("Error retrieving image:", e.reason)  # Log the specific error reason

		
		book = Book(
			title=myBook['title']['#text'],
			bookID=myBook['ASIN'],
			path=bookURL,
			icon_path=ICON_PATH,
			author=myBook['authorString'],
			book_desc="",
			read_pct=0,
			source="Kindle",
			loaned=loaned,
			downloaded=isDownloaded
			
			)
		books.append(book)

	# Save the list of books to a file
	with open(KINDLE_PICKLE, 'wb') as file:
		pickle.dump(books, file)

def fetchImageCover(epub_path, ICON_PATH):
	# a function to retrieve the cover image of the book from the ePUB file
	if os.path.exists(f"{epub_path}/cover.jpeg"):
		src_path = f"{epub_path}/cover.jpeg"
		dest_path = ICON_PATH
		shutil.copy2(src_path, dest_path)
		log ("cover image copied")
		return ICON_PATH
	else:
		log ("no cover image found")
		return "icons/ibooks.png"

	

def get_ibooks(myDatabase):
	books = []
	conn = sqlite3.connect(myDatabase)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	c.execute('''SELECT "_rowid_",* FROM "main"."ZBKLIBRARYASSET" ORDER BY "_rowid_" ASC LIMIT 0, 49999;''')
	data = c.fetchall()
	
	for row in data:
		row = dict(row)
		if row['ZSTATE'] == 5:
			continue
		elif row['ZSTATE'] == 3:
			downloaded = 0
		elif row['ZSTATE'] == 1:
			downloaded = 1
		
		
		
		# downloading the cover
			
		ICON_PATH = f"{CACHE_FOLDER_IMAGES_IBOOKS}{row['ZASSETID']}"

		if not os.path.exists(ICON_PATH) and row['ZCOVERURL'] is not None:
			try:
				urllib.request.urlretrieve(row['ZCOVERURL'], ICON_PATH)
			except urllib.error.URLError as e:
				log("Error retrieving image:", e.reason)  # Log the specific error reason

		
		elif not os.path.exists(ICON_PATH) and row['ZPATH'] is not None:
			if row['ZPATH'].endswith('.epub'):
				log ("trying to retrieve image from ePUB file: " + row['ZPATH'])
				try:
					ICON_PATH = fetchImageCover (row['ZPATH'], ICON_PATH)
				except:
					log("Error retrieving image") 
			else:
				ICON_PATH = "icons/ibooks.png"
		elif not os.path.exists(ICON_PATH):
			ICON_PATH = "icons/ibooks.png"
			
		
		book = Book(
			title=row['ZTITLE'],
			bookID="",
			
			path=row['ZPATH'],
			icon_path=ICON_PATH,
			author=row['ZAUTHOR'],
			book_desc=row['ZBOOKDESCRIPTION'],
			read_pct=row['ZREADINGPROGRESS'],
			source="iBooks",
			loaned=0,
			downloaded=downloaded
			
			)
		books.append(book)

	conn.close()

	# Save the list of books to a file
	with open(IBOOKS_PICKLE, 'wb') as file:
		pickle.dump(books, file)
	
	
def get_kindle(myDatabase):
	"""
    a function to build the kindle database for the new kindle app
		
   
    """
    
	# Connect to the SQLite database
	conn = sqlite3.connect(myDatabase)
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()

	# Select the rows with BLOB data
	query = f"SELECT rowid, ZSYNCMETADATAATTRIBUTES, ZDISPLAYTITLE, ZRAWCURRENTPOSITION, ZRAWMAXPOSITION,ZRAWBOOKSTATE, ZBOOKID FROM ZBOOK WHERE ZRAWBOOKTYPE IN (10, 13)"

	cursor.execute(query)


	books = []
	loanCount = 0
	for row in cursor.fetchall():
		
		rowid, blob_data, title, currPos, maxPos, downStatus, asinRaw = row
		
        # Skip if blob_data is None
		if blob_data is None:
			authorName = ''
		else: 	# Attempt to decode the blob data to text
			try:
				plist_data = biplist.readPlistFromString(blob_data)
				# Search for the string in the decoded text
				authorRow = plist_data['$objects'].index('author')
				authorName = plist_data['$objects'][authorRow+1]
				
				if 'Purchase' in plist_data['$objects']:
						loaned = 0
						
				elif 'PublicLibraryLending' in plist_data['$objects']:
					loaned = 1
					loanCount += 1
					#log (f"Loaned! title: {title}, total: {loanCount}")
				
				if not isinstance(authorName, str):
					
					myAuthorIDs = authorName['NS.objects']
					myAuthorIDs = [int(str(uid).strip('Uid()')) for uid in myAuthorIDs]
					# Fetch elements from list B and join them
					authorName = '; '.join([plist_data['$objects'][i] for i in myAuthorIDs])
					
			except (biplist.InvalidPlistException, biplist.NotBinaryPlistException):
				log("Failed to decode BLOB data as a plist.")
				authorName = ''
			
			try:
				percentRead = currPos/maxPos

			except:
				percentRead = 0.0
			
			# downloading the cover
			ASIN = asinRaw[2:-2]
			ICON_PATH = f"{CACHE_FOLDER_IMAGES_KINDLE}{ASIN}.01"

			bookURL = f"https://www.amazon.com/dp/{ASIN}"
			
			if not os.path.exists(ICON_PATH):
				log ("retrieving image" + ICON_PATH)
				try:
					urllib.request.urlretrieve(f"{MY_URL_STRING}{ASIN}.01", ICON_PATH)
				except urllib.error.URLError as e:
					ICON_PATH = "icons/kindle.png"
					log("Error retrieving image:", e.reason)  # Log the specific error reason

			
			if downStatus == 3:
				downStatus = 1
			else:
				downStatus = 0
			 
		book = Book(
				title=title,
				bookID=ASIN,
				path=bookURL,
				icon_path=ICON_PATH,
				author=authorName,
				book_desc="",
				read_pct=percentRead,
				source = "Kindle",
				loaned=loaned,
				downloaded=downStatus
				)
		books.append(book)
		

            
	
	conn.close()
	# pickle the books object
	with open(KINDLE_PICKLE, 'wb') as file:
		pickle.dump(books, file)
	log ("building kindle database")
	log ("done 👍")
	return books



   

             
