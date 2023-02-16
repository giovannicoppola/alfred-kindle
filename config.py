#!/usr/bin/env python3

import os
import sys


#WF_BUNDLE = os.getenv('alfred_workflow_bundleid')
#WF_FOLDER = os.getenv('alfred_preferences')+ "/workflows/"+os.getenv('alfred_workflow_uid')
# INDEX_DB = WF_FOLDER+"index.db"
# TIMESTAMP = WF_FOLDER+'timestamp.txt'
#WISHLIST_SYMBOL = os.path.expanduser(os.getenv('WISHLIST_SYMBOL'))
#GHOST_RESULTS = os.path.expanduser(os.getenv('GHOST_RESULTS'))
#CACHE_FOLDER = os.getenv('alfred_workflow_cache')
#CACHE_FOLDER_IMAGES = CACHE_FOLDER+"/images/"
#MY_DATABASE = CACHE_FOLDER+"/myKindle.db"
#MY_URL_STRING = "https://www.audible.com/pd/"
#MY_URL_ROOT = "https://www.audible.com/"


# if not os.path.exists(CACHE_FOLDER):
#     os.makedirs(CACHE_FOLDER)
# if not os.path.exists(CACHE_FOLDER_IMAGES):
#     os.makedirs(CACHE_FOLDER_IMAGES)





# Specify path
pathA = os.path.expanduser('~')+'/Library/Application Support/Kindle/'
pathB = os.path.expanduser('~')+'/Library/Containers/com.amazon.Kindle/Data/Library/Application Support/Kindle/'
 
# cd "/Users/giovanni/Library/Application Support/Kindle/My Kindle Content"
# cd "/Users/giovanni.coppola/Library/Containers/com.amazon.Kindle/Data/Library/Application Support/Kindle/My Kindle Content"

# checking the possible kindle folders
if (os.path.exists(pathA)):
    kindle_path = pathA
elif (os.path.exists(pathB)):
    kindle_path = pathB
else:
    print ("no kindle path")
    


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def logF(log_message, file_name):
    with open(file_name, "a") as f:
        f.write(log_message + "\n")


KINDLE_DB = kindle_path+'My Kindle Content/book_asset.db'
XML_CACHE = kindle_path+'/Cache/KindleSyncMetadataCache.xml'





