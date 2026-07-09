# Подключаем pytest, чтобы использовать fixture — заготовки для тестов.
import pytest

# Импортируем Flask-приложение из файла app.py.
# Переименовываем app в flask_app, чтобы не путать его с fixture app ниже.
from app import app as flask_app


@pytest.fixture()
def app():
    """
    Подготавливает Flask-приложение для тестов.
    """

    # Включаем тестовый режим Flask.
    # Это нужно, чтобы приложение корректно работало внутри pytest.
    flask_app.config.update({
        "TESTING": True,
    })

    # Отдаём подготовленное приложение тестам.
    yield flask_app


@pytest.fixture()
def client(app):
    """
    Создаёт тестового клиента Flask.

    Через client тесты смогут открывать страницы:
    client.get("/")
    client.get("/about")
    client.get("/db-check")
    """

    # test_client() имитирует пользователя, который отправляет запросы к сайту.
    return app.test_client()
