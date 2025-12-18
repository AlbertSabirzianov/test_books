"""
Модуль содержит тестовый роутер FastAPI для создания seed-данных в базе.

Эндпоинт:

- POST /test/ — вызывает функцию create_seed_data(),
 которая заполняет базу начальными тестовыми данными (пользователи, теги, элементы).

Обработка ошибок:

- При попытке повторного создания данных,
 если возникает IntegrityError (например, дублирование уникальных значений),
 возвращается HTTP 400 с сообщением "Item already exists".

Использование:

- Удобно для быстрого наполнения базы данными при разработке и тестировании.
- Рекомендуется ограничивать доступ к этому роутеру в продакшене.

"""

import sqlalchemy
from fastapi import APIRouter, HTTPException
from src.service import create_seed_data


test_router = APIRouter(
    tags=["test"],
    prefix="/test",
)

@test_router.post("/")
def create_data_for_tests():
    try:
        create_seed_data()
        return "success"
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Item already exists",
        )