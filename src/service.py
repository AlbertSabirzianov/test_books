"""
Модуль содержит функции для работы с базой данных через SQLAlchemy ORM.

Функции включают:

- get_model_by_id: получение объекта модели по id с опциональной загрузкой связанных данных.
- get_all_models: получение всех объектов модели с опциональной загрузкой связанных данных.
- delete_model_by_id: удаление объекта модели по id.
- create_model: создание нового объекта модели из Pydantic-схемы с дополнительными параметрами.
- get_models_by_user_id: получение объектов модели, связанных с конкретным пользователем.
- get_filtered_items: получение списка элементов (Item) с фильтрацией по статусу, типу,
 приоритету, тегам, подстроке в заголовке, диапазону дат, пагинацией и сортировкой.
- add_tag_to_item: добавление связи между элементом и тегом через таблицу ассоциации.
- remove_tag_from_item: удаление связи между элементом и тегом.
- create_seed_data: заполнение базы начальными данными — пользователями, тегами и элементами с привязкой тегов.

Особенности:

- Используется контекстный менеджер для сессий (sync_session).
- Для фильтрации и сортировки применяется SQLAlchemy Core и ORM.
- В функциях create_model и get_model_by_id используется типизация с generics.
- Функция get_filtered_items реализует сложную логику фильтрации с join по тегам и пагинацией.
- Seed-данные создают пример пользователей с элементами и тегами для тестирования.

Данный модуль служит репозиторием для удобного и безопасного взаимодействия с базой данных в приложении.
"""

from datetime import datetime

from pydantic import BaseModel
from typing import Type, TypeVar, Optional, Sequence, List

from sqlalchemy import delete, select, and_, desc, asc, insert
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from .models import sync_session, User, Tag, Item, Base, item_tag
from .schema import UserBaseSchema
from .enums import SortField, SortOrder, ItemKind, ItemStatus, ItemPriority

T = TypeVar("T", bound=Base)

def get_model_by_id(model_id, model: T, options: Optional[List[_AbstractLoad]] = None) -> Optional[T]:
    with sync_session() as session:
        stmt = select(model).where(model.id == model_id)
        if options:
            stmt = stmt.options(*options)
        result = session.scalars(stmt).unique()
        return result.first()


def get_all_models(model: T, options: Optional[List[_AbstractLoad]] = None) -> Sequence[T]:
    with sync_session() as session:
        stmt = select(model)
        if options:
            stmt = stmt.options(*options)
        result = session.scalars(stmt).unique()
        return result.fetchall()


def delete_model_by_id(model_id: int, model: Type[Base]):
    with sync_session() as session:
        session.execute(delete(model).where(model.id == model_id))
        session.commit()

def create_model(model: Type[Base], schema: BaseModel, **kwargs):
    with sync_session() as session:
        session.add(model(**schema.model_dump(), **kwargs))
        session.commit()


def get_models_by_user_id(
    user_id: int,
    model: T,
    options: Optional[List[_AbstractLoad]] = None
) -> List[T]:
    with sync_session() as session:
        stmt = select(model).where(model.user_id == user_id)
        if options:
            stmt = stmt.options(*options)
        result = session.scalars(stmt).unique()
        return result.fetchall()


def get_filtered_items(
    status: Optional[str] = None,
    kind: Optional[str] = None,
    priority: Optional[str] = None,
    tag_names: Optional[List[str]] = None,
    title_substring: Optional[str] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    limit: int = 20,
    offset: int = 0,
    sort_field: SortField = SortField.created_at,  # created_at | updated_at | priority
    sort_order: SortOrder = SortOrder.desc  # asc | desc
) -> List[Item]:

    with sync_session() as session:
        stmt = select(Item).distinct()

        # Фильтры по простым полям
        filters = []
        if status:
            filters.append(Item.status == status)
        if kind:
            filters.append(Item.kind == kind)
        if priority:
            filters.append(Item.priority == priority)
        if title_substring:
            filters.append(Item.title.ilike(f"%{title_substring}%"))
        if created_from:
            filters.append(Item.created_at >= created_from)
        if created_to:
            filters.append(Item.created_at <= created_to)

        # Фильтр по тегам (любая из переданных)
        if tag_names:
            # Присоединяем таблицу тегов через ассоциацию
            stmt = stmt.join(Item.tags)
            filters.append(Tag.name.in_(tag_names))

        if filters:
            stmt = stmt.where(and_(*filters))

        # Сортировка
        sort_col_map = {
            "created_at": Item.created_at,
            "updated_at": Item.updated_at,
            "priority": Item.priority
        }
        sort_col = sort_col_map.get(sort_field, Item.created_at)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(sort_col))
        else:
            stmt = stmt.order_by(asc(sort_col))

        # Пагинация
        stmt = stmt.limit(limit).offset(offset)

        # Чтобы избежать дублирования из-за join с тегами
        stmt = stmt.options(joinedload(Item.tags))

        result = session.scalars(stmt).unique().all()
        return result


def add_tag_to_item(item: Item, tag: Tag) -> None:
    with sync_session() as session:
        session.execute(
            insert(item_tag).values(item_id=item.id, tag_id=tag.id)
        )
        session.commit()


def remove_tag_from_item(item: Item, tag: Tag) -> None:
    with sync_session() as session:
        session.execute(
            delete(item_tag).where(
                (item_tag.c.item_id == item.id) & (item_tag.c.tag_id == tag.id)
            )
        )
        session.commit()


def create_seed_data():
    with sync_session() as session:
        # Создаём пользователей
        user1 = User(email="alice@example.com", display_name="Alice")
        user2 = User(email="bob@example.com", display_name="Bob")

        session.add_all([user1, user2])
        session.commit()  # чтобы получить id пользователей

        # Создаём теги для пользователей
        tag1 = Tag(user_id=user1.id, name="urgent")
        tag2 = Tag(user_id=user1.id, name="work")
        tag3 = Tag(user_id=user2.id, name="personal")

        session.add_all([tag1, tag2, tag3])
        session.commit()

        # Создаём items для пользователей
        item1 = Item(
            user_id=user1.id,
            title="Finish report",
            kind=ItemKind.book,
            status=ItemStatus.reading,
            priority=ItemPriority.high,
            notes="Due next week",
            created_at=datetime.utcnow()
        )
        item2 = Item(
            user_id=user1.id,
            title="Buy groceries",
            kind=ItemKind.book,
            status=ItemStatus.reading,
            priority=ItemPriority.high,
            notes="Milk, Bread, Eggs",
            created_at=datetime.utcnow()
        )
        item3 = Item(
            user_id=user2.id,
            title="Call mom",
            kind=ItemKind.book,
            status=ItemStatus.reading,
            priority=ItemPriority.high,
            notes="Sunday evening",
            created_at=datetime.utcnow()
        )

        # Привязываем теги к items
        item1.tags.append(tag1)  # urgent
        item1.tags.append(tag2)  # work
        item2.tags.append(tag2)  # work
        item3.tags.append(tag3)  # personal

        session.add_all([item1, item2, item3])
        session.commit()