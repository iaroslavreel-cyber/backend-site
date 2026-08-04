import os

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

    connection = None

    try:
        connection = psycopg2.connect(database_url)
        cursor = connection.cursor()

        cursor.execute(CREATE_SUPPORT_QUESTIONS_TABLE)

        connection.commit()

        cursor.close()

        print("Таблица support_questions успешно создана.")

    except Exception:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    create_tables()
