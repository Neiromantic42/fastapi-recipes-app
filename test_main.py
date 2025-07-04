import asyncio
import random

from fastapi.testclient import TestClient

from database import engine
from main import app
from models import Base


# Создаем таблицы в тестовой БД
async def create_test_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(create_test_tables())  # Асинхронно создаём таблицы

client = TestClient(app)


def test_post_create_recipe():
    response = client.post(
        "/create/recipe/",
        json={
            "dish_name": f"Test Dish {random.randint(1, 1000)}",
            "cooking_time": 15,
            "ingredients": "Test ingredients",
            "description_dish": "Test description",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert all(
        key in data
        for key in [
            "dish_name",
            "cooking_time",
            "ingredients",
            "description_dish",
            "id",
            "views_counter",
        ]
    )


def test_get_recipies():
    response = client.get("/recipes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for i in range(len(data) - 1):
        current = data[i]
        next_item = data[i + 1]
        if current["views_counter"] > next_item["views_counter"]:
            continue
        elif current["views_counter"] == next_item["views_counter"]:
            assert current["cooking_time"] <= next_item["cooking_time"]
        else:
            raise AssertionError("Сортировка по кол-ву просмотров нарушена")


def test_get_detailed_recipe():
    # Создаём рецепт, чтобы точно знать его ID
    response_create = client.post(
        "/create/recipe/",
        json={
            "dish_name": "Detailed Dish",
            "cooking_time": 20,
            "ingredients": "Some ingredients",
            "description_dish": "Some description",
        },
    )
    assert response_create.status_code == 200
    recipe = response_create.json()
    recipe_id = recipe["id"]

    # Первый запрос (увеличим счетчик просмотров)
    response_1 = client.get(f"/recipes/{recipe_id}")
    assert response_1.status_code == 200
    data_1 = response_1.json()
    current_views_counter = data_1["views_counter"]

    # Второй запрос (счетчик должен увеличиться)
    response_2 = client.get(f"/recipes/{recipe_id}")
    assert response_2.status_code == 200
    data_2 = response_2.json()
    next_views_counter = data_2["views_counter"]

    assert current_views_counter < next_views_counter


def test_error_handling_get_recipe():
    non_existent_id = 100
    response = client.get(f"/recipes/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert (
        data["detail"] == f"Рецепт с id {non_existent_id} не существует."
        f" Пожалуйста, укажите существующий id"
    )


def test_recipe_creation_error_handling():
    response = client.post(
        "/create/recipe/",
        json={
            "dish_name": "Test Dish",
            "cooking_time": 15,
            "ingredients": 100,  # Не валидные данные
            "description_dish": "Test description",
        },
    )
    assert response.status_code == 422
