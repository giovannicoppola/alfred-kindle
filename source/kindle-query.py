#!/usr/bin/env python3
#Sunny ☀️   🌡️+44°F (feels +39°F, 41%) 🌬️↘2mph 🌗 Tue Feb 14 06:18:23 2023
#W7Q1 – 45 ➡️ 319 – 279 ❇️ 85

import os
import json
from config import  log, KINDLE_APP, XML_CACHE,KINDLE_PATH, BOOK_CONTENT_SYMBOL,GHOST_RESULTS, SEARCH_SCOPE, IBOOKS_PATH, GHOST_SYMBOL, TIMESTAMP_KINDLE, TIMESTAMP_IBOOKS, KINDLE_PICKLE, IBOOKS_PICKLE, TARGET_LIBRARY
from time import time


import sys
import json
import pickle
from kindle_fun import get_kindle, get_ibooks, checkTimeStamp, getDownloadedASINs, get_kindleClassic


MYINPUT = sys.argv[1].casefold()

	

def search_books(books, search_string):
	if '--p' in search_string:
		search_string = search_string.replace('--p', '')
		books = [book for book in books if book.loaned != 1]
	
	if '--l' in search_string:
		search_string = search_string.replace('--l', '')
		books = [book for book in books if book.loaned == 1]
	
	if '--d' in search_string:
		search_string = search_string.replace('--d', '')
		books = [book for book in books if book.downloaded == 1]
	

	if '--k' in search_string:
		search_string = search_string.replace('--k', '')
		books = [book for book in books if book.source == 'Kindle']
	
	if '--ib' in search_string:
		search_string = search_string.replace('--ib', '')
		books = [book for book in books if book.source == 'iBooks']
	

	if GHOST_RESULTS == '0':
		books = [book for book in books if book.loaned == 0]

	search_fragments = search_string.split()
	if not search_fragments:
		search_fragments = [""]

	results = []
	if not search_string:
		return books	
	
	for book in books:
		if SEARCH_SCOPE == "Title":
			if any(fragment.lower() in book.title.lower() for fragment in search_fragments):
				results.append(book)
		elif SEARCH_SCOPE == "Author":
			if any(fragment.lower() in book.author.lower() for fragment in search_fragments):
				results.append(book)
		elif SEARCH_SCOPE == "Both":
			if all(fragment.lower() in book.title.lower() or fragment.lower() in book.author.lower() for fragment in search_fragments):
				results.append(book)

	return results

def serveBooks(books, result):
	myCounter = 0
	
	for myBook in books:
		loanedString = ""
		downloadedString = ""
	
		myCounter += 1
		if myBook.loaned == 1:
			loanedString = GHOST_SYMBOL
		if myBook.downloaded == 1:
			downloadedString = BOOK_CONTENT_SYMBOL

		# I currently can't figure out how to classify the books that were first loaned, then purchased. In case they were downloaded I can just remove the ghost symbol
		if loanedString == GHOST_SYMBOL and downloadedString == BOOK_CONTENT_SYMBOL:
			loanedString = ""
		booksN = len(books)
		if myBook.read_pct != "0%":
			readPct = myBook.read_pct
		else:
			readPct = ""
		
		
		
		result["items"].append({
			"title": f"{myBook.title} {loanedString} {downloadedString}",
			'subtitle': f"{myCounter}/{booksN:,} – {myBook.author} {readPct}",
			'valid': True,
			"icon": {
				"path": myBook.icon_path
				
			},
			"mods": {
				"cmd": {
					"valid": True,
					"subtitle": myBook.icon_path
			}},
			'arg': myBook.path
		})
	


	if not books:
		result["items"].append({
			"title": f"No results!",
			'subtitle': f"query again",
			'valid': True,
			"icon": {
				"path": f'icons/Warning.png'
			},
			'arg': "resultString"
		})
	
	return result




def main():
	main_start_time = time()
	
	myBooks = []
	if TARGET_LIBRARY in ["Kindle", "Both"]:
		if KINDLE_APP == "classic":

			myContentBooks = getDownloadedASINs(KINDLE_PATH) # output is a list of downloaded book ASINs
			#log(myContentBooks)
			get_kindleClassic(XML_CACHE, myContentBooks)
			with open(KINDLE_PICKLE, 'rb') as file:
				myBooks = myBooks + pickle.load(file)


		elif KINDLE_APP == "new":


			
			if not os.path.exists(KINDLE_PICKLE):
				log ("building new kindle database")
				get_kindle(KINDLE_PATH)
				
			elif checkTimeStamp(KINDLE_PATH,TIMESTAMP_KINDLE):
				log ("outdated, building new kindle database")
				get_kindle(KINDLE_PATH)
				
			else:
				log ("using existing Kindle database")
				# Load the list of books from the file
			
			with open(KINDLE_PICKLE, 'rb') as file:
				myBooks = myBooks + pickle.load(file)
			


	if TARGET_LIBRARY in ["iBooks", "Both"]:
		if not os.path.exists(IBOOKS_PICKLE):
				log ("building new iBooks database")
				get_ibooks(IBOOKS_PATH)
				
		elif checkTimeStamp(IBOOKS_PATH,TIMESTAMP_IBOOKS):
			log ("outdated, building new iBooks database")
			get_ibooks(IBOOKS_PATH)
			
		else:
			log ("using existing iBooks database")
			# Load the list of books from the file
		
		with open(IBOOKS_PICKLE, 'rb') as file:
			myBooks = myBooks + pickle.load(file)

			
	
	# Search the books
	myBooks = search_books(myBooks, MYINPUT)

	result = {"items": []}
	result = serveBooks(myBooks, result)
	print (json.dumps(result))


	main_timeElapsed = time() - main_start_time
	log(f"\nscript duration: {round (main_timeElapsed,3)} seconds")

if __name__ == '__main__':
	main ()



