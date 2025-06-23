from typing import List  # Импортируем типы для работы с аннотациями
from fastapi import FastAPI, HTTPException  # Импортируем основной класс FastAPI для создания приложения
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select  # Для выполнения асинхронных SQL-запросов через SQLAlchemy
import models  # Модуль с моделями SQLAlchemy (например, CookBook)
import schemas  # Модуль с Pydantic-схемами для валидации данных
from database import engine, async_session  # Импортируем асинхронный движок и сессии для работы с БД
from contextlib import asynccontextmanager  # Импортируем декоратор для работы с асинхронным контекстом



# объявляем механизм жизненного цикла приложения, который заменяет старые события
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём подключение к базе данных и начинаем транзакцию
    async with engine.begin() as conn:
        # Создаём все таблицы, определённые в моделях, если они ещё не созданы
        await conn.run_sync(models.Base.metadata.create_all)
    # yield ставит точку паузы. Весь код до yield выполняется при старте приложения.
    yield  # Здесь приложение будет работать, обрабатывать запросы и маршруты.
    await engine.dispose()  # Очищаем ресурсы и закрываем соединения с базой данных.

# Создаём экземпляр приложения FastAPI и передаём ему механизм жизненного цикла
app = FastAPI(lifespan=lifespan)  # Передаем функцию lifespan для обработки событий старта и завершения.

# POST-запрос для добавления нового рецепта в бд
@app.post('/create/recipe/', response_model=schemas.CookBookOut)
async def create_recipe(recipe: schemas.CookBookIn)-> models.CookBook:
    new_recipe = models.CookBook(**recipe.model_dump()) # Создаем объект CookBook из запроса
    try:
        async with async_session() as session:
            async with session.begin():
                session.add(new_recipe)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A recipe with this dish name already exists. Please use a unique name."
        )
    return new_recipe # Возвращаем созданный рецепт (FastAPI преобразует в CookBookOut)


# GET-запрос для получения детального рецепта + 1 просмотр
@app.get('/recipes/{recipe_id}/', response_model=schemas.CookBookOut)  # Определяем GET-эндпоинт с параметром recipe_id и указываем модель ответа
async def get_detailed_recipe(recipe_id: int):  # Асинхронная функция, принимающая recipe_id как целое число
    async with async_session() as session:  # Создаём асинхронную сессию с базой данных
        async with session.begin():  # Начинаем транзакцию (автоматически вызовет commit, если не будет ошибок)
            result = await session.execute(  # Выполняем асинхронный SQL-запрос
                select(models.CookBook).where(models.CookBook.id == recipe_id)  # Формируем SELECT-запрос по ID рецепта
            )
            recipes = result.scalars().first()  # Извлекаем первый результат (если есть) из результата запроса
            if recipes is None:  # Если рецепт не найден (None)
                raise HTTPException(  # Генерируем исключение с кодом 404
                    status_code=404,
                    detail=f"Рецепт с id {recipe_id} не существует. Пожалуйста, укажите существующий id"
                )
            else:  # Если рецепт найден
                recipes.views_counter += 1  # Увеличиваем счётчик просмотров на 1
                # Поскольку мы находимся в блоке session.begin(), это изменение будет автоматически закоммичено

    return recipes  # Возвращаем объект рецепта (FastAPI автоматически сериализует его в соответствии с response_model)

# GET-запрос для получения отсортированного списка рецептов
@app.get('/recipes', response_model=List[schemas.CookBookShort])
async def get_recipes()-> List[models.CookBook]:
    async with async_session() as session: # Создаём асинхронную сессию с базой данных
        result = await session.execute(
            select(models.CookBook).order_by(
                models.CookBook.views_counter.desc(), # Сортируем объекты по кол-ву просмотров в порядке убывания
                models.CookBook.cooking_time.asc() # Сортируем объекты по времени приготовления меньше времени выше в результате
            )
        )
        recipes = result.scalars().all()# Извлекаем все объекты Book

    return recipes