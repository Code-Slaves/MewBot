from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

# Определение базового класса модели
Base = declarative_base()

# Определение модели
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

# Создание асинхронного движка для SQLite
# Замените "sqlite+aiosqlite:///example.db" на ваш путь к файлу базы данных
engine = create_async_engine("sqlite+aiosqlite:///example.db", echo=True)

# Асинхронное создание таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Асинхронная запись в базу данных
async def async_add_user(name, age):
    # Создание асинхронной сессии
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            # Добавление нового пользователя
            new_user = User(name=name, age=age)
            session.add(new_user)
            
            # Отправка изменений в базу данных
            await session.commit()
            print(f"User {new_user.name} added.")

# Запуск асинхронных функций
import asyncio

async def main():
    await create_tables()  # Создаем таблицы, если они еще не созданы
    await async_add_user("Alice", 30)  # Добавляем пользователя

asyncio.run(main())
