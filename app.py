import os
import psycopg2
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello world</h1><p>Это главная страница.</p>"

@app.route("/about")
def about():
    return "<h1>О сайте</h1><p>Это вторая страница моего backend-сайта.</p>"

@app.route("/db-check")
def db_check():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        return "<h1>Database error</h1><p>DATABASE_URL is not set.</p>", 500

    try:
        connection = psycopg2.connect(database_url)
        cursor = connection.cursor()

        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return f"<h1>Database connection OK</h1><p>Result: {result[0]}</p>"

    except Exception as error:
        return f"<h1>Database connection failed</h1><p>{error}</p>", 500

port = int(os.environ.get("PORT", 5000))

app.run(host="0.0.0.0", port=port, debug=True)
