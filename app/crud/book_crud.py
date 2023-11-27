from app.api.database.config import books_collection, members_collections
from bson import ObjectId


def add_book(books):
    # books = dict(books)
    books_added = books_collection.insert_one(books)
    return books_added


def edit_books(id, title, author, quantity):
    string_id = str(id)
    object_id = ObjectId(string_id)
    books_edit = books_collection.update_one({"_id": object_id},
                                             {"$set": {"title": title, "author": author, "quantity": quantity}})
    books = books_collection.find({"_id": id})
    return books


def delete_book(id):
    string_id = str(id)
    object_id = ObjectId(string_id)
    book_delete = books_collection.delete_one({"_id": object_id})
    return book_delete
