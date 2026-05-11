import os
from pathlib import Path

import pytest
import pytest_asyncio

from testcontainers.postgres import PostgresContainer
from alembic import command
from alembic.config import Config

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

# ---------------------------------------------------
# Paths
# ---------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BASE_DIR / "alembic.ini"


# ---------------------------------------------------
# 1. PostgreSQL container
# ---------------------------------------------------
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


# ---------------------------------------------------
# 2. DATABASE_URL
# ---------------------------------------------------
@pytest.fixture(scope="session")
def database_url(postgres_container):
    sync_url = postgres_container.get_connection_url()

    async_url = sync_url.replace(
        "postgresql+psycopg2",
        "postgresql+asyncpg",
    )

    return async_url


# ---------------------------------------------------
# 3. Apply Alembic migrations
# ---------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def apply_migrations(database_url):
    os.environ["DATABASE_URL"] = database_url

    alembic_cfg = Config(str(ALEMBIC_INI))

    # абсолютный путь до migrations
    alembic_cfg.set_main_option(
        "script_location",
        str(BASE_DIR / "shared/db/migrations"),
    )

    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")


# ---------------------------------------------------
# 4. Async DB session
# ---------------------------------------------------
@pytest_asyncio.fixture
async def db_session(database_url, apply_migrations):
    engine = create_async_engine(
        database_url,
        echo=False,
    )

    session_maker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        yield session

    await engine.dispose()
