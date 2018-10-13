import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, book_name, author, year in reader:
        db.execute("INSERT INTO books (isbn, book_name, author, year) VALUES (:isbn, :book_name, :author, :year)",
                    {"isbn": isbn, "book_name": book_name, "author":author, "year":year})
    db.commit()

if __name__ == "__main__":
    main()
