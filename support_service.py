import os

import psycopg2


class SupportQuestionProcessingError(Exception):
    def __init__(self, user_name):
        self.user_name = user_name

        super().__init__(
            f"Не удалось обработать вопрос пользователя {user_name}."
        )


INSERT_SUPPORT_QUESTION = """
INSERT INTO support_questions (
    user_name,
    email,
    message
)
VALUES (%s, %s, %s)
RETURNING id, created_at;
"""


def process_support_question(user_name, email, message):
    user_name = user_name.strip()
    email = email.strip()
    message = message.strip()

    if not user_name or not email or not message:
        raise ValueError("Заполните все поля формы.")

    if user_name.casefold() == "эрик картман":
        raise SupportQuestionProcessingError(user_name)

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "Переменная окружения DATABASE_URL не установлена."
        )

    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(database_url)
        cursor = connection.cursor()

        cursor.execute(
            INSERT_SUPPORT_QUESTION,
            (
                user_name,
                email,
                message,
            ),
        )

        question_id, created_at = cursor.fetchone()

        connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

    return {
        "id": question_id,
        "user_name": user_name,
        "email": email,
        "message": message,
        "created_at": created_at,
    }
