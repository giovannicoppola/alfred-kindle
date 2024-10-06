# Script to Search for Two Words within a Maximum Distance

 
pip install ebooklib beautifulsoup4
from ebooklib import epub
from bs4 import BeautifulSoup
import re

def extract_text_from_epub(epub_path):
    book = epub.read_epub(epub_path)
    text = ""

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text()

    return text

def search_words_within_distance(epub_path, word1, word2, max_distance):
    text = extract_text_from_epub(epub_path)
    words = re.findall(r'\w+', text.lower())  # Tokenize the text into words

    for i in range(len(words)):
        if words[i] == word1.lower():
            for j in range(i + 1, min(i + 1 + max_distance, len(words))):
                if words[j] == word2.lower():
                    print(f"'{word1}' and '{word2}' found within {max_distance} words apart.")
                    return

    print(f"'{word1}' and '{word2}' not found within {max_distance} words apart.")

# Example usage
epub_path = 'path_to_your_epub_file.epub'
word1 = 'first_word'
word2 = 'second_word'
max_distance = 5  # Maximum distance in words
search_words_within_distance(epub_path, word1, word2, max_distance)





# Script to Tokenize and Save Text in SQLite Database


import sqlite3
from ebooklib import epub
from bs4 import BeautifulSoup
import re

def extract_text_from_epub(epub_path):
    book = epub.read_epub(epub_path)
    text = ""

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text()

    return text

def tokenize_and_save_to_db(epub_path, db_path):
    text = extract_text_from_epub(epub_path)
    words = re.findall(r'\w+', text.lower())  # Tokenize the text into words

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY,
            word TEXT,
            position INTEGER,
            book_path TEXT
        )
    ''')

    for position, word in enumerate(words):
        cursor.execute('''
            INSERT INTO tokens (word, position, book_path)
            VALUES (?, ?, ?)
        ''', (word, position, epub_path))

    conn.commit()
    conn.close()

def search_words_within_distance(db_path, word1, word2, max_distance):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT t1.book_path, t1.position, t2.position
        FROM tokens t1
        JOIN tokens t2 ON t1.book_path = t2.book_path
        WHERE t1.word = ? AND t2.word = ? AND t2.position > t1.position AND t2.position <= t1.position + ?
    ''', (word1.lower(), word2.lower(), max_distance))

    results = cursor.fetchall()
    conn.close()

    if results:
        for result in results:
            print(f"'{word1}' and '{word2}' found within {max_distance} words apart in book: {result[0]}")
    else:
        print(f"'{word1}' and '{word2}' not found within {max_distance} words apart.")

# Example usage
epub_paths = ['path_to_your_first_epub_file.epub', 'path_to_your_second_epub_file.epub']
db_path = 'tokens.db'

# Tokenize and save each book to the database
for epub_path in epub_paths:
    tokenize_and_save_to_db(epub_path, db_path)

# Search for words within a specified distance
word1 = 'first_word'
word2 = 'second_word'
max_distance = 5  # Maximum distance in words
search_words_within_distance(db_path, word1, word2, max_distance)