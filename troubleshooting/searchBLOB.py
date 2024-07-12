import sqlite3
import binascii
import base64

def searchBLOB():
    # Connect to the SQLite database
    conn = sqlite3.connect('/Users/giovanni/Library/Containers/com.amazon.Lassen/Data/Library/Protected/BookData.sqlite')
    cursor = conn.cursor()

    # Define the string you are searching for
    search_string = 'Leonnig'

    # Convert search_string to bytes
    search_bytes = search_string.encode()

    # List of tables and blob columns to search
    tables_blob_columns = [
        ('ZBOOK','ZDISPLAYAUTHOR'),
        ('ZBOOK','ZSORTAUTHOR'),
        ('ZBOOK','ZSYNCMETADATAATTRIBUTES'),# ('table_name', 'blob_column_name'),
        ('ZBOOK','ZALTERNATESORTAUTHOR'),
        ('ZBOOK','ZEXTENDEDMETADATA'),
        ('ZBOOK','ZORIGINS'),
        ('ZBOOK','ZRAWTITLEDETAILSJSON')
        
        # Add other tables and columns as needed
    ]

    # Iterate over each table and blob column
    for table, blob_column in tables_blob_columns:
        mySQL = f"SELECT rowid, {blob_column} FROM {table}"
        cursor.execute(mySQL)
        print (mySQL)
        
        rows = cursor.fetchall()
        print (len(rows))
        
        for row in rows:
            rowid, blob_data = row
            
            if blob_data:
                # Check if the search string is in the blob data
                if search_bytes in blob_data:
                    print(f"Match found in table '{table}', column '{blob_column}', rowid {rowid}")

    # Close the connection
    conn.close()


  
def save_decoded_data(decoded_data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decoded_data)
    print(f"Decoded data saved as", output_file)

def extract_blob_data(db_path, table, blob_column, rowid):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {blob_column} FROM {table} WHERE rowid = ?", (rowid,))
    blob_data = cursor.fetchone()[0]
    conn.close()
    return blob_data

def try_decoding(blob_data):
    encodings_tried = []
    decoded_data = None
    
    encodings_to_try = [
        'base64', 'hexadecimal', 'latin-1', 'windows-1252', 'iso-8859-15',
        'macroman', 'iso-8859-2', 'iso-8859-3', 'iso-8859-4', 'iso-8859-5',
        'iso-8859-7', 'iso-8859-9', 'windows-1250', 'windows-1251', 'windows-1253',
        'windows-1254', 'windows-1255', 'windows-1256', 'koi8-r', 'big5', 'shift_jis',
        'iso-2022-jp', 'iso-2022-kr', 'iso-8859-6', 'iso-8859-8', 'gb2312',
        'euc-jp', 'euc-kr', 'cp437', 'cp850', 'cp852', 'cp866',
        'ibm775', 'ibm852', 'ibm855', 'ibm857', 'ibm860', 'ibm861',
        'ibm862', 'ibm863', 'ibm864', 'ibm865', 'ibm869'
    ]

    for encoding in encodings_to_try:
        try:
            if encoding == 'base64':
                decoded_data = base64.b64decode(blob_data).decode('utf-8')
            elif encoding == 'hexadecimal':
                decoded_data = binascii.unhexlify(blob_data).decode('utf-8')
            else:
                decoded_data = blob_data.decode(encoding)
                save_decoded_data(decoded_data, f'decoded_text_{encoding}.txt')
                encodings_tried.append(encoding)
            print(f"Successfully decoded using {encoding}")
            
        except Exception as e:
            print(f"{encoding} decoding failed: {e}")
    
    if not decoded_data:
        print("Failed to decode blob data with tried encodings.")
    else:
        print(f"Decoded data with encodings: {', '.join(encodings_tried)}")
    
    return decoded_data



