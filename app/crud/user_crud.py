from app.api.database.config import books_collection, members_collections
from bson import ObjectId
from fastapi import HTTPException
from bson import ObjectId


def add_user(user):
    user_create = members_collections.insert_one(user)
    if user_create is not None:
        return user_create
    raise HTTPException(status_code=400, detail="user not added")


def edit_user(user, contact_information):
    object_id = ObjectId(user)
    edit_user_detail = members_collections.update_one({"_id": object_id},
                                                      {"$set": {"contact_detail" : contact_information}})
    if edit_user_detail is not None:
        return edit_user_detail
    raise HTTPException(status_code=400, detail="user not updated")


