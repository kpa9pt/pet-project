import os

# Заглушки для Pydantic
os.environ.setdefault("TELEGRAM_TOKEN", "fake_token_for_tests")
os.environ.setdefault("SECRET_KEY", "fake_secret_key_for_tests")

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/orders",
)


# ---------------------------------------------------
# Async DB session
# ---------------------------------------------------
@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(DATABASE_URL, echo=False)

    session_maker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        yield session

    await engine.dispose()
