# Импортируем декоратор для работы с асинхронным контекстом
from contextlib import (
    asynccontextmanager,
)

# Импортируем типы для работы с аннотациями
from typing import List

# Импортируем основной класс FastAPI для создания приложения
from fastapi import (
    FastAPI,
    HTTPException,
)
from sqlalchemy.exc import IntegrityError

# Для выполнения асинхронных SQL-запросов через SQLAlchemy
from sqlalchemy.future import (
    select,
)

import models  # Модуль с моделями SQLAlchemy (например, CookBook)
import schemas  # Модуль с Pydantic-схемами для валидации данных

# Импортируем асинхронный движок и сессии для работы с БД
from database import (
    async_session,
    engine,
)


# объявляем механизм жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём подключение к базе данных и начинаем транзакцию
    async with engine.begin() as conn:
        # Создаём все таблицы, определённые в моделях, если они ещё не созданы
        await conn.run_sync(models.Base.metadata.create_all)
    # yield ставит точку паузы. Весь код до yield выполняется при старте
    yield  # Здесь приложение будет работать, обрабатывать запросы и маршруты.
    await engine.dispose()  # Очищаем ресурсы и закрываем соединения


# Создаём экземпляр приложения FastAPI и передаём ему механизм жизненного цикла
app = FastAPI(
    lifespan=lifespan
)  # Передаем функцию lifespan для обработки событий старта и завершения.


# POST-запрос для добавления нового рецепта в бд
@app.post("/create/recipe/", response_model=schemas.CookBookOut)
async def create_recipe(recipe: schemas.CookBookIn) -> models.CookBook:
    new_recipe = models.CookBook(
        **recipe.model_dump()
    )  # Создаем объект CookBook из запроса
    try:
        async with async_session() as session:
            async with session.begin():
                session.add(new_recipe)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A recipe with this dish name already exists."
            " Please use a unique name.",
        )
    return new_recipe  # Возвращаем рецепт(FastAPI преобразует в CookBookOut)


# GET-запрос для получения детального рецепта + 1 просмотр
@app.get(
    "/recipes/{recipe_id}/", response_model=schemas.CookBookOut
)  # Определяем GET-эндпоинт с параметром recipe_id и указываем модель ответа
async def get_detailed_recipe(
    recipe_id: int,
):  # Асинхронная функция, принимающая recipe_id как целое число
    async with async_session() as session:  # Создаём асинхронную сессию
        async with session.begin():  # Начинаем транзакцию
            result = await session.execute(  # Выполняем асинхронный SQL-запрос
                select(models.CookBook).where(
                    models.CookBook.id == recipe_id
                )  # Формируем SELECT-запрос по ID рецепта
            )
            recipes = (
                result.scalars().first()
            )  # Извлекаем первый результат (если есть) из результата запроса
            if recipes is None:  # Если рецепт не найден (None)
                raise HTTPException(  # Генерируем исключение с кодом 404
                    status_code=404,
                    detail=f"Рецепт с id {recipe_id} не существует."
                    f" Пожалуйста, укажите существующий id",
                )
            else:  # Если рецепт найден
                recipes.views_counter += 1  # Увеличиваем счётчик
                # Поскольку мы находимся в блоке session.begin(),
                # это изменение будет автоматически закоммичено

    return recipes  # Возвращаем объект рецепта


# GET-запрос для получения отсортированного списка рецептов
@app.get("/recipes", response_model=List[schemas.CookBookShort])
async def get_recipes() -> List[models.CookBook]:
    async with async_session() as session:  # Создаём асинхронную сессию
        result = await session.execute(
            select(models.CookBook).order_by(
                models.CookBook.views_counter.desc(),
                models.CookBook.cooking_time.asc(),
            )
        )
        recipes = result.scalars().all()  # Извлекаем все объекты Book

    return recipes
