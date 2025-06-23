from sqlalchemy.ext.asyncio import (  # Импортируем асинхронный движок и сессию
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.ext.declarative import (  # Импортируем базовый класс
    declarative_base,
)
from sqlalchemy.orm import sessionmaker  # Импортируем фабрику сессий

DATABASE_URL = "sqlite+aiosqlite:///./cookbook.db"

# Создаём асинхронный движок SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },  # Для SQLite: отключаем проверку потока (необходимая настройка)
)

# Создаём фабрику асинхронных сессий
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)  # type: ignore


# # Создаем саму сессию
# session = async_session()

# Создаём базовый класс для описания моделей таблиц
Base = declarative_base()
