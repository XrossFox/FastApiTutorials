import datetime
from typing import Optional
from fastapi import Body, FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Book:
    id: int = -1
    title: str = ""
    author: str = ""
    description: str = ""
    rating: int = -1,
    published_date: datetime.date = None

    def __init__(self, id: int, title : str, author: str, description: str, rating: int, published_date: datetime.date) -> None:
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="Not needed on creation", default=None)
    title: str = Field(min_length=3, max_length=50)
    author: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=3, max_length=250)
    rating: int = Field(gt=0, lt=100)
    published_date: datetime.date = Field(default=datetime.datetime.now().date())

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "Neim",
                "description": "a Comment",
                "rating": 5,
                "published_date": "YYYY-MM-DD"
            }
        }
    }


BOOKS = [
    Book(1, "PRocrastinator", "Jose", "bad book", 1, (datetime.datetime.now().date()) - datetime.timedelta(days=25)),
    Book(2, "azure", "Luis", "boring asf", 2, (datetime.datetime.now().date()) - datetime.timedelta(days=5)),
    Book(3, "Jejetl", "Eli", "Kinda ok", 3, (datetime.datetime.now().date()) - datetime.timedelta(days=10)),
    Book(4, "Adios pendejo!", "David", "La meritita verga", 5, (datetime.datetime.now().date()) - datetime.timedelta(days=8)),
    Book(5, "Java es para putos", "DAvid", "maomeno", 3, (datetime.datetime.now().date()) - datetime.timedelta(days=8)),
]
     

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/{published_date}")
async def read_book_by_pub_date(published_date: str):
    date_to_Search = datetime.datetime.strptime(published_date, "%Y-%m-%d").date()
    list_of_books = []
    for book in BOOKS:
        print(book)
        print(date_to_Search)
        print(book.published_date)
        print(date_to_Search == book.published_date)
        if date_to_Search == book.published_date:
            list_of_books.append(book)

    return list_of_books


@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book

@app.get("/books/")
async def read_book_by_rating(book_rating: int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)

    return books_to_return
                

@app.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

def find_book_id(book: Book):
    book.id = len(BOOKS) + 1
    return book

@app.put("/books/update_book")
async def update_book(book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book


@app.delete("/books/{book_id}")
async def update_book(book_id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            break
