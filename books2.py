from typing import Optional
from fastapi import Body, FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Book:
    id: int = -1
    title: str = ""
    author: str = ""
    description: str = ""
    rating: int = -1

    def __init__(self, id: int, title : str, author: str, description: str, rating: int) -> None:
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="Not needed on creation", default=None)
    title: str = Field(min_length=3, max_length=50)
    author: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=3, max_length=250)
    rating: int = Field(gt=0, lt=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "Neim",
                "descirption": "a Comment",
                "rating": 5
            }
        }
    }


BOOKS = [
    Book(1, "PRocrastinator", "Jose", "bad book", 1),
    Book(2, "azure", "Luis", "boring asf", 2),
    Book(3, "Jejetl", "Eli", "Kinda ok", 3),
    Book(4, "Adios pendejo!", "David", "La meritita verga", 5),
]
     

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

def find_book_id(book: Book):
    book.id = len(BOOKS) + 1
    return book
