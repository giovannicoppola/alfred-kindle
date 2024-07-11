#!/usr/bin/env python3
#Sunny ☀️   🌡️+44°F (feels +39°F, 41%) 🌬️↘2mph 🌗 Tue Feb 14 06:18:23 2023
#W7Q1 – 45 ➡️ 319 – 279 ❇️ 85

import requests
import os
import sqlite3
import json
from config import  log, XML_CACHE,KINDLE_CONTENT, BOOK_CONTENT_SYMBOL,GHOST_RESULTS, CACHE_FOLDER_IMAGES,MY_URL_STRING, SEARCH_SCOPE
from time import time
import xmltodict
import urllib.request
import sys

MYINPUT = sys.argv[1].casefold()
   




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
	
    
    

def main():
	main_start_time = time()
	myContentBooks = getDownloadedBooks (KINDLE_CONTENT) # output is a list of downloaded book ASINs
	log (myContentBooks)
	getXML(XML_CACHE, myContentBooks)
	
	main_timeElapsed = time() - main_start_time
	log(f"\nscript duration: {round (main_timeElapsed,3)} seconds")
    
if __name__ == '__main__':
    main ()
