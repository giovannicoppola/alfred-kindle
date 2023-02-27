#!/usr/bin/env python3
#Sunny ☀️   🌡️+44°F (feels +39°F, 41%) 🌬️↘2mph 🌗 Tue Feb 14 06:18:23 2023
#W7Q1 – 45 ➡️ 319 – 279 ❇️ 85

import requests
import os
import sqlite3
import json
from config import KINDLE_DB, log, XML_CACHE,KINDLE_CONTENT, BOOK_CONTENT_SYMBOL,GHOST_RESULTS, CACHE_FOLDER_IMAGES,MY_URL_STRING, SEARCH_SCOPE
from time import time
import xmltodict
import urllib.request
import sys

MYINPUT = sys.argv[1].casefold()

    

def getKindleDB():
	db = sqlite3.connect(KINDLE_DB)
	cursor = db.cursor()

		
		
	queryString = f"""SELECT *
		FROM Book """
		
	
	try:
		cursor.execute(queryString)
		
		
		result = [row[1] for row in cursor.fetchall()]
		


	except sqlite3.OperationalError as err:
		result= {"items": [{
		"title": "Error: " + str(err),
		"subtitle": "Some error",
		"arg": "",
		"icon": {

				"path": "icons/Warning.png"
			}
		}]}
		print (json.dumps(result))
		raise err

	
		

	resultList = []
	for i in range(0, len(result), 10):
		resultList.append(','.join(str(x) for x in result[i:i+10]))

	return resultList
	#print(resultList)


def GetKindleData(myList):
	url = "https://amazon-product-price-data.p.rapidapi.com/product"

	myResults = []
	#querystring = {"asins":"B00JGAS65Q, B003EY7IQI, B004DEPH3E","locale":"US"}
	for myBatch in myList: 
		querystring = {"asins":myBatch,"locale":"US"}

		headers = {
			"X-RapidAPI-Key": "060192ca34msh77aa6624f8e5d93p186236jsn93b44b5109c8",
			"X-RapidAPI-Host": "amazon-product-price-data.p.rapidapi.com"
		}

		response = requests.request("GET", url, headers=headers, params=querystring)
		myResults.append(response.json())
	
	with open('kindle.json', 'w') as f:
		json.dump(myResults, f,indent=4)
	
	return (myResults)

def getDownloadedBooks(basepath):
	import os
	myContentBooks = []
	# List all subdirectories using scandir()
	with os.scandir(basepath) as entries:
		for entry in entries:
			if entry.is_dir():
				myContentBooks.append(entry.name.split("_")[0])
	return myContentBooks

def getXML(myFile, downloaded):
## Importing the XML table
    
	with open(myFile) as xml_file:
		data_dict = xmltodict.parse(xml_file.read())
		xml_file.close()
	
	#print (data_dict)
	
	# with open('xml.json', 'w') as f:
	# 	json.dump(data_dict, f,indent=4)
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
		
	
	if MYINPUT and not myFilteredBooks:
		result["items"].append({
			"title": "No matches in your library",
			"subtitle": "Try a different query",
			"arg": "",
			"icon": {
				"path": "icons/Warning.png"
				}
			
				})
		#print (json.dumps(result))





	for book in myFilteredBooks:
		#print (book['title']['#text'])
		
		if book['ASIN'] in downloaded:
			BookSymbol = BOOK_CONTENT_SYMBOL
			bookURL = f"{KINDLE_CONTENT}{book['ASIN']}_EBOK/{book['ASIN']}_EBOK.azw"
			ICON_PATH = f"{CACHE_FOLDER_IMAGES}{book['ASIN']}.01"
			if not os.path.exists(ICON_PATH):
				log ("retrieving image" + ICON_PATH)
				urllib.request.urlretrieve(f"{MY_URL_STRING}{book['ASIN']}.01", ICON_PATH)
		
			
		elif GHOST_RESULTS == '1':
			BookSymbol = ""
			bookURL = f"https://www.amazon.com/dp/{book['ASIN']}"
			ICON_PATH = f"{CACHE_FOLDER_IMAGES}{book['ASIN']}.01"
			if not os.path.exists(ICON_PATH):
				log ("retrieving image" + ICON_PATH)
				urllib.request.urlretrieve(f"{MY_URL_STRING}{book['ASIN']}.01", ICON_PATH)
		
		else:
			continue
		
		
		
		result["items"].append({
			"title": book['title']['#text']+BookSymbol,
			'subtitle': book['authorString'],
			'valid': True,
			
			"icon": {
				"path": ICON_PATH	
			},
			'arg': bookURL
				}) 
	log (len(data_dict['response']['add_update_list']['meta_data']))
	log (len(myFilteredBooks))
	
	print (json.dumps(result))
	
    
    

def main():
	main_start_time = time()
	myContentBooks = getDownloadedBooks (KINDLE_CONTENT)
	getXML(XML_CACHE, myContentBooks)
	
	main_timeElapsed = time() - main_start_time
	log(f"\nscript duration: {round (main_timeElapsed,3)} seconds")
    
if __name__ == '__main__':
    main ()
