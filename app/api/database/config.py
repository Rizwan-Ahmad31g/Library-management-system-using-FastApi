import pymongo

Client = pymongo.MongoClient("mongodb://localhost:27017")

database = "librarymanagement"
db = Client[database]
books_collection = db.books
members_collections = db.members
user_authetication_collection = db.authentication