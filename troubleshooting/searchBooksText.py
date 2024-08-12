import sqlite3
import re
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup

def create_db_schema(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT UNIQUE,
            path TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            book_id INTEGER,
            word TEXT,
            position INTEGER,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def extract_text_from_epub(epub_path):
    book = epub.read_epub(epub_path, {"ignore_ncx": True})
    text = ""
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text()
    return text

def is_book_in_database(c, title):
    c.execute('SELECT id FROM books WHERE title = ?', (title,))
    return c.fetchone()

def tokenize_and_save_book(c, epub_path):
    title = epub_path.split('/')[-1]
    text = extract_text_from_epub(epub_path)
    words = re.findall(r'\w+', text.lower())

    c.execute('INSERT INTO books (title, path) VALUES (?, ?)', (title, epub_path))
    book_id = c.lastrowid
    
    for i, word in enumerate(words):
        c.execute('INSERT INTO tokens (book_id, word, position) VALUES (?, ?, ?)', (book_id, word, i))

def process_books(epub_paths, db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    for epub_path in epub_paths:
        title = epub_path.split('/')[-1]
        book_id = is_book_in_database(c, title)
        
        if not book_id:
            print(f"Tokenizing and saving book: {title}")
            tokenize_and_save_book(c, epub_path)
        else:
            print(f"Book '{title}' is already in the database.")
    
    conn.commit()
    conn.close()

def search_words_in_multiple_books(db_path, word1, word2, max_distance):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('SELECT book_id, position FROM tokens WHERE word = ?', (word1.lower(),))
    word1_positions = c.fetchall()
    
    for book_id, pos in word1_positions:
        c.execute('''
            SELECT word, position FROM tokens
            WHERE book_id = ? AND position > ? AND position <= ?
        ''', (book_id, pos, pos + max_distance))
        words = c.fetchall()
        
        for word, position in words:
            if word == word2.lower():
                surrounding_text = get_surrounding_text_from_db(c, book_id, pos, position)
                c.execute('SELECT title FROM books WHERE id = ?', (book_id,))
                book_title = c.fetchone()[0]
                
                print(f"'{word1}' and '{word2}' found within {max_distance} words apart in '{book_title}'.")
                print("Surrounding text:", surrounding_text)
                conn.close()
                return surrounding_text
    
    print(f"'{word1}' and '{word2}' not found within {max_distance} words apart.")
    conn.close()
    return None

def get_surrounding_text_from_db(c, book_id, start_idx, end_idx, num_words=50):
    start = max(0, start_idx - num_words)
    end = end_idx + num_words

    c.execute('''
        SELECT word FROM tokens
        WHERE book_id = ? AND position >= ? AND position <= ?
        ORDER BY position
    ''', (book_id, start, end))
    
    surrounding_words = [row[0] for row in c.fetchall()]
    return ' '.join(surrounding_words)


# Example usage
db_path = 'books_tokens.db'
create_db_schema(db_path)

# Example usage
epub_paths = [
    '/Users/giovanni/Library/CloudStorage/GoogleDrive-giovannicoppola@gmail.com/My Drive/eBooks/Leonardo da Vinci -- Isaacson, Walter -- 2017 -- Simon & Schuster -- 74ac60641c980b7ba66da3194ebb1b33 -- Anna’s Archive.epub',
    '/Users/giovanni/Library/CloudStorage/GoogleDrive-giovannicoppola@gmail.com/My Drive/eBooks/The Conquest of Happiness -- Russell, Bertrand -- 1, 2013 -- W_ W_ Norton & Company -- 1631491482 -- 0b7c3f92fa1d695eafe8c1fa99ed156d -- Anna’s Archive.epub',
    '/Users/giovanni/Library/CloudStorage/GoogleDrive-giovannicoppola@gmail.com/My Drive/eBooks/Macbeth -- SparkNotes -- No Fear Shakespeare, 2018 -- Spark -- 1411400437 -- c5767439cb1b853883c3455196b73ec1 -- Anna’s Archive.epub',
    '/Users/giovanni/Library/CloudStorage/GoogleDrive-giovannicoppola@gmail.com/My Drive/eBooks/La smorfia napoletana per giocare e vincere -- 2007 -- Brancato -- fe1cc24a918c417e9c89d26cf3f4aac2 -- Anna’s Archive.epub',
    '/Users/giovanni/Library/CloudStorage/GoogleDrive-giovannicoppola@gmail.com/My Drive/eBooks/The Civil War_ A Narrative_ Volume 3_ Red River to -- Foote, Shelby -- The Civil War_ A Narrative Three, 1986 -- Vintage Books -- 9780307744692 -- d7c5939af735f7d475802044ca059e6c -- Anna’s Archive.epub',
    '/Users/giovanni/Library/CloudStorage/GoogleDrive-giovannicoppola@gmail.com/My Drive/eBooks/The Civil War_ A Narrative_ Volume 2_ Fredericksburg to -- Foote, Shelby -- The Civil War_ A Narrative Two, 2011 -- Random House -- 9780307744685 -- c95f27ab2c85e3e91ad6738b6f899ead -- Anna’s Archive.epub',
    # Add more paths as needed
]

process_books(epub_paths, db_path)

# Now you can search across the books
word1 = 'lee'
word2 = 'grant'
max_distance = 100
search_words_in_multiple_books(db_path, word1, word2, max_distance)


"""
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
import re

def extract_text_from_epub(epub_path):
    book = epub.read_epub(epub_path, {"ignore_ncx": True})
    text = ""
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text()
    return text

def get_surrounding_text(words, start_idx, end_idx, num_words=50):
    #Extract surrounding text, with `num_words` before and after the search words.
    
    start = max(0, start_idx - num_words)
    end = min(len(words), end_idx + num_words + 1)
    return ' '.join(words[start:end])

def search_words_within_distance(epub_path, word1, word2, max_distance):
    text = extract_text_from_epub(epub_path)
    words = re.findall(r'\w+', text.lower())
    for i in range(len(words)):
        if words[i] == word1.lower():
            for j in range(i + 1, min(i + 1 + max_distance, len(words))):
                if words[j] == word2.lower():
                    surrounding_text = get_surrounding_text(words, i, j)
                    print(f"'{word1}' and '{word2}' found within {max_distance} words apart in {epub_path}.")
                    #print("Surrounding text:", surrounding_text)
                    return surrounding_text
    #print(f"'{word1}' and '{word2}' not found within {max_distance} words apart in {epub_path}.")
    return None

def search_across_multiple_books(epub_paths, word1, word2, max_distance):
    for epub_path in epub_paths:
        result = search_words_within_distance(epub_path, word1, word2, max_distance)
        if result:
            print(f"Result from {epub_path}:\n{result}\n")

# Example usage
epub_paths = [
    '/Users/giovanni/Library/CloudStorage/GoogleDrive-giovannicoppola@gmail.com/My Drive/eBooks/Leonardo da Vinci -- Isaacson, Walter -- 2017 -- Simon & Schuster -- 74ac60641c980b7ba66da3194ebb1b33 -- Anna’s Archive.epub',
    '/Users/giovanni/Library/CloudStorage/GoogleDrive-giovannicoppola@gmail.com/My Drive/eBooks/The Conquest of Happiness -- Russell, Bertrand -- 1, 2013 -- W_ W_ Norton & Company -- 1631491482 -- 0b7c3f92fa1d695eafe8c1fa99ed156d -- Anna’s Archive.epub',
    '/Users/giovanni/Library/CloudStorage/GoogleDrive-giovannicoppola@gmail.com/My Drive/eBooks/Macbeth -- SparkNotes -- No Fear Shakespeare, 2018 -- Spark -- 1411400437 -- c5767439cb1b853883c3455196b73ec1 -- Anna’s Archive.epub',
    # Add more paths as needed
]
word1 = 'lee'
word2 = 'grant'
max_distance = 100

search_across_multiple_books(epub_paths, word1, word2, max_distance)
"""