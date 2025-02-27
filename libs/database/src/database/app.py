from typing import AsyncGenerator
from sqlalchemy import event, Select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_MASTER_DATABASE_URL = (
    "mysql+aiomysql://test.id:aaaa@127.0.0.1:13306/test_project"
)
SQLALCHEMY_SLAVE_DATABASE_URL = (
    "mysql+aiomysql://test.id:aaaa@127.0.0.1:13307/test_project"
)


class Base(DeclarativeBase):
    pass


engines = {
    "master": create_async_engine(
        SQLALCHEMY_MASTER_DATABASE_URL,
        pool_size=5,
        max_overflow=0,
        pool_recycle=3600,
        pool_pre_ping=True,
    ),
    "slave": create_async_engine(
        SQLALCHEMY_SLAVE_DATABASE_URL,
        pool_size=5,
        max_overflow=0,
        pool_recycle=3600,
        pool_pre_ping=True,
    ),
}

# async sessionmaker for both master and slave
async_master_session = async_sessionmaker(
    bind=engines["master"], autocommit=False, autoflush=False
)
async_slave_session = async_sessionmaker(
    bind=engines["slave"], autocommit=False, autoflush=False
)


class RoutingSession:
    """
    Custom async session class that routes queries to either the master or slave.
    """

    def __init__(self):
        self.session = None

    async def __call__(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Create and yield a session.
        """
        try:
            yield await self.get_session()
        finally:
            await self.session.close()

    async def get_session(self, mapper=None, clause=None, **kw) -> AsyncSession:
        """
        Get the appropriate session (master or slave) based on the query type.

        Args:
            mapper: The SQLAlchemy mapper (if available).
            clause: The SQLAlchemy clause (if available).
            **kw: Additional keyword arguments.

        Returns:
            An AsyncSession instance.
        """
        if self.session:
            return self.session
        if self.is_write_operation(clause):
            self.session = async_master_session()
        else:
            self.session = async_slave_session()
        return self.session

    def is_write_operation(self, clause) -> bool:
        """
        Check if the operation is a write operation.

        Args:
            clause: The SQLAlchemy clause.

        Returns:
            True if it's a write operation, False otherwise.
        """
        # You may add more conditions to check if the operation is a write.
        return not isinstance(clause, Select)

    async def close(self):
        """Close the current session."""
        if self.session:
            await self.session.close()
            self.session = None


# Helper function for creating tables if needed
async def create_all_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """
    Dependency to get a database session.
    """
    db = RoutingSession()
    try:
        yield await db.get_session()
    finally:
        await db.close()


# listener of connection pool
# @event.listens_for(AsyncEngine, "engine_connect")
# def ping_connection(dbapi_connection, connection_record, connection_proxy):
#     """
#     Ensure stale connections are not used by testing the connection
#     before using it.
#     """
#     cursor = dbapi_connection.cursor()
#     try:
#         cursor.execute("SELECT 1")
#     except Exception as exc:
#         raise exc
#     finally:
#         cursor.close()