import biplist
def useBiplist():
    # Connect to your SQLite database
    conn = sqlite3.connect('/Users/giovanni/Library/Containers/com.amazon.Lassen/Data/Library/Protected/BookData.sqlite')

    # Replace 'your_table' with your actual table name, 'your_blob_column' with your BLOB column name, and 'your_rowid' with the specific row ID
    rowid = 171  # Example rowid
    cursor = conn.cursor()
    cursor.execute(f"SELECT ZSYNCMETADATAATTRIBUTES FROM ZBOOK WHERE rowid = ?", (rowid,))
    result = cursor.fetchone()

    if result:
        blob_data = result[0]  # Assuming BLOB is the first column in the result tuple
        
        # Attempt to decode the BLOB data using biplist
        try:
            plist_data = biplist.readPlistFromString(blob_data)
            # Process the plist_data here (e.g., print, manipulate, etc.)
            #print(plist_data)
            print(plist_data['$objects'][23])
        except (biplist.InvalidPlistException, biplist.NotBinaryPlistException):
            print("Failed to decode BLOB data as a plist.")
        
    # Close the cursor and connection
    cursor.close()
    conn.close()




# Example usage
db_path = '/Users/giovanni/Library/Containers/com.amazon.Lassen/Data/Library/Protected/BookData.sqlite'
table = 'ZBOOK'
blob_column = 'ZSYNCMETADATAATTRIBUTES'
rowid = 171

# blob_data = extract_blob_data(db_path, table, blob_column, rowid)

# if blob_data:
#     decoded_data = try_decoding(blob_data)
# else:
#     print("No blob data found.")


useBiplist()


# ['$null', {'attributes': Uid(2), '$class': Uid(45)}, 
#  {'NS.keys': [Uid(3), Uid(4), Uid(5), Uid(6), Uid(7), Uid(8), Uid(9), Uid(10), Uid(11), Uid(12), Uid(13), Uid(14)], 'NS.objects': [Uid(15), Uid(16), Uid(20), Uid(21), Uid(24), Uid(25), Uid(32), Uid(33), Uid(34), Uid(35), Uid(43), Uid(44)], '$class': Uid(19)}, 
# 'ASIN', 'publishers', 'content_type', 'authors', 'cde_contenttype', 'origins', 'title', 'purchase_date', 'publication_date', 'bisac_subject_description_code', 'content_size', 'textbook_type', 'B002LDM8QS', {'NS.keys': [Uid(17)], 'NS.objects': [Uid(18)], '$class': Uid(19)}, 'publisher', 'Basic Books', {'$classname': 'NSMutableDictionary', '$classes': ['NSMutableDictionary', 'NSDictionary', 'NSObject']}, 'application/x-mobipocket-ebook', {'NS.keys': [Uid(22)], 'NS.objects': [Uid(23)], '$class': Uid(19)}, 'author', 'Farmelo, Graham', 'EBOK', {'NS.keys': [Uid(26)], 'NS.objects': [Uid(27)], '$class': Uid(19)}, 'origin', {'NS.keys': [Uid(28), Uid(29)], 'NS.objects': [Uid(30), Uid(31)], '$class': Uid(19)}, 'type', 'id', 'PublicLibraryLending', 'AV61VLSPKCOTL', 'The Strangest Man: The Hidden Life of Paul Dirac, Mystic of the Atom', '2023-12-07T10:02:21+0000', '2009-08-25T00:00:00+0000', {'NS.keys': [Uid(36)], 'NS.objects': [Uid(37)], '$class': Uid(19)}, 'code', {'NS.objects': [Uid(38), Uid(39), Uid(40), Uid(41)], '$class': Uid(42)}, 'BIO015000', 'SCI034000', 'SCI080000', 'SCI057000', {'$classname': 'NSMutableArray', '$classes': ['NSMutableArray', 'NSArray', 'NSObject']}, '2916352', 'unknown', {'$classname': 'SyncMetadataAttributes', '$classes': ['SyncMetadataAttributes', 'NSObject']}]
