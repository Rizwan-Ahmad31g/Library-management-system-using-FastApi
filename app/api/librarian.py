from fastapi import APIRouter, Depends, HTTPException, Path, Query,status
from typing import Annotated
from app.models.books_model import BookInformation
from app.models.user import NewUser
from app.models.user_authentication_model import Token
from app.api.database.config import books_collection, members_collections,user_authetication_collection
from app.crud.book_crud import add_book, edit_books, delete_book
from app.crud.user_crud import add_user, edit_user
from app.dependencies.depends import check, deactivate_user_acct, report
from app.api.user_credentials import get_current_user,check_user_permission
from bson import ObjectId
import time
import json

ACCESS_TOKEN_EXPIRE_MINUTES = 30
router = APIRouter(
    tags=["librarian privileges"],

)
router_member = APIRouter(
    tags=["Librarian User Management"]
)
router_report = APIRouter(
    tags=["Report"]
)



@router.post("/books/" , dependencies=[Depends(check_user_permission)])
def create_book(books: BookInformation):
    books = dict(books)
    book_added = add_book(books)

    if book_added is not None:
        return "book added successfully"
    HTTPException(status_code=400, detail="book not added")


@router.put("/books/", dependencies=[Depends(check_user_permission)])
def edit_book(
        *,
        id: Annotated[str, Query(description="enter the id of book you want to update")],
        title: Annotated[str, Query(description="Title of the book")] = None,
        author: Annotated[str | None, Query(description="Enter name of author", alias="author of the book")] = None,
        quantity: Annotated[int | None, Query(description="Enter quantity of books you want to update",
                                              alias="quantity of the book")] = None):
    edit = edit_books(id, title, author, quantity)

    if edit is not None:
        return "book updated successfully"

    HTTPException(status_code=400, detail="not updated")


@router.delete("/books/", dependencies=[Depends(check_user_permission)])
def delete_books(book_id: str = Query(title="Enter the ID of the book you want to delete")):
    try:
        object_id = ObjectId(book_id)
        user_db = check(book_id)

        if object_id == user_db["_id"]:
            delete_book(book_id)
            return "Book deleted successfully"
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except TypeError:
        raise HTTPException(status_code=400, detail="Invalid ObjectID format. Please provide a valid ObjectID.")


@router_member.post("/user_management/", dependencies=[Depends(check_user_permission)])
def create_user(user: NewUser):
    create_user_acct = dict(user)
    user_added = add_user(create_user_acct)
    return "user added successfully"


@router_member.put("/user_management/", dependencies=[Depends(check_user_permission)])
def update_user(id: Annotated[str, Query(description="enter contact information to modify")],
                contact_information: Annotated[str, Query(description="enter contact information to modify")]):
    update_user_acct = edit_user(id, contact_information)
    return "user updated successfully"


@router_member.patch("/user_management/", dependencies=[Depends(check_user_permission)])
def deactivate_user(
        *,
        id: Annotated[str, Query(title="enter the account id of user you want to activate or deactivate it")] = None,
        deactivate: Annotated[bool, Query(title="Title of the book")] = None):
    deactivate = deactivate_user_acct(id, deactivate)
    return "user deactivated or activated successfully"


@router_report.get("/report/", dependencies=[Depends(check_user_permission)])
def generate_report():
    for_time = members_collections.find()
    library_book = []
    title_1 = books_collection.find({}, {"title": 1, "_id": 0})

    for library_books in title_1:
        library_book.append(library_books)

    borrowed_books = []
    new_borrowed_book = []

    for for_time_1 in for_time:
        for_time_1["_id"] = str(for_time_1["_id"])
        book_json = json.dumps(for_time_1)
        book_dict = json.loads(book_json)
        borrowed_books.append(book_dict.get("borrowed_book"))

    max_count_dict = {}

    for book in borrowed_books:
        if book is not None:
            new_borrowed_book.append(book)

    count_dict = {}

    for newbook in new_borrowed_book:
        for books in newbook:
            for title_of_book in library_book:
                if title_of_book["title"] == books["title"]:
                    count_dict[title_of_book["title"]] = count_dict.get(title_of_book["title"], 0) + 1
    if count_dict:
        max_value = max(count_dict, key=count_dict.get)
    else:
        max_value = "No book is borrowed by the library Patrons"

    """ overdue book code handler"""
    borrowed_time = members_collections.find()
    overdue_book_check = []
    new_over_due_book_check = []

    for times in borrowed_time:
        times["_id"] = str(times["_id"])
        book_json = json.dumps(times)
        book_dict = json.loads(book_json)
        overdue_book_check.append(book_dict.get("borrowed_book"))

    for book in overdue_book_check:
        if book is not None:
            new_over_due_book_check.append(book)

    over_due_count = {}

    for times in new_over_due_book_check:
        for due_date in times:
            current_time = time.time()
            if current_time > due_date["due date"]:
                over_due_count[due_date["title"]] = over_due_count.get(due_date["title"], 0) + 1

    for title, count in over_due_count.items():
        books_collection.update_one({"title": title}, {"$set": {"overdue": count}})

    if max_value is None:
        return "No book is borrowed by the user"
    available_books = []
    staus_over_book = []
    status_overdue_books = []
    availibility = books_collection.find({}, {"title": 1, "availibility": 1, "_id": 0})
    status_overdue = books_collection.find({}, {"title": 1, "overdue": 1, "_id": 0})

    for availibility in availibility:
        available_books.append(availibility)

    for status in status_overdue:
        staus_over_book.append(status)

    return {"popular book": max_value, "available books":available_books, "over due" : staus_over_book}
