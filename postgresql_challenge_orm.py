from os import environ
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Database name
dbname = "books"

# Get Postgresql URI variable from Conda environment
postgresql_uri = environ.get('POSTGRESQL_URI')

# Create engine
engine = create_engine(postgresql_uri + dbname)

# Create the base
Base = declarative_base()


class Author(Base):
    """ 
    A model for the "Author" table 
    """
    __tablename__ = "authors"

    # Columns of the table
    author_id = Column(Integer, primary_key=True)
    first_name = Column(String(60))
    last_name = Column(String(60))

    # String representation
    def __repr__(self):
        return f"[Author(author_id={self.author_id}, \
                first_name={self.first_name}, last_name={self.last_name})]"


class Book(Base):
    """ A model for the "Book" table """
    __tablename__ = "books"

    # Columns of the table
    book_id = Column(Integer, primary_key=True)
    title = Column(String(60))
    number_of_pages = Column(Integer)

    # String representation
    def __repr__(self):
        return f"[Book(book_id={self.book_id}, \
                title={self.title}, number_of_pages={self.number_of_pages})]"


class BookAuthor(Base):
    """ A model for the "BookAuthor" table """
    __tablename__ = "bookauthors"

    # Columns of the table
    bookauthor_id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("authors.author_id"))
    book_id = Column(Integer, ForeignKey("books.book_id"))

    author = relationship("Author")
    book = relationship("Book")

    # String representation
    def __repr__(self):
        return f"[BookAuthor(bookauthor_id={self.bookauthor_id}, \
                author_first_name={self.author.first_name}, \
                author_last_name={self.author.last_name})]"


# Add table models to the database
Base.metadata.create_all(engine)


def createSession():
    """ 
    A method to create a session for making transactions to the database 
    """
    session = sessionmaker(bind=engine)
    return session()


def addBookItem(title, number_of_pages, first_name, last_name):
    """ 
    A method to add an instance of the book object to the database

    Parameters
    ----------
        title: the title of the book
        number_of_pages: the number of pages of the book
        first_name: first name of the author
        last_name: last name of the author

    """
    book = Book(title=title, number_of_pages=number_of_pages)

    # Create a new session with the createSession function
    session = createSession()

    try:

        existingAuthor = session.query(Author).filter(
            Author.first_name == first_name, Author.last_name == last_name).first()
        # Add book to the session
        session.add(book)

        # Check if the author of the book is already in the database before adding it
        if existingAuthor is not None:
            session.flush()
            pairing = BookAuthor(
                author_id=existingAuthor.author_id, book_id=book.book_id)
        else:
            author = Author(first_name=first_name, last_name=last_name)
            session.add(author)
            session.flush()
            pairing = BookAuthor(
                author_id=author.author_id, book_id=book.book_id)

            session.add(pairing)

        session.commit()

    except:
        session.rollback()
        raise

    finally:
        session.close()


# Main()
if __name__ == "__main__":
    print("Input a new book item: \n")
    title = input("Provide the title of the book... \n")
    number_of_pages = int(input("Type the number of pages in the book... \n"))
    first_name = input("Type the first name of the author... \n")
    last_name = input("Type the last name of the author... \n")
    print("Insert book data into the database.")
    print("Loading===========>>")

    addBookItem(title, number_of_pages, first_name, last_name)

    print("Data insertion successful")
