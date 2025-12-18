"""
Модуль содержит определения моделей базы данных с использованием SQLAlchemy ORM.

Классы моделей:

- User: пользователь с уникальным email, отображаемым именем и связями к элементам (items) и тегам (tags).
- Item: элемент пользователя с полями заголовка, типа, статуса, приоритета, заметок и связью с тегами.
- Tag: тег пользователя с уникальным именем в рамках пользователя и связью с элементами.
- item_tag: вспомогательная таблица для реализации связи многие-ко-многим между Item и Tag.

Также в модуле создаётся движок SQLAlchemy для SQLite и фабрика сессий sync_session.

Использование:

- Модели позволяют работать с базой данных через ORM, управлять пользователями, элементами и тегами.
- Связи реализованы через relationship и вспомогательную таблицу item_tag.
- Таблицы создаются автоматически через Base.metadata.create_all(engine).

Пример создания сессии:

    session = sync_session()
    # работа с объектами и commit

"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table, UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship, sessionmaker,
)
from sqlalchemy.sql import func

from contains import DB_NAME

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    items = relationship('Item', back_populates='user', cascade="all, delete-orphan")
    tags = relationship('Tag', back_populates='user', cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = 'items'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    kind = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    notes = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship('User', back_populates='items')
    tags = relationship('Tag', secondary='item_tag', back_populates='items')


class Tag(Base):
    __tablename__ = 'tags'
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_tag_name'),
        {'sqlite_autoincrement': True}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)

    user = relationship('User', back_populates='tags')
    items = relationship('Item', secondary='item_tag', back_populates='tags')


# Ассоциация таблица для связи Item и Tag
item_tag = Table(
    'item_tag',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

# Пример создания движка и сессии
engine = create_engine(f'sqlite:///{DB_NAME}')


sync_session = sessionmaker(engine)