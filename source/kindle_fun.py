## support functions for the alfred-kindle-ibook workflow

from datetime import datetime, date
from config import log, RefRate, CACHE_DATABASE_FILE, KINDLE_APP, GHOST_RESULTS, Book, KINDLE_CONTENT, DATA_FOLDER
import os
import sqlite3
import biplist
import pickle


def search_blob_in_db_biplist(db_path, table, column, search_string):
	# Connect to the SQLite database
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# Select the rows with BLOB data
	query = f"SELECT rowid, {column}, ZDISPLAYTITLE FROM {table} WHERE ZRAWBOOKTYPE = 10"
	cursor.execute(query)

	matching_rows = []

	for row in cursor.fetchall():
		rowid, blob_data, title = row
		# Skip if blob_data is None
		if blob_data is None:
			continue
		
		#log (rowid)
		# Attempt to decode the blob data to text
		try:
			plist_data = biplist.readPlistFromString(blob_data)
		except (biplist.InvalidPlistException, biplist.NotBinaryPlistException):
			log("Failed to decode BLOB data as a plist.")

		# Search for the string in the decoded text
		authorRow = plist_data['$objects'].index('author')
		authorName = plist_data['$objects'][authorRow+1]
		
		
		if isinstance(authorName, str):
			
			
			if checkMatch(search_string, authorName, title):
	#if (search_string in authorName.casefold()) or (search_string in title.casefold()):
				#log (authorName)
				#log (f"FOUND ONE: {title}")
				#matching_rows.append(rowid)
				result["items"].append({
					"title": f"{title}",

					'subtitle': f"{authorName}",
					'valid': True,
					"quicklookurl": '',
					'variables': {

					},
						# "mods": {

						# "control": {
						#     "valid": 'true',
						#     "subtitle": f"🧵 filter entire thread",
						#     "arg": r['Message_ThreadTopic'],
						#     'variables': {
						#         "mySource": 'thread',
						#         "threadTopic": r['Message_ThreadTopic']
						#     }
						# }
						# },
					"icon": {
						"path": f""
					},
					'arg': "myarg"
						}) 

				

	#log(matching_rows)
	conn.close()
	return result



def search_blob_in_db(db_path, table, column, search_string):
	# Connect to the SQLite database
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	
	# Select the rows with BLOB data
	query = f"SELECT rowid, {column} FROM {table}"
	cursor.execute(query)
	
	matching_rows = []
	
	for row in cursor.fetchall():
		rowid, blob_data = row
		if blob_data is None:
			continue

		# Attempt to decode the blob data to text
		try:
			# Try various text encodings
			text_data = blob_data.decode('latin-1')
		except UnicodeDecodeError:
			try:
				text_data = blob_data.decode('koi8-r')
			except UnicodeDecodeError:
				# If text decoding fails, try base64 encoding
				text_data = base64.b64encode(blob_data).decode('utf-8')
		
		# Search for the string in the decoded text
		if search_string in text_data:
			matching_rows.append(rowid)
	log(matching_rows)
	conn.close()
	return matching_rows


			
def checkMatch (search_string, authorName, title):
				for s in search_string.split():
					if s not in authorName.casefold() and s not in title.casefold():
						return False
				return True



def buildKindleNew(myDatabase):
	"""
    a function to build the kindle database for the new kindle app
		
   
    """
    
	# Connect to the SQLite database
	conn = sqlite3.connect(myDatabase)
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()

	# Select the rows with BLOB data
	query = f"SELECT rowid, ZSYNCMETADATAATTRIBUTES, ZDISPLAYTITLE, ZPATH FROM ZBOOK WHERE ZRAWBOOKTYPE IN (10, 13)"

	cursor.execute(query)


	books = []
	loanCount = 0
	for row in cursor.fetchall():
		
		rowid, blob_data, title, zpath = row
		
        # Skip if blob_data is None
		if blob_data is None:
			authorName = ''
		else: 	# Attempt to decode the blob data to text
			try:
				plist_data = biplist.readPlistFromString(blob_data)
				# Search for the string in the decoded text
				authorRow = plist_data['$objects'].index('author')
				authorName = plist_data['$objects'][authorRow+1]
				if all(item in plist_data['$objects'] for item in ['Purchase', 'PublicLibraryLending']):
					log (f"Both! title: {title}, total: {loanCount}")

				elif 'Purchase' in plist_data['$objects']:
						continue
				elif 'PublicLibraryLending' in plist_data['$objects']:
					loanCount += 1
					log (f"Loaned! title: {title}, total: {loanCount}")
				
				if isinstance(authorName, str):
					continue
					#log ('')
				else:
					myAuthorIDs = authorName['NS.objects']
					myAuthorIDs = [int(str(uid).strip('Uid()')) for uid in myAuthorIDs]
					# Fetch elements from list B and join them
					authorName = '; '.join([plist_data['$objects'][i] for i in myAuthorIDs])
					
			except (biplist.InvalidPlistException, biplist.NotBinaryPlistException):
				log("Failed to decode BLOB data as a plist.")
				authorName = ''
			 
		book = Book(
				title=title,
				path=zpath,
				author=authorName,
				book_desc="",
				read_pct="",
				
				)
		books.append(book)
		

            
	
	conn.close()
	# pickle the books object
	with open(f'{DATA_FOLDER}/kindle_books.pkl', 'wb') as file:
		pickle.dump(books, file)
	log ("building kindle database")
	log ("done 👍")
	return books



   

             
            

def buildLibraryDatabase (myFile):
    if myFile.startswith('both'):
        log ("building kindle database")
    
    elif myFile.startswith('kindle'):
        log ("building kindle database")
        if KINDLE_APP == 'new':
            buildKindleNew ()
        
        





def checkDatabases ():
## Checking if the database needs to be built or rebuilt
    timeToday = date.today()
    if not os.path.exists(CACHE_DATABASE_FILE):
        log ("Database missing ... building")
        refreshReadwiseDatabase()
        
    else: 
        databaseTime= (int(os.path.getmtime(CACHE_DATABASE_FILE)))
        dt_obj = datetime.fromtimestamp(databaseTime).date()
        time_elapsed = (timeToday-dt_obj).days
        log (str(time_elapsed)+" days from last update")
        if time_elapsed >= RefRate:
            log ("rebuilding database ⏳...")
            refreshReadwiseDatabase()
            log ("done 👍")
            