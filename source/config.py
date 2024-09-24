# CONFIG file for the alfred-eBooks workflow

import os
import sys
import shutil



CACHE_FOLDER = os.getenv('alfred_workflow_cache')
DATA_FOLDER = os.getenv('alfred_workflow_data')
CACHE_FOLDER_IMAGES_KINDLE = CACHE_FOLDER+"/images/kindle/"
CACHE_FOLDER_IMAGES_IBOOKS = CACHE_FOLDER+"/images/ibooks/"
TIMESTAMP_KINDLE = CACHE_FOLDER+"/timestamp_kindle.txt"
TIMESTAMP_IBOOKS = CACHE_FOLDER+"/timestamp_ibooks.txt"



MY_URL_STRING = "https://ecx.images-amazon.com/images/P/"





def move_images_to_newFolder(parent_folder, newFolder):
    """
    Compatibility with previous version and file structure 
    moving existing cover images from the previous version of the workflow to the new folder structure
    Note: this function can be removed in future versions
    
    """    
    
    # Get a list of all files in the parent folder
    for file_name in os.listdir(parent_folder):
        # Construct the full file path
        file_path = os.path.join(parent_folder, file_name)

        # Check if the file is an image (you can add more extensions if needed)
        if os.path.isfile(file_path):
            # Move the file to the subfolder
            shutil.move(file_path, newFolder)
            



if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)
if not os.path.exists(CACHE_FOLDER_IMAGES_KINDLE):
    os.makedirs(CACHE_FOLDER_IMAGES_KINDLE)
    move_images_to_newFolder(CACHE_FOLDER+"/images/", CACHE_FOLDER_IMAGES_KINDLE)
if not os.path.exists(CACHE_FOLDER_IMAGES_IBOOKS):
    os.makedirs(CACHE_FOLDER_IMAGES_IBOOKS)

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

KINDLE_PICKLE = f"{DATA_FOLDER}/kindle_books.pkl"
IBOOKS_PICKLE = f"{DATA_FOLDER}/ibooks_books.pkl"

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
        KINDLE_APP_PATH = "/Applications/Amazon Kindle.app"
        

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

    def __init__(self, title, bookID, path, icon_path, author, book_desc, 
                 read_pct, source, loaned,downloaded):
        self.title = title
        self.bookID = bookID
        self.path = path
        self.icon_path = icon_path
        self.author = author
        self.book_desc = book_desc if book_desc \
            else "No book description for this title available in Books"
        self.read_pct = '0%' if not read_pct else f"{(read_pct * 100):.1f}%"
        self.source = source
        self.loaned = loaned
        self.downloaded = downloaded
        Book.books += 1

    def display_book(self):
        return {
            'title:': self.title,
            'bookID:': self.bookID,
            'path:': self.path,
            'icon_path:': self.icon_path,
            'author:': self.author,
            'read_pct:': self.read_pct,
            'book_desc:': self.book_desc,
            'source:': self.source,
            'loaned:': self.loaned,
            'downloaded:': self.downloaded
            
            
        }

    def display_count(self):
        return 'Total books: ' + str(Book.books)




BOOK_CONTENT_SYMBOL = os.path.expanduser(os.getenv('BookContent'))
GHOST_SYMBOL = os.path.expanduser(os.getenv('GhostContent'))
GHOST_RESULTS = os.path.expanduser(os.getenv('SHOW_GHOST'))
SEARCH_SCOPE = os.path.expanduser(os.getenv('SEARCH_SCOPE'))
TARGET_LIBRARY = os.path.expanduser(os.getenv('TARGET_LIBRARY'))


if TARGET_LIBRARY in ["Kindle", "Both"]:
    XML_CACHE, KINDLE_PATH, KINDLE_APP = defineKindleFolder()
else:
    XML_CACHE, KINDLE_PATH, KINDLE_APP = '', '', ''



IBOOKS_PATH = define_iBooksFolder()