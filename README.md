# fastapi-sqlalchemy
Generate REST CRUD and GraphQL endpoints based upon SqlAlchemy tables.


## Goals:
- Expedite creation of a multi-protocol API with little to no customization required.
- Allow rich customization as needed.


## TODO:
1. Generate the Pydantic validation model, but allow one to be specified to customize.
   1. Primary Keys not editable by default.
2. Show column names in the generated update CRUD endpoint. 
3. Add `json+api` support instead of simple JSON responses and requests.
4. Generate GraphQL mutation and subscription, not just query.
5. Generate the GraphQL schema based upon a sqlalchemy table.
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
