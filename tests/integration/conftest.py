import os
import subprocess
from pathlib import Path

import pytest
import pytest_asyncio

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

BASE_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BASE_DIR / "alembic.ini"


# ---------------------------------------------------
# 1. Запуск всех сервисов через docker-compose
# ---------------------------------------------------
@pytest.fixture(scope="session")
def docker_compose_up():
    # Останавливаем и удаляем старые контейнеры, если они висят
    subprocess.run(
        ["docker", "compose", "down", "--volumes", "--remove-orphans"],
        cwd=str(BASE_DIR),
        check=False,
    )

    # Поднимаем все контейнеры
    subprocess.run(
        ["docker", "compose", "up", "-d", "--build"],
        cwd=str(BASE_DIR),
        check=True,
    )

    yield

    # Останавливаем и удаляем всё после тестов
    subprocess.run(
        ["docker", "compose", "down", "--volumes", "--remove-orphans"],
        cwd=str(BASE_DIR),
        check=False,
    )


# ---------------------------------------------------
# 2. DATABASE_URL для тестов (на хосте)
# ---------------------------------------------------
@pytest.fixture(scope="session")
def database_url(docker_compose_up):
    # PostgreSQL доступен на localhost:5432
    return "postgresql+asyncpg://postgres:postgres@localhost:5432/orders"


# ---------------------------------------------------
# 3. Apply Alembic migrations
# ---------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def apply_migrations(database_url):
    os.environ["DATABASE_URL"] = database_url
    alembic_cfg = Config(str(ALEMBIC_INI))
    alembic_cfg.set_main_option(
        "script_location", str(BASE_DIR / "shared/db/migrations")
    )
    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")


# ---------------------------------------------------
# 4. Async DB session
# ---------------------------------------------------
@pytest_asyncio.fixture
async def db_session(database_url, apply_migrations):
    engine = create_async_engine(database_url, echo=False)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()
