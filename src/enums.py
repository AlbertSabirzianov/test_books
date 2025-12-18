"""
Модуль содержит перечисления (Enum) для описания различных констант, используемых в модели Item и для управления сортировкой.

Классы перечислений:

- ItemKind: типы элементов (например, книга, статья).
- ItemStatus: статусы элементов (запланировано, читается, выполнено).
- ItemPriority: приоритеты элементов (низкий, нормальный, высокий).
- SortField: поля, по которым можно сортировать (created_at, updated_at).
- SortOrder: направления сортировки (по возрастанию, по убыванию).

Использование перечислений повышает читаемость и безопасность кода, позволяя работать с ограниченным набором допустимых значений.
"""

from enum import Enum


class ItemKind(str, Enum):
    book = 'book'
    article = 'article'

class ItemStatus(str, Enum):
    planned = 'planned'
    reading = 'reading'
    done = 'done'

class ItemPriority(str, Enum):
    low = 'low'
    normal = 'normal'
    high = 'high'

class SortField(str, Enum):
    created_at = 'created_at'
    updated_at = 'updated_at'

class SortOrder(str, Enum):
    asc = 'asc'
    desc = 'desc'