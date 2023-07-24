import asyncio
import typing as T

from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.orm import merge_frozen_result
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from db.models import Base, insert_objects, A, B, C
from fastapi import FastAPI
from functools import cache
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine


class Data(BaseModel):
    id: int
    name: str


app = FastAPI()


@app.get("/")
async def get_data() -> T.List[Data]:
    tables = [A, B, C]
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    statements = [select(table) for table in tables]
    frozen_results = await asyncio.gather(
        *(
            run_out_of_band(async_session, statement)
            for statement in statements
        )
    )
    async with async_session() as session:
        results = [
            (
                await session.run_sync(
                    merge_frozen_result, statement, result, load=False
                )
            )()
            for statement, result in zip(statements, frozen_results)
        ]
    rows = [item for sublist in results for item in sublist]

    return sorted([Data(id=row._data[0].id, name=row._data[0].name) for row in rows],
                  key=lambda data: data.id)


async def run_out_of_band(async_sessionmaker, statement, merge_results=True):

    async with async_sessionmaker() as oob_session:
        await oob_session.connection(
            execution_options={"isolation_level": "AUTOCOMMIT"}
        )

        result = await oob_session.execute(statement)

        if merge_results:
            return result.freeze()
        else:
            await result.close()


@app.get("/raw_sql")
async def get_data_raw_sql() -> T.List[Data]:
    stmt = text(
        "select id, name from a union all select id, name from b union all select id, name from c order by 1;")
    async_session = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(stmt)
            return [Data(id=row.id, name=row.name)for row in result]


@cache
def get_engine() -> AsyncEngine:
    return create_async_engine(
        "postgresql+asyncpg://user:password@postgres/data",
        echo=True,
    )


async def populate_data() -> None:
    engine = get_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await insert_objects(async_session)


@app.on_event("startup")
async def startup_event():
    await populate_data()
