from pydantic import BaseModel, Field


class NewUser(BaseModel):
    name: str
    contact_detail: str
    membership_type: str
    active: bool


class MemberBookCheckout(NewUser):
    limit_of_books: int


class Activity(BaseModel):
    is_active: bool
