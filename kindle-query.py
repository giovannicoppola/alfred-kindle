#!/usr/bin/env python3
#New York – Sunny ☀️   🌡️+44°F (feels +39°F, 41%) 🌬️↘2mph 🌗 Tue Feb 14 06:18:23 2023
#W7Q1 – 45 ➡️ 319 – 279 ❇️ 85

import requests
import os
import sqlite3
import json
from config import KINDLE_DB, log, logF
from time import time



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


def main():
	main_start_time = time()
	datab = getKindleDB()
	GetKindleData(datab)
	main_timeElapsed = time() - main_start_time
	log(f"\nscript duration: {round (main_timeElapsed,3)} seconds")
    
if __name__ == '__main__':
    main ()
