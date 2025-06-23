from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession # Импортируем асинхронный движок и сессию
from sqlalchemy.ext.declarative import declarative_base # Импортируем базовый класс для ORM-моделей
from sqlalchemy.orm import sessionmaker # Импортируем фабрику сессий


DATABASE_URL = "sqlite+aiosqlite:///./cookbook.db" # Указываем URL для подключения к SQLite через aiosqlite (асинхронно)

# Создаём асинхронный движок SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}# Для SQLite: отключаем проверку потока (необходимая настройка)
)

# Создаём фабрику асинхронных сессий
async_session = sessionmaker(
    engine,
    expire_on_commit=False, # после commit данные в объекте не сбрасываются, остаются доступными
    class_=AsyncSession # указываем, что используется асинхронная сессия
)


# # Создаем саму сессию
# session = async_session()

# Создаём базовый класс для описания моделей таблиц
Base = declarative_base()