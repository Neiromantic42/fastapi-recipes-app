from sqlalchemy import Column, String, Integer, Text
from database import Base

# Модель кулинарной книги будет отображаться в таблицу cookbook
class CookBook(Base): # Наследует от базового класса
    __tablename__ = 'cookbook'
    # Описание столбцов таблицы кулинарной книги
    id = Column(Integer, primary_key=True, index=True) # Уникальный ID книги, первичный ключ, быстрый доступ к id
    dish_name = Column(String, unique=True) # Название блюда
    cooking_time = Column(Integer) # Время приготовления блюда
    ingredients = Column(Text) # список ингредиентов
    description_dish = Column(Text) # текстовое описание блюда
    views_counter = Column(Integer, default=0) # Счетчик просмотров конкретного рецепта

