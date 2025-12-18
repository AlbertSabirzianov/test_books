"""
Модуль маршрутов FastAPI для работы с сущностью Tag.

Реализованы следующие эндпоинты:

- GET /tags/ — получить все теги.
- GET /tags/{tag_id} — получить тег по ID.
- GET /tags/user/{user_id} — получить все теги пользователя.
- POST /tags/user/{user_id} — создать новый тег для пользователя.
- POST /tags/link/tag/{tag_id}/item/{item_id} — связать тег с элементом.
- POST /tags/unlink/tag/{tag_id}/item/{item_id} — удалить связь тега с элементом.
- DELETE /tags/{tag_id} — удалить тег по ID.

Особенности:

- Используется SQLAlchemy ORM с жадной загрузкой тегов для элементов (joinedload).
- Обработка ошибок с HTTPException (404 при отсутствии, 400 при ошибках создания или дублирования).
- Валидация входных данных через Pydantic-схемы.
- Логика работы с БД делегирована функциям из модуля service.
- При связывании и отвязывании тегов с элементами проверяется существование обеих сущностей.
- При удалении тега возвращается статус 204 No Content.

Данный модуль обеспечивает REST API для управления тегами и их связями с элементами в приложении.
"""

import sqlalchemy
from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.orm import joinedload

from src.service import (create_model, delete_model_by_id, get_model_by_id, get_all_models, get_models_by_user_id,
                         add_tag_to_item, remove_tag_from_item)
from src.schema import TagBaseSchema, TagWithIdSchema, ItemWithTagsSchema
from src.models import Tag, User, Item

tag_router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)


@tag_router.get(
    "/",
    response_model=list[TagWithIdSchema]
)
def get_all_tags():
    return get_all_models(Tag)


@tag_router.get(
    "/{tag_id}",
    response_model=TagWithIdSchema
)
def get_tag_by_id(tag_id: int):
    tag = get_model_by_id(model_id=tag_id, model=Tag)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@tag_router.get(
    "/user/{user_id}",
    response_model=list[TagWithIdSchema]
)
def get_user_tags(user_id: int):
    user = get_model_by_id(model_id=user_id, model=User)
    if user is None:
       raise HTTPException(status_code=404, detail="User not found")
    return get_models_by_user_id(user_id=user_id, model=Tag)


@tag_router.post(
    "/user/{user_id}",
    response_model=TagBaseSchema
)
def create_tag(user_id: int, tag: TagBaseSchema):
    user = get_model_by_id(model_id=user_id, model=User)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        create_model(model=Tag, schema=tag, user_id=user_id)
        return tag
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=400, detail="Tag already exists")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@tag_router.post(
    "/link/tag/{tag_id}/item/{item_id}",
    response_model=ItemWithTagsSchema
)
def link_tag_item(tag_id: int, item_id: int):
    tag = get_model_by_id(model_id=tag_id, model=Tag)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    item = get_model_by_id(model_id=item_id, model=Item, options=[joinedload(Item.tags)])
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        add_tag_to_item(item=item, tag=tag)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=400, detail="Item already exists")
    return get_model_by_id(model_id=item_id, model=Item, options=[joinedload(Item.tags)])


@tag_router.post(
    "/unlink/tag/{tag_id}/item/{item_id}",
    response_model=ItemWithTagsSchema
)
def unlink_tag_item(tag_id: int, item_id: int):
    tag = get_model_by_id(model_id=tag_id, model=Tag)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    item = get_model_by_id(model_id=item_id, model=Item, options=[joinedload(Item.tags)])
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    remove_tag_from_item(item=item, tag=tag)
    return get_model_by_id(model_id=item_id, model=Item, options=[joinedload(Item.tags)])



@tag_router.delete("/{id}")
def delete_tag(tag_id: int, response: Response):
    try:
        delete_model_by_id(model=Tag, model_id=tag_id)
        response.status_code = status.HTTP_204_NO_CONTENT
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
