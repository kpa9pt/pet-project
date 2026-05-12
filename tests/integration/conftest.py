import os

# Заглушки для Pydantic (устанавливаются ДО импорта app)
os.environ.setdefault("TELEGRAM_TOKEN", "fake_token_for_tests")  # noqa: E402
os.environ.setdefault("SECRET_KEY", "fake_secret_key_for_tests")  # noqa: E402
# os.environ.setdefault(  # noqa: E402
#     "DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/stub"
# )
import subprocess
from pathlib import Path
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
import time
import requests
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

BASE_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BASE_DIR / "alembic.ini"


# ---------------------------------------------------
# 1. Запуск всех сервисов через docker-compose
# ---------------------------------------------------
@pytest.fixture(scope="session")
def docker_compose_up():
    # Останавливаем и удаляем старые контейнеры
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

    # Останавливаем контейнеры после тестов
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
    return "postgresql+asyncpg://postgres:postgres@localhost:5433/orders"


# ---------------------------------------------------
# 3. Apply Alembic migrations
# ---------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def apply_migrations(database_url):
    os.environ["DATABASE_URL"] = database_url
    from shared.db.session import reset_db_state

    import asyncio

    asyncio.run(reset_db_state())

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


def wait_for_api(url: str, timeout: float = 30):
    start = time.time()

    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200 and r.json().get("status") == "ok":
                return
        except requests.RequestException:
            pass

        time.sleep(0.5)

    raise RuntimeError(f"API did not become ready: {url}")


@pytest.fixture(scope="session")
def fastapi_ready(docker_compose_up):
    wait_for_api("http://localhost:8000/health")
