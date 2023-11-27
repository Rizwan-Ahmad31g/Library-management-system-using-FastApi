import json
import time
from fastapi import HTTPException, Path
from app.api.database.config import books_collection, members_collections
from bson import ObjectId
from datetime import datetime, timezone


def check(id):
    object_id = ObjectId(id)
    books_edit = books_collection.find({"_id": object_id})
    if books_edit is not None:
        for books in books_edit:
            return books


def deactivate_user_acct(id, deactivate):
    string_id = str(id)
    object_id = ObjectId(string_id)
    deactivate_user = members_collections.update_one({"_id": object_id},
                                                     {"$set": {"active": deactivate}})
    if deactivate_user is not None:
        return deactivate_user
    raise HTTPException(status_code=400, detail="user not deactivated")


def patron_search_book(user):
    search_book = books_collection.find({"$or": [{"title": user}, {"author": user}, {"category": user}]})
    mul_search_book = []
    if search_book is not None:
        for search_book in search_book:
            search_book["_id"] = str(search_book["_id"])
            mul_search_book.append(search_book)

        return mul_search_book

    raise HTTPException(status_code=400, detail="No such book available against title , author or category")


def borrow_books(ID, title, due_time):
    # try:
    object_id = ObjectId(ID)
    title_book = title
    book = books_collection.find_one({"title": title}, {"quantity": 1})
    book_member = members_collections.find_one({"_id": object_id}, {"borrowed_book": 1, "due date": 1, "_id": 0})
    book_json = json.dumps(book_member)
    book_dict = json.loads(book_json)
    borrowed_book_value = book_dict.get("borrowed_book")
    if borrowed_book_value is None:
        borrowed_book_value = ["Test"]
    borrow_1 = len(borrowed_book_value)
    book = book["quantity"]
    book = int(book)
    borrow_book = []

    if book:
        if book <= 0:
            raise HTTPException(status_code=400, detail="Sorry! Books out of stock")
    count = 0
    if borrow_1 < 5:
        borrow_time = time.time()
        due_time_book = (due_time * 60)
        due_time = float(due_time_book)
        borrow = members_collections.update_one(
            {"_id": object_id},
            {"$push": {"borrowed_book": {"title": title, "due date": borrow_time + due_time}}}
        )
        books_title = members_collections.find_one({"_id": object_id}, {"borrowed_book": 1, "_id": 0})
        book_json = json.dumps(books_title)
        book_dict = json.loads(book_json)
        check_title = book_dict.get("borrowed_book")

        for title_books in check_title:
            if title_book in title_books.get("title"):
                count += 1

        if count > 1:
            borrow = members_collections.update_one(
                {"_id": object_id},
                {"$pull": {"borrowed_book": {"title": title, "due date": borrow_time + due_time}}}
            )
            books_collection.update_one(
                {"title": title},
                {
                    "$inc": {"number of book borrow": -1}
                }
            )
            borrow_book_quantity = books_collection.find_one({"title": title}, {"number of book borrow": 1, "_id": 0})
            book_json = json.dumps(borrow_book_quantity)
            book_dict = json.loads(book_json)
            number_of_book_borrow = book_dict.get("number of book borrow")
            number_of_borrow_status = number_of_book_borrow
            if number_of_book_borrow < 0:
                number_of_borrow = books_collection.update_one(
                    {"title": title}, {"$set": {"number of book borrow": 1}})

            raise HTTPException(status_code=400, detail="Cannot buy same book twice at a time")
        else:
            books_collection.update_one(
                {"title": title},
                {"$inc": {"quantity": -1}}
            )

            books_collection.update_one(
                {"title": title},
                {
                    "$inc": {"number of book borrow": 1}
                }
            )
            number_of_borrow = books_collection.find_one(
                {"title": title}, {"number of book borrow": 1, "_id": 0}
            )

    else:
        raise HTTPException(status_code=400,
                            detail="you cannot borrow 2 books with same name also your limit is only 4 books")

    if book:
        book_quantity = books_collection.find_one({"title": title}, {"quantity": 1, "_id": 0})
        book_json = json.dumps(book_quantity)
        book_dict = json.loads(book_json)
        borrowed_book_quantity = book_dict.get("quantity")
        if borrowed_book_quantity <= 5:
            books_collection.update_one(
                {"title": title},
                {"$set": {"availibility": "Limited Stock"}}
            )
        books_collection.update_one({"title": title}, {"$set": {"returned status": "Pending"}})

        return count

    else:
        raise HTTPException(status_code=400, detail="Book not found to add")


