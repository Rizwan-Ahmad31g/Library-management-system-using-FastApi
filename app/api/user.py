from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.books_model import LocationStatus
from app.dependencies.depends import user_search_book, user_active
# from app.dependencies.authetication import get_user
from typing import Annotated
from app.api.database.config import books_collection, members_collections, user_authetication_collection
import json
from bson import ObjectId
import time

router = APIRouter(
    tags=["User"]
)


@router.post("/member/")
def search_book(
        id: Annotated[str, Query(description="enter ID")],
        user: Annotated[str, Query(description="enter book title, author ISBN or category")]
):
    active = user_active(id)
    if active["active"]:
        user_search = user_search_book(user)
        return user_search

    raise HTTPException(status_code=400, detail="you are not allowed to search book")



