# To run this example you need:
# pip install Flask Flask-WTF Flask-Bootstrap4

import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mdform import mdform
from flask_wtf import CSRFProtect

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY
Bootstrap(app)
CSRFProtect(app)


@app.route("/")
def index():
    return render_template("index.html")


def _loader():
    return dict(name="John Smith")


@app.route("/simple", methods=["GET", "POST"])
@mdform()
def simple(form):
    return str(form.to_plain_dict())


@app.route("/with_loader", methods=["GET", "POST"])
@mdform("simple.md", data_loader=_loader)
def with_loader(form):
    return str(form.to_plain_dict())


@app.route("/read_only_with_loader", methods=["GET", "POST"])
@mdform("simple.md", data_loader=_loader, read_only=True)
def read_only_with_loader(form):
    return str(form.to_plain_dict())


app.run()
