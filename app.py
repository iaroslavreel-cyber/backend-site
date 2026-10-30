import logging
import os
import sys
import time
from ipaddress import ip_address
from uuid import uuid4

import psycopg2
from flask import Flask, g, render_template, request

from support_service import (
    SupportQuestionProcessingError,
    process_support_question,
)


log_level_name = os.environ.get("LOG_LEVEL", "INFO").strip().upper()

logging.basicConfig(
    level=logging.WARNING,
    format=(
        "%(asctime)s "
        "level=%(levelname)s "
        "logger=%(name)s "
        "%(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)


app = Flask(__name__)

app.logger.setLevel(
    os.environ.get("APP_LOG_LEVEL", log_level_name).strip().upper()
)

http_logger = logging.getLogger("yt_academy.http")
http_logger.setLevel(
    os.environ.get("HTTP_LOG_LEVEL", log_level_name).strip().upper()
)

support_logger = logging.getLogger("yt_academy.support")
support_logger.setLevel(
    os.environ.get("SUPPORT_LOG_LEVEL", log_level_name).strip().upper()
)


def get_client_ip():
    if os.environ.get("RENDER") == "true":
        cloudflare_ip = request.headers.get("CF-Connecting-IP")

        if cloudflare_ip:
            try:
                return str(ip_address(cloudflare_ip.strip()))
            except ValueError:
                pass

    return request.remote_addr or "unknown"


@app.before_request
def prepare_request_logging():
    g.request_started_at = time.perf_counter()

    g.request_id = (
        request.headers.get("Rndr-Id")
        or str(uuid4())
    )

    g.user_name = "anonymous"


@app.after_request
def log_request(response):
    if request.path.startswith("/static/"):
        return response

    duration_ms = (
        time.perf_counter() - g.request_started_at
    ) * 1000

    http_logger.info(
        (
            "event=http_request "
            "user=%s "
            "method=%s "
            "path=%s "
            "ip=%s "
            "status=%s "
            "duration_ms=%.1f "
            "request_id=%s"
        ),
        g.user_name,
        request.method,
        request.path,
        get_client_ip(),
        response.status_code,
        duration_ms,
        g.request_id,
    )

    return response


@app.errorhandler(SupportQuestionProcessingError)
def handle_support_question_processing_error(error):
    g.user_name = error.user_name

    support_logger.exception(
        (
            "event=support_question_processing_failed "
            "user=%s "
            "path=%s "
            "ip=%s "
            "request_id=%s"
        ),
        error.user_name,
        request.path,
        get_client_ip(),
        g.request_id,
    )

    return (
        render_template(
            "support.html",
            error_message=(
                "Не удалось обработать ваш вопрос. "
                "Попробуйте отправить его позже."
            ),
        ),
        500,
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/courses")
def courses():
    return render_template("courses.html")


@app.route("/courses/math")
def math_course():
    return render_template("math_course.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/support", methods=["GET", "POST"])
def support():
    if request.method == "POST":
        support_logger.debug(
            "event=support_question_received request_id=%s",
            g.request_id,
        )

        try:
            question = process_support_question(
                request.form.get("name", ""),
                request.form.get("email", ""),
                request.form.get("message", ""),
            )

        except ValueError as error:
            return (
                render_template(
                    "support.html",
                    error_message=str(error),
                ),
                400,
            )

        g.user_name = question["user_name"]

        support_logger.info(
            (
                "event=support_question_saved "
                "user=%s "
                "question_id=%s "
                "request_id=%s"
            ),
            question["user_name"],
            question["id"],
            g.request_id,
        )

        return render_template(
            "support.html",
            success_message=(
                "Ваш вопрос получен. "
                f"Номер вопроса: {question['id']}."
            ),
        )

    return render_template("support.html")


@app.route("/db-check")
def db_check():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        return (
            "<h1>Database error</h1>"
            "<p>DATABASE_URL is not set.</p>",
            500,
        )

    try:
        connection = psycopg2.connect(database_url)
        cursor = connection.cursor()

        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return (
            "<h1>Database connection OK</h1>"
            f"<p>Result: {result[0]}</p>"
        )

    except Exception as error:
        return (
            "<h1>Database connection failed</h1>"
            f"<p>{error}</p>",
            500,
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.logger.info(
        (
            "event=application_start "
            "port=%s "
            "app_log_level=%s "
            "http_log_level=%s "
            "support_log_level=%s"
        ),
        port,
        logging.getLevelName(app.logger.getEffectiveLevel()),
        logging.getLevelName(http_logger.getEffectiveLevel()),
        logging.getLevelName(support_logger.getEffectiveLevel()),
    )

    app.logger.debug(
        "event=debug_logging_check status=visible"
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
    )
