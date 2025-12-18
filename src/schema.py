"""
Модуль содержит Pydantic-схемы для валидации и сериализации данных, связанных с пользователями,
 элементами (items) и тегами (tags).

Классы схем:

- UserBaseSchema: базовые поля пользователя (email, display_name).
- ItemBaseSchema: базовые поля элемента (title, kind, status, priority, notes).
- TagBaseSchema: базовые поля тега (name).
- IDSchema: схема с полем id для наследования.
- UserWithIdSchema, TagWithIdSchema, ItemWithIdSchema: расширенные схемы с id.
- ItemWithTagsSchema: элемент с вложенным списком тегов.
- ItemSearchParams: параметры для поиска и фильтрации элементов, включая фильтры по статусу, типу, приоритету, тегам, подстроке в заголовке, диапазону дат создания, пагинацию и сортировку.

Используются перечисления из модуля enums для строгой типизации полей kind, status, priority, а также для параметров сортировки.

Схемы обеспечивают удобную и безопасную работу с входными и выходными данными API, включая автоматическую валидацию и преобразование типов.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr

from enums import ItemKind, ItemStatus, ItemPriority, SortOrder, SortField


class UserBaseSchema(BaseModel):
    email: EmailStr
    display_name: str

class ItemBaseSchema(BaseModel):
    title: str
    kind: ItemKind
    status: ItemStatus
    priority: ItemPriority
    notes: Optional[str] = None

class TagBaseSchema(BaseModel):
    name: str

class IDSchema(BaseModel):
    id: int

class UserWithIdSchema(IDSchema, UserBaseSchema):
    pass

class TagWithIdSchema(IDSchema, TagBaseSchema):
    pass

class ItemWithIdSchema(IDSchema, ItemBaseSchema):
    pass

class ItemWithTagsSchema(IDSchema, ItemBaseSchema):
    tags: list[TagWithIdSchema]

class ItemSearchParams(BaseModel):
    status: Optional[ItemStatus] = None
    kind: Optional[ItemKind] = None
    priority: Optional[ItemPriority] = None
    tag_names: Optional[List[str]] = None
    title_substring: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    limit: int = 20
    offset: int = 0
    sort_field: SortField = SortField.created_at
    sort_order: SortOrder = SortOrder.desc
