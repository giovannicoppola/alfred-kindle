# CONFIG file for the kindle-ibooks workflow

import os
import sys




CACHE_FOLDER = os.getenv('alfred_workflow_cache')
CACHE_FOLDER_IMAGES = CACHE_FOLDER+"/images/"
MY_URL_STRING = "https://ecx.images-amazon.com/images/P/"
RefRate = int(os.getenv('RefreshRate'))

if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)
if not os.path.exists(CACHE_FOLDER_IMAGES):
    os.makedirs(CACHE_FOLDER_IMAGES)


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def defineKindleFolder ():
    """
    a function to find the kindle folder
    it will look for the newer kindle app, then the classic one, so if both are present it will use the new one

    """


    # checking the possible kindle folders
    pathA = os.path.expanduser('~')+'/Library/Containers/com.amazon.Lassen/Data/Library/'
    pathB = os.path.expanduser('~')+'/Library/Containers/com.amazon.Kindle/Data/Library/Application Support/Kindle/'
    pathC = os.path.expanduser('~')+'/Library/Application Support/Kindle/'
    

    if (os.path.exists(pathA)):
        kindle_path = pathA
        KINDLE_CONTENT = kindle_path+'Protected/BookData.sqlite'
        XML_CACHE = kindle_path+'/Cache/KindleSyncMetadataCache.xml'
        log ("using new Kindle app")
        KINDLE_APP = 'new'
        

    elif (os.path.exists(pathB)):
        kindle_path = pathB
        XML_CACHE = kindle_path+'/Cache/KindleSyncMetadataCache.xml'
        KINDLE_CONTENT = kindle_path+'/My Kindle Content/'
        log ("using Kindle Classic app")
        KINDLE_APP = 'classic'

    elif (os.path.exists(pathC)):
        kindle_path = pathC
        XML_CACHE = kindle_path+'/Cache/KindleSyncMetadataCache.xml'
        KINDLE_CONTENT = kindle_path+'/My Kindle Content/'
        log ("using Kindle Classic app")
        KINDLE_APP = 'classic'

    else:
        kindle_path = ''
    return XML_CACHE, KINDLE_CONTENT, KINDLE_APP



def define_iBooksFolder ():
    iBooks_path = os.path.expanduser('~/Library/Containers/com.apple.iBooksX/Data/Documents/BKLibrary/')
    dbs = []
    dbs += [each for each in os.listdir(iBooks_path)
            if (each.endswith('.sqlite') and each.startswith('BKLibrary'))]
    db_path = iBooks_path + dbs[0]
    return db_path



class Book:
    """
    Storing book information from Kindle and iBooks
    """

    books = 0

    def __init__(self, title, path, author, book_desc, 
                 read_pct):
        self.title = title
        self.path = path
        self.author = author
        self.book_desc = book_desc if book_desc \
            else "No book description for this title available in Books"
        self.read_pct = '0%' if not read_pct else str(read_pct * 100)[:4] + '%'
        Book.books += 1

    def display_book(self):
        return {
            'title:': self.title,
            'path:': self.path,
            'author:': self.author,
            'book_desc:': self.book_desc
            
        }

    def display_count(self):
        return 'Total books: ' + str(Book.books)



XML_CACHE, KINDLE_CONTENT, KINDLE_APP = defineKindleFolder()
BOOK_CONTENT_SYMBOL = os.path.expanduser(os.getenv('BookContent'))
GHOST_RESULTS = os.path.expanduser(os.getenv('SHOW_GHOST'))
SEARCH_SCOPE = os.path.expanduser(os.getenv('SEARCH_SCOPE'))
TARGET_LIBRARY = os.path.expanduser(os.getenv('TARGET_LIBRARY'))

if TARGET_LIBRARY == 'Both':
    CACHE_DATABASE_FILE = CACHE_FOLDER+'/both.pkl'
elif TARGET_LIBRARY == 'Kindle':
    CACHE_DATABASE_FILE = CACHE_FOLDER+'/kindle.pkl'
elif TARGET_LIBRARY == 'iBooks':
    CACHE_DATABASE_FILE = CACHE_FOLDER+'/ibooks.pkl'

if GHOST_RESULTS == '0':
    CACHE_DATABASE_FILE = CACHE_DATABASE_FILE.replace('.pkl', '_noghost.pkl')









IBOOKS_PATH = define_iBooksFolder()