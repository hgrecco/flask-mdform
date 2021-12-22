# To run this example you need:
# pip install Flask Flask-WTF

import os

from flask import Flask, flash, redirect, render_template, url_for
from flask_wtf import CSRFProtect

from flask_mdform import on_get_form, on_submit_form

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY
CSRFProtect(app)

app.config["MDFORM_CLASS_NAME"] = "MDForm"


DATA = {
    1: dict(
        title="The Matrix",
        description="When a beautiful stranger leads computer hacker Neo to a forbidding underworld, he discovers the shocking truth--the life he knows is the elaborate deception of an evil cyber-intelligence.",
        email="neo@matrix.com",
        imdb_rating_votes=1790903,
        imdb_rating=8.7,
        ticket_value=3.21,
        release_date="1999-03-24",
        duration="02:16:00",
        color="Yes",
        genres=("Action", "Sci-Fi"),
        mpa_movie_rating="R Restricted",
    )
}


def _load_data(uid):
    return DATA.get(uid, {})


def _save_data(uid, content):
    DATA[uid] = content


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/read_only/<int:uid>", methods=["GET"])
@on_get_form("simple", read_only=True)
def read_only(uid):
    return _load_data(uid)


@app.route("/editable/<int:uid>", methods=["GET"])
@on_get_form("simple")
def editable(uid):
    return _load_data(uid)


@app.route("/submit/<int:uid>", methods=["POST"])
@on_submit_form("simple")
def submit(form, uid):
    _save_data(uid, form.to_plain_dict())
    flash("Saved data")
    return redirect(url_for("read_only", uid=uid))


app.run()
