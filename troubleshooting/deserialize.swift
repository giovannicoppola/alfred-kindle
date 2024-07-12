
import Foundation
import SQLite3

// Path to your SQLite database
let dbPath = "/Users/giovanni/Library/Containers/com.amazon.Lassen/Data/Library/Protected/BookData.sqlite"
var db: OpaquePointer?

// Open the database
if sqlite3_open(dbPath, &db) != SQLITE_OK {
    fatalError("Unable to open database")
}

// Query to fetch the blob data for a specific rowid
let rowid = 171  // Replace with your desired rowid
let query = "SELECT ZSYNCMETADATAATTRIBUTES FROM ZBOOK WHERE rowid = 171"
var statement: OpaquePointer?

if sqlite3_prepare_v2(db, query, -1, &statement, nil) != SQLITE_OK {
    fatalError("Unable to prepare statement")
}

// Execute the query and fetch the blob data
if sqlite3_step(statement) == SQLITE_ROW {
    if let blobPointer = sqlite3_column_blob(statement, 0) {
        let blobSize = sqlite3_column_bytes(statement, 0)
        let blobData = Data(bytes: blobPointer, count: Int(blobSize))

        do {
            let unarchiver = try NSKeyedUnarchiver(forReadingFrom: blobData)
            unarchiver.requiresSecureCoding = false
            let deserializedObject = unarchiver.decodeObject(forKey: NSKeyedArchiveRootObjectKey)
            if let object = deserializedObject {
                print("Successfully deserialized object: \(object)")
            } else {
                print("Deserialized object is nil")
            }
        } catch {
            print("Failed to deserialize: \(error)")
        }
    } else {
        print("Blob data pointer is nil or empty")
    }
} else {
    print("No row found for rowid \(rowid)")
}

sqlite3_finalize(statement)
sqlite3_close(db)
