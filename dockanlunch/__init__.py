from flask import Flask, render_template, url_for
from werkzeug.contrib.cache import SimpleCache
from models import get_all

app = Flask(__name__)
cache = SimpleCache()


@app.route("/")
def index():
    r = get_all(cache)
    return render_template("index.html", restaurants=r)

