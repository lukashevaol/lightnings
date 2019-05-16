from models import Book
from db_manager import Session

session = Session()

books = session.query(Book).all()

for book in books:
    price = input(f"Price for '{book.title}': $")
    book.price = price
    session.add(book)

session.commit()

print(session.query(Book.title, Book.price).all())
session.close()
