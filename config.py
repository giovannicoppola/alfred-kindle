#!/usr/bin/env python3

import os
import sys

# WF_BUNDLE = os.getenv('alfred_workflow_bundleid')
# WF_FOLDER = os.path.expanduser('~')+"/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/"+WF_BUNDLE+"/"
# INDEX_DB = WF_FOLDER+"index.db"
# TIMESTAMP = WF_FOLDER+'timestamp.txt'


# if not os.path.exists(WF_FOLDER):
#      os.makedirs(WF_FOLDER)


# Specify path
path1 = os.path.expanduser('~')+'/Library/Application Support/Kindle/My Kindle Content/'
path2 = os.path.expanduser('~')+'/Library/Containers/com.amazon.Kindle/Data/Library/Application Support/Kindle/My Kindle Content/'
 
# cd "/Users/giovanni/Library/Application Support/Kindle/My Kindle Content"
# cd "/Users/giovanni.coppola/Library/Containers/com.amazon.Kindle/Data/Library/Application Support/Kindle/My Kindle Content"
# checking the possible kindle folders
if (os.path.exists(path1)):
    kindle_path = path1
elif (os.path.exists(path2)):
    kindle_path = path2
else:
    print ("no kindle path")
    


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def logF(log_message, file_name):
    with open(file_name, "a") as f:
        f.write(log_message + "\n")


KINDLE_DB = kindle_path+'book_asset.db'
