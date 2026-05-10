import os

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5435/fake"
)

os.environ.setdefault("TELEGRAM_TOKEN", "fake_token_for_tests")
os.environ.setdefault("SECRET_KEY", "fake_secret_key_for_tests")
