from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from shared.settings import settings

# Движок (подключение к БД)
engine = create_async_engine(settings.database_url, echo=True)

# Фабрика сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
