# fastapi-sqlalchemy
Generate REST CRUD and GraphQL endpoints based upon SqlAlchemy tables.


## Usage:
```python

import sqlalchemy

from fastapi_sqlalchemy.api import FastAPIBuilder

# Create SQLAlchemy tables.
MetaData = sqlalchemy.MetaData()
AuthorTable = sqlalchemy.Table(
    "author",
    MetaData,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("alias", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("birth_date", sqlalchemy.Date, nullable=False),
    sqlalchemy.UniqueConstraint('name', 'birth_date'),
)

app = FastAPIBuilder(
    # Use this like you would fastapi.FastAPI
    # The main difference is that this requires a database URL.
    database_url='postgresql://example:example@localhost/example'
)

# Register the new API endpoints based upon the table.
app.add_rest_crud_api('/author', table=AuthorTable)

```
Now there will be CRUD operation endpoints available for the table.


## Goals:
- Expedite creation of a multi-protocol API with little to no customization required.
- Allow rich customization as needed.
- Enforce best practices so very little manual work is required.


## TODO:
1. Generate the Pydantic validation model, but allow one to be specified to customize.
   1. Primary Keys not editable by default.
2. Show column names in the generated update CRUD endpoint. 
3. Add `json+api` support instead of simple JSON responses and requests.
4. Support SQLAlchemy ORM, not just tables.
5. Generate all endpoints using the SQLAlchemy MetaData.
6. Generate GraphQL mutation and subscription, not just query.
7. Generate the GraphQL schema based upon a sqlalchemy table.
    i.e. instead of requiring all of this:
    ```python
    
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
    ```
    
    Just require this:
    ```python
    my_table = Table(
        'my_table',
        MetaData,
        Column(...),
    )
    
    api.add_graphql_from_table(table=my_table)
    ```
