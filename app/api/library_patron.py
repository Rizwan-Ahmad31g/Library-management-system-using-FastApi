from fastapi import APIRouter, Depends, HTTPException, Query, Path
from app.dependencies.depends import patron_search_book, borrow_books, borrow_history, user_active, return_books
from app.models.books_model import BookInformation
from app.models.user import Activity
from typing import Annotated
from app.api.user_credentials import check_user_permission,get_current_user

router = APIRouter(
    tags=["library patron(student,teacher,reseachers)"]
)


@router.get("/library_patron/" , dependencies=[Depends(get_current_user)])
def search_book(book_search: Annotated[
    str, Query(description="enter book title , author or category", alias="book search")] = None):
    search = patron_search_book(book_search)
    if not search:
        raise HTTPException(status_code=400, detail="No book title , author or category")
    else:
        return search


@router.put("/library_patron/", dependencies=[Depends(check_user_permission)])
def request_borrow_book(
        id: Annotated[str, Query(description="Enter ID")],
        title: Annotated[str, Query(description="which book you may want to borrow")],
        day: Annotated[int, Query(description="which book you may want to borrow")]):
    active = user_active(id)
    if active["active"]:
        borrow = borrow_books(id, title,day)
        return f"{title} is borrowed Have a Good time"
    raise HTTPException(status_code=400, detail="you are not allowed to borrow book")


@router.get("/library_patron/{user_id}", dependencies=[Depends(check_user_permission)])
def borrowing_history(user_id: Annotated[str, Path(description="enter ID to check borrowing history")]):
    history = borrow_history(user_id)
    return history


@router.patch("/library_patron/", dependencies=[Depends(check_user_permission)])
def return_book(id: Annotated[str, Query(description="enter ID")],
                title: Annotated[str, Query(description="enter title of the book you want to return")]):
    title = title
    book_return = return_books(id, title)
    return f"{title} is returned successfully"