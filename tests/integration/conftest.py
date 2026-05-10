import asyncio
import time
import asyncpg
import pytest
from alembic import command
from alembic.config import Config


def build_db_url(port: int) -> str:
    return f"postgresql://test:test@localhost:{port}/test"


async def _check_db(url: str):
    conn = await asyncpg.connect(url)
    await conn.execute("SELECT 1")
    await conn.close()


def wait_for_postgres(port: int) -> str:
    url = build_db_url(port)

    for _ in range(60):
        try:
            asyncio.run(_check_db(url))
            return url
        except Exception:
            time.sleep(1)

    raise RuntimeError(f"Postgres not ready on {url}")


@pytest.fixture(scope="session")
def postgres_container():
    # ❗ ВАЖНО: НЕ ХАРДКОД
    from integration.docker import container  # <-- твой реальный контейнер

    port = container.get_exposed_port(5432)

    raw_url = wait_for_postgres(port)

    cfg = Config("alembic.ini")
    cfg.set_main_option(
        "sqlalchemy.url", raw_url.replace("postgresql://", "postgresql+psycopg2://")
    )

    command.upgrade(cfg, "head")

    yield raw_url
