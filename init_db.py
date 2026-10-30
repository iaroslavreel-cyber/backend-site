import os
from contextlib import closing

import psycopg2


CREATE_SUPPORT_QUESTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS support_questions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def create_tables():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "Переменная окружения DATABASE_URL не установлена."
        )

    with closing(psycopg2.connect(database_url)) as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_SUPPORT_QUESTIONS_TABLE)

    print("Таблица support_questions успешно создана.")


if __name__ == "__main__":
    create_tables()
