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
            original_word TEXT,
            position INTEGER,
            lower_word TEXT,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def extract_text_from_epub(epub_path):
    book = epub.read_epub(epub_path)
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
    words = re.findall(r'\w+', text)

    c.execute('INSERT INTO books (title, path) VALUES (?, ?)', (title, epub_path))
    book_id = c.lastrowid
    
    for i, word in enumerate(words):
        lower_word = word.lower()
        c.execute('INSERT INTO tokens (book_id, original_word, position, lower_word) VALUES (?, ?, ?, ?)', (book_id, word, i, lower_word))

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

def get_surrounding_text_from_db(c, book_id, start_idx, end_idx, num_words=50):
    start = max(0, start_idx - num_words)
    end = end_idx + num_words

    c.execute('''
        SELECT original_word FROM tokens
        WHERE book_id = ? AND position >= ? AND position <= ?
        ORDER BY position
    ''', (book_id, start, end))
    
    surrounding_words = [row[0] for row in c.fetchall()]
    return ' '.join(surrounding_words)

def search_words_in_multiple_books(db_path, word1, word2, max_distance):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    word1_lower = word1.lower()
    word2_lower = word2.lower()
    
    c.execute('SELECT book_id, position FROM tokens WHERE lower_word = ?', (word1_lower,))
    word1_positions = c.fetchall()
    
    matches = []

    for book_id, pos in word1_positions:
        c.execute('''
            SELECT original_word, position FROM tokens
            WHERE book_id = ? AND position > ? AND position <= ?
        ''', (book_id, pos, pos + max_distance))
        words = c.fetchall()
        
        for word, position in words:
            if word.lower() == word2_lower:
                surrounding_text = get_surrounding_text_from_db(c, book_id, pos, position)
                c.execute('SELECT title FROM books WHERE id = ?', (book_id,))
                book_title = c.fetchone()[0]
                
                match_info = {
                    "book_title": book_title,
                    "word1_position": pos,
                    "word2_position": position,
                    "surrounding_text": surrounding_text
                }
                matches.append(match_info)
    
    conn.close()
    
    if matches:
        for match in matches:
            print(f"'{word1}' and '{word2}' found within {max_distance} words apart in '{match['book_title']}'.")
            print("Surrounding text:", match["surrounding_text"])
    else:
        print(f"'{word1}' and '{word2}' not found within {max_distance} words apart.")
    
    return matches

# Example usage
db_path = 'books_tokensCap.db'
create_db_schema(db_path)

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
word1 = 'members'
word2 = 'notai'
max_distance = 100
matches = search_words_in_multiple_books(db_path, word1, word2, max_distance)
