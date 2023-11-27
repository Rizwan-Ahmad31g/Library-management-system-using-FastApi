from pydantic import BaseModel


class BookInformation(BaseModel):
    title: str
    author: str
    ISBN: str
    category: str
    quantity: int
    location: str
    availability: str


class NoMoreCirculation(BookInformation):
    circulation: bool | None


class LocationStatus(BookInformation):
    location: str
    status: str
