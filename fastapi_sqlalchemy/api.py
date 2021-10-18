"""Base FastAPI API."""

from typing import Type, Union

import databases
import pydantic
import sqlalchemy
import strawberry

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from strawberry.asgi import GraphQL


class FastAPIBuilder(FastAPI):
    """Extend the functionality of FastAPI to include REST/CRUD and GraphQL generation."""

    def __init__(self, *args, database_url: str, **kwargs) -> None:
        """Extend inputs to include a database."""
        super().__init__(*args, **kwargs)
        self.database = databases.Database(database_url)
        self.engine = sqlalchemy.create_engine(database_url)
        self.metadata = sqlalchemy.MetaData(bind=self.engine)

        @self.on_event('startup')
        async def startup() -> None:
            """Connect to the database on startup."""
            await self.database.connect()
            self.metadata.create_all()

        @self.on_event('shutdown')
        async def shutdown() -> None:
            """Disconnect from the database on shutdown."""
            await self.database.disconnect()

    def add_crud_from_meta(self, meta: sqlalchemy.MetaData) -> None:
        """Add CRUD endpoints for all tables registered in the metadata."""
        for table in meta.tables:
            name = table.__name__.lower().strip()
            self.add_rest_crud_api(name, table=table)

    def add_rest_crud_api(
            self,
            api_path: str,
            table: sqlalchemy.Table,
            model: Type[BaseModel] = None,
    ) -> None:
        """Add a new CRUD interface for a given SQLAlchemy Table and validation model."""
        if model is None:
            model = self.generate_model_from_table(table)

        @self.post(api_path, tags=[model.__name__])
        async def create(body: model) -> JSONResponse:
            """Create a new item/insert into the database."""
            values = dict(body)
            statement = table.insert().values(**values).returning(table)
            content = await self.database.execute(statement)
            return JSONResponse(status_code=201, content=content)

        @self.delete(f'{api_path}/{{item_id}}', tags=[model.__name__])
        async def delete_by_id(item_id: Union[str, int]) -> JSONResponse:
            """Delete an item by ID."""
            statement = table.delete().where(table.id == item_id)
            content = await self.database.execute(statement)
            return JSONResponse(status_code=200, content=content)

        @self.get(f'{api_path}/{{item_id}}', tags=[model.__name__])
        async def get_by_id(item_id: Union[str, int]) -> JSONResponse:
            """Get an item by ID."""
            statement = table.select().where(table.id == item_id)
            content = await self.database.execute(statement)
            return JSONResponse(status_code=200, content=content)

        @self.get(f'{api_path}', tags=[model.__name__])
        async def get_by_filters(**filters) -> JSONResponse:
            """Get an item(s) by filters."""
            statement = table.select().where(**filters)
            content = await self.database.execute(statement)
            return JSONResponse(status_code=200, content=content)

        @self.put(f'{api_path}/{{item_id}}', tags=[model.__name__])
        async def update_by_id(body: BaseModel, item_id: Union[str, int]) -> JSONResponse:
            """Update an item by ID."""
            values = dict(body)
            statement = table.update().where(table.id == item_id).values(**values)
            content = await self.database.execute(statement)
            return JSONResponse(status_code=200, content=content)

    def add_graphql_api(self, schema: strawberry.Schema) -> None:
        """Add a GraphQL endpoint for the given schema."""
        graphql_app = GraphQL(schema)
        self.add_route("/graphql", graphql_app)
        self.add_websocket_route("/graphql", graphql_app)

    def generate_model_from_table(self, table: sqlalchemy.Table) -> pydantic.BaseModel:
        """Generate a validation model (pydantic.BaseModel) based upon a SQL Alchemy table."""

