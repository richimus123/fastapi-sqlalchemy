"""Example application built with DAB."""

import datetime
import os

import sqlalchemy
import strawberry
import uvicorn

from pydantic import BaseModel

from fastapi_sqlalchemy import api

DB_URL = os.getenv('DB_URL', 'postgresql://example:example@localhost/example')
MetaData = sqlalchemy.MetaData()


app = api.FastAPIBuilder(database_url=DB_URL)
AuthorTable = sqlalchemy.Table(
    "author",
    MetaData,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("alias", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("birth_date", sqlalchemy.Date, nullable=False),
    sqlalchemy.UniqueConstraint('name', 'birth_date'),
)
BookTable = sqlalchemy.Table(
    "book",
    MetaData,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("publication_date", sqlalchemy.Date),
    sqlalchemy.Column("revision", sqlalchemy.Integer),
    sqlalchemy.UniqueConstraint('name', 'revision'),
)
BookAuthorTable = sqlalchemy.Table(
    "book_author",
    MetaData,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("author_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("book_id", sqlalchemy.Integer, nullable=False),
)


class AuthorModel(BaseModel):
    """Validation model for Author requests."""

    name: str
    birth_date: datetime.date


class BookModel(BaseModel):
    """Validation model for Book requests."""

    name: str
    publication_date: datetime.date
    revision: int


class BookAuthorModel(BaseModel):
    """Validation model for Book/Author relationship requests."""

    author_id: int
    book_id: int


app.add_rest_crud_api('/author', AuthorModel, AuthorTable)
app.add_rest_crud_api('/book', BookModel, BookTable)
app.add_rest_crud_api('/book_author', BookAuthorModel, BookAuthorTable)


@strawberry.type
class Author:
    name: str
    birth_date: datetime.date


@strawberry.type
class Book:
    name: str
    publication_date: datetime.date
    revision: int


@strawberry.type
class Query:
    """Define GraphQL Queries."""

    @strawberry.field
    def author(self) -> Author:
        """Resolver for authors."""
        return Author(name="Patrick", birth_date=datetime.date.today())

    @strawberry.field
    def book(self) -> Book:
        """Resolver for books."""
        return Book(name="Sponge Bob", publication_date=datetime.date.today(), revision=1)


app.add_graphql_api(strawberry.Schema(query=Query))


if __name__ == "__main__":
    engine = sqlalchemy.create_engine(DB_URL)
    MetaData.create_all(bind=engine)
    uvicorn.run(app, host='0.0.0.0', port=80)
