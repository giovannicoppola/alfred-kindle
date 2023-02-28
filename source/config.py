#!/usr/bin/env python3

import os
import sys
import json



CACHE_FOLDER = os.getenv('alfred_workflow_cache')
CACHE_FOLDER_IMAGES = CACHE_FOLDER+"/images/"
MY_URL_STRING = "https://ecx.images-amazon.com/images/P/"


if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)
if not os.path.exists(CACHE_FOLDER_IMAGES):
    os.makedirs(CACHE_FOLDER_IMAGES)


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)




# checking the possible kindle folders
pathA = os.path.expanduser('~')+'/Library/Application Support/Kindle/'
pathB = os.path.expanduser('~')+'/Library/Containers/com.amazon.Kindle/Data/Library/Application Support/Kindle/'

if (os.path.exists(pathA)):
    kindle_path = pathA
elif (os.path.exists(pathB)):
    kindle_path = pathB
else:
    kindle_path = ''




KINDLE_DB = kindle_path+'My Kindle Content/book_asset.db'
XML_CACHE = kindle_path+'/Cache/KindleSyncMetadataCache.xml'
KINDLE_CONTENT = kindle_path+'/My Kindle Content/'
BOOK_CONTENT_SYMBOL = os.path.expanduser(os.getenv('BookContent'))
GHOST_RESULTS = os.path.expanduser(os.getenv('SHOW_GHOST'))
SEARCH_SCOPE = os.path.expanduser(os.getenv('SEARCH_SCOPE'))



