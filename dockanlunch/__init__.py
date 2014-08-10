# coding: utf-8

from datetime import datetime
from flask import Flask, render_template, url_for
from werkzeug.contrib.cache import SimpleCache
from models import get_all

app = Flask(__name__)
cache = SimpleCache()


@app.route("/")
def index():
    r = get_all(cache)
    if not datetime.now().weekday() in (5,6):
        return render_template("index.html", restaurants=r)
    else:
        return render_template("weekend.html", restaurants=r)

