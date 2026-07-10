import os

import psycopg2
import pytest


def test_database_answers():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        pytest.skip("DATABASE_URL is not set, skipping real database test")

    connection = psycopg2.connect(database_url)
    cursor = connection.cursor()

    cursor.execute("SELECT 1;")
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    assert result[0] == 1


def test_db_check_page_opens(client):
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        pytest.skip("DATABASE_URL is not set, skipping /db-check test")

    response = client.get("/db-check")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Database connection OK" in html
    assert "Result: 1" in html
