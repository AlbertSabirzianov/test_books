"""
Модуль маршрутов FastAPI для работы с сущностью Item.

Реализованы следующие эндпоинты:

- GET /items/ — получить все элементы с тегами.
- GET /items/{item_id} — получить элемент по ID с тегами.
- POST /items/ — поиск элементов с фильтрацией и пагинацией.
- GET /items/user/{user_id} — получить все элементы пользователя с тегами.
- POST /items/user/{user_id} — создать новый элемент для пользователя.
- DELETE /items/{item_id} — удалить элемент по ID.

Особенности:

- Используется SQLAlchemy ORM с жадной загрузкой тегов (joinedload).
- Обработка ошибок с HTTPException (404 при отсутствии, 400 при ошибках создания).
- Валидация входных данных через Pydantic-схемы.
- Логика работы с БД делегирована функциям из модуля service.
- При создании элемента проверяется существование пользователя.
- При удалении элемента возвращается статус 204 No Content.

Данный модуль обеспечивает REST API для управления элементами в приложении.
"""

import sqlalchemy
from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.orm import joinedload

from src.models import Item, User
from src.schema import ItemBaseSchema, ItemWithTagsSchema, ItemSearchParams
from src.service import (get_all_models, get_model_by_id, get_models_by_user_id, create_model, delete_model_by_id,
                         get_filtered_items)

item_router = APIRouter(
    prefix="/items",
    tags=["items"]
)


@item_router.get(
    "/",
    response_model=list[ItemWithTagsSchema],
)
def get_all_items():
    return get_all_models(Item, options=[joinedload(Item.tags)])


@item_router.get(
    "/{item_id}",
    response_model=ItemWithTagsSchema,
)
def get_item_by_id(item_id: int):
    item = get_model_by_id(model_id=item_id, model=Item, options=[joinedload(Item.tags)])
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@item_router.post(
    "/",
    response_model=list[ItemWithTagsSchema],
)
def search_items(item_search_params: ItemSearchParams):
    return get_filtered_items(
        status=item_search_params.status,
        kind=item_search_params.kind,
        priority=item_search_params.priority,
        tag_names=item_search_params.tag_names,
        title_substring=item_search_params.title_substring,
        created_from=item_search_params.created_from,
        created_to=item_search_params.created_to,
        limit=item_search_params.limit,
        offset=item_search_params.offset,
        sort_field=item_search_params.sort_field,
        sort_order=item_search_params.sort_order,
    )


@item_router.get(
    "/user/{user_id}",
    response_model=list[ItemWithTagsSchema]
)
def get_items_by_user(user_id: int):
    user = get_model_by_id(model_id=user_id, model=User)
    if user is None:
       raise HTTPException(status_code=404, detail="User not found")
    return get_models_by_user_id(user_id=user_id, model=Item, options=[joinedload(Item.tags)])


@item_router.post(
    "/user/{user_id}",
    response_model=ItemBaseSchema
)
def create_item(item: ItemBaseSchema, user_id: int):
    user = get_model_by_id(model_id=user_id, model=User)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        create_model(model=Item, schema=item, user_id=user_id)
        return item
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=400, detail="Item already exists")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@item_router.delete("/{id}")
def delete_item(item_id: int, response: Response):
    try:
        delete_model_by_id(model=Item, model_id=item_id)
        response.status_code = status.HTTP_204_NO_CONTENT
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

