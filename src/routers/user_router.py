"""
Модуль маршрутов FastAPI для работы с сущностью User.

Реализованы следующие эндпоинты:

- GET /users/ — получить список всех пользователей.
- GET /users/{user_id} — получить пользователя по ID.
- POST /users/ — создать нового пользователя.
- DELETE /users/{user_id} — удалить пользователя по ID.

Особенности:

- Используется SQLAlchemy ORM для работы с базой данных.
- Обработка ошибок с HTTPException:
  - 404, если пользователь не найден.
  - 400, если пользователь с таким email уже существует или другая ошибка при создании.
- Валидация входных данных через Pydantic-схему UserBaseSchema.
- Логика работы с БД делегирована функциям из модуля service.
- При успешном удалении возвращается статус 204 No Content.

Данный модуль обеспечивает REST API для управления пользователями в приложении.
"""

import sqlalchemy
from fastapi import APIRouter, Response, status, HTTPException

from src.models import User
from src.schema import UserBaseSchema, UserWithIdSchema
from src.service import create_model, delete_model_by_id, get_all_models, get_model_by_id

user_router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@user_router.get(
    "/",
    response_model=list[UserWithIdSchema]
)
def get_all_users():
    return get_all_models(User)


@user_router.get(
    "/{user_id}",
    response_model=UserWithIdSchema
)
def get_user_by_id(user_id: int):
    user = get_model_by_id(model_id=user_id, model=User)
    if user is None:
       raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.post(
    "/",
    response_model=UserBaseSchema
)
def create_user(user: UserBaseSchema):
    try:
        create_model(model=User, schema=user)
        return user
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.delete("/{id}")
def delete_user(user_id: int, response: Response):
    try:
        delete_model_by_id(model=User, model_id=user_id)
        response.status_code = status.HTTP_204_NO_CONTENT
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

