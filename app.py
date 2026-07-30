import logging
import os
import sys
import time
from uuid import uuid4

import psycopg2
from flask import Flask, g, render_template, request

from support_service import process_support_question


log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()

log_level = getattr(
    logging,
    log_level_name,
    logging.INFO,
)

logging.basicConfig(
    level=log_level,
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


def get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

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

    app.logger.info(
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

        return render_template(
            "support.html",
            success_message="Ваш вопрос получен.",
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
        "event=application_start port=%s log_level=%s",
        port,
        log_level_name,
    )

    app.logger.debug(
        "event=debug_logging_check status=visible"
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
    )
