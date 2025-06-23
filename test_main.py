import pytest
import random
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_post_create_recipe():
    response = client.post(
        "/create/recipe/",
        json={
            "dish_name": "Test Dish {name}".format(name=random.randint(1, 1000)),
            "cooking_time": 15,
            "ingredients": "Test ingredients",
            "description_dish": "Test description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert all(key in data for key in [
        "dish_name", "cooking_time", "ingredients",
        "description_dish", "id", "views_counter"
    ])

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
            assert False, "Сортировка по кол-ву просмотров нарушена"

def test_get_detailed_recipe():
    recipe_id = 2
    response_1 = client.get(f"/recipes/{recipe_id}")
    assert response_1.status_code == 200
    data = response_1.json()
    current_views_counter = data["views_counter"]
    response_2 = client.get(f"/recipes/{recipe_id}")
    data_2 = response_2.json()
    next_views_counter = data_2["views_counter"]
    assert current_views_counter < next_views_counter

def test_error_handling_get_recipe():
    non_existent_id = 100
    response = client.get(f"/recipes/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == f"Рецепт с id {non_existent_id} не существует. Пожалуйста, укажите существующий id"

def test_recipe_creation_error_handling():
    response = client.post(
        "/create/recipe/",
        json={
            "dish_name": "Test Dish",
            "cooking_time": 15,
            "ingredients": 100,  # Не валидные данные
            "description_dish": "Test description"
        }
    )
    assert response.status_code == 422