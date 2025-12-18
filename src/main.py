"""
Главный модуль запуска FastAPI приложения.

- Загружает переменные окружения из файла .env с помощью load_dotenv().
- Инициализирует настройки приложения через класс AppSettings.
- Создаёт все таблицы в базе данных, используя SQLAlchemy metadata.
- Регистрирует маршруты (routers) для пользователей, тегов, элементов и тестов.
- Предоставляет функцию get_app() для создания и конфигурации экземпляра FastAPI.
- При запуске напрямую (через __main__) загружает настройки и может запускать сервер (код запуска можно дополнить).

Этот модуль служит точкой входа для запуска и конфигурации веб-приложения на FastAPI.
"""

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

from models import engine, Base
from routers import user_router, tag_router, item_router, test_router
from settings import AppSettings



def get_app() -> FastAPI:
    Base.metadata.create_all(engine)
    app = FastAPI()
    app.include_router(user_router)
    app.include_router(tag_router)
    app.include_router(item_router)
    app.include_router(test_router)
    return app


if __name__ == "__main__":
    load_dotenv()
    app_settings = AppSettings()

    uvicorn.run(get_app(), port=app_settings.port, host=app_settings.host)