def borrow_history(user_id):
    object_id = ObjectId(user_id)
    borrow = members_collections.find_one({"_id": object_id}, {"borrowed_book": 1})
    borrow["_id"] = str(borrow["_id"])

    book_overdue_time = json.dumps(borrow)
    book_dict_overdue = json.loads(book_overdue_time)

    human_readable_book_list = []

    for book_dict in book_dict_overdue["borrowed_book"]:
        overdue_book_time = book_dict.get("due date")

        if isinstance(overdue_book_time, float):
            human_readable_time = datetime.utcfromtimestamp(overdue_book_time).replace(tzinfo=timezone.utc).strftime(
                '%Y-%m-%d %H:%M:%S GMT')

            updated_book_dict = {"title": book_dict["title"], "due date": human_readable_time}

            human_readable_book_list.append(updated_book_dict)

    return human_readable_book_list


def user_active(id):
    object_id = ObjectId(id)
    check = members_collections.find_one({"_id": object_id})
    check["_id"] = str(check["_id"])
    return check


def return_books(id, title):
    object_id = ObjectId(id)
    title_book = title
    increment = 0
    book_return = members_collections.update_one({"_id": object_id},
                                                 {"$pull": {"borrowed_book": title}})
    status = books_collection.find_one({"title": title}, {"quantity": 1})
    quantity_status = status["quantity"]
    book_member = members_collections.find_one({"_id": object_id}, {"borrowed_book": 1, "due date": 1, "_id": 0})
    book_json = json.dumps(book_member)
    book_dict = json.loads(book_json)
    borrowed_book_value = book_dict.get("borrowed_book")
    increment = 0

    for borrowed_book in borrowed_book_value:
        if title_book in borrowed_book["title"]:
            increment += 1
            books_collection.update_one({"title": title}, {"$set": {"quantity": quantity_status}})
            books_collection.update_one({"title": title}, {"$inc": {"quantity": increment}})

    members_collections.update_one(
        {"_id": object_id},
        {"$pull": {"borrowed_book": {"title": title}}}
    )

    over_due_count = books_collection.find_one({"title": title},
                                               {"overdue": 1, "number of book borrow": 1, "_id": 0})
    book_json = json.dumps(over_due_count)
    book_dict = json.loads(book_json)
    over_due = book_dict.get("overdue")
    number_of_book_borrow = book_dict.get("number of book borrow")

    if over_due is not None:
        if over_due < 0:
            books_collection.update_one({"title": title},
                                        {"$set": {"overdue": over_due - increment}})

    else:
        books_collection.update_one({"title": title},
                                    {"$set": {"number of book borrow": number_of_book_borrow - increment}})
        book_quantity = books_collection.find_one({"title": title}, {"quantity": 1, "_id": 0})
        book_json = json.dumps(book_quantity)
        book_dict = json.loads(book_json)
    borrowed_book_quantity = book_dict.get("quantity")
    if borrowed_book_quantity is not None:
        if borrowed_book_quantity >= 5:
            books_collection.update_one(
                {"title": title},
                {"$set": {"availibility": "In Stock"}}
            )

    books_collection.update_one({"title": title}, {"$set": {"returned status": "OK"}})

    return True


def user_search_book(user):
    search_book_user = books_collection.find(
        {"$or": [{"title": user}, {"author": user}, {"category": user}, {"ISBN": user}]})
    add_search_book = []
    if search_book_user is not None:
        for search_book in search_book_user:
            search_book["_id"] = str(search_book["_id"])
            add_search_book.append(search_book)

        return add_search_book

    raise HTTPException(status_code=400, detail="No such book available against title , author or category")


def report():
    reports = []
    finding = members_collections.find({}, {"borrowed_book": 1, "_id": 0})

    for title_document in finding:
        reports.append(title_document)

    return reports
