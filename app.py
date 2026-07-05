from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello world</h1><p>Это главная страница.</p>"

@app.route("/about")
def about():
    return "<h1>О сайте</h1><p>Это вторая страница моего backend-сайта.</p>"

app.run(host="0.0.0.0", port=5000, debug=True)