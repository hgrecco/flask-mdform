import pytest

from flask_mdform import from_mdstr, on_get_form, on_submit_form, render_mdform
from flask_mdform.deco import in_app_from_mdfile
from flask_mdform.testsuite import data_test

meta, html, BasicForm = from_mdstr(data_test.TEXT_2, "BasicForm")


def test_render(app, client):
    @app.route("/<int:value>", methods=["GET"])
    def tmp(value):
        if value == 0:
            return render_mdform("index")
        elif value == 1:
            return render_mdform(
                "index", read_only=True, data=data_test.DATA["peter@capusotto.com"]
            )
        elif value == 2:
            return render_mdform("index", block="formblock", extends="othertmpl.html")

    TESTS = {
        0: data_test.RENDERED_JINJA_WTF_INDEX,
        1: data_test.RENDERED_JINJA_WTF_INDEX_PETER_RO,
        2: data_test.RENDERED_JINJA_WTF_INDEX.replace("innerform", "myform"),
    }

    for val, expected in TESTS.items():
        ret = client.get(f"/{val}")
        assert ret.data.decode("utf-8") == expected, val


def test_get_form_ro(app, client):
    @app.route("/<username>", methods=["GET"])
    @on_get_form(read_only=True)
    def index(username):
        return data_test.DATA[username]

    @app.route("/by_arg/<username>", methods=["GET"])
    @on_get_form(mdfile="index", read_only=True)
    def by_arg(username):
        return data_test.DATA[username]

    @app.route("/<mdfile>/<username>", methods=["GET"])
    @on_get_form(read_only=True)
    def by_view_arg_str(mdfile, username):
        return data_test.DATA[username]

    @app.route("/path/<path:mdfile>/<username>", methods=["GET"])
    @on_get_form(read_only=True)
    def by_view_arg(mdfile, username):
        return data_test.DATA[username]

    ret = client.get("/peter@capusotto.com")
    assert ret.data.decode("utf-8") == data_test.RENDERED_JINJA_WTF_INDEX_PETER_RO
    ret = client.get("/by_arg/peter@capusotto.com")
    assert ret.data.decode("utf-8") == data_test.RENDERED_JINJA_WTF_INDEX_PETER_RO
    ret = client.get("/index/peter@capusotto.com")
    assert ret.data.decode("utf-8") == data_test.RENDERED_JINJA_WTF_INDEX_PETER_RO
    ret = client.get("/path/index/peter@capusotto.com")
    assert ret.data.decode("utf-8") == data_test.RENDERED_JINJA_WTF_INDEX_PETER_RO


def test_get_form(app, client):
    @app.route("/<username>", methods=["GET"])
    @on_get_form(mdfile="index")
    def bla(username):
        return data_test.DATA[username]

    ret = client.get("/peter@capusotto.com")
    assert ret.data.decode("utf-8") == data_test.RENDERED_JINJA_WTF_INDEX_PETER


def test_get_form_tmpl_ctx(app, client):
    @app.route("/<username>", methods=["GET"])
    @on_get_form(mdfile="index_ver")
    def bla(username):
        return data_test.DATA[username], dict(version="1.x")

    ret = client.get("/peter@capusotto.com")
    assert (
        ret.data.decode("utf-8")
        == data_test.RENDERED_JINJA_WTF_INDEX_PETER + "\n<p>1.x</p>"
    )

    @app.route("/exc/<username>", methods=["GET"])
    @on_get_form(mdfile="index")
    def exc(username):
        return data_test.DATA[username], dict(form="1.x")

    with pytest.raises(ValueError):
        client.get("/exc/peter@capusotto.com")


def test_post_form(app, client):
    @app.route("/<username>", methods=["POST"])
    @on_submit_form(mdfile="index")
    def bla(form, username):
        return username

    ret = client.post(
        "/peter@capusotto.com",
        data=data_test.DATA["peter@capusotto.com"],
        content_type="application/x-www-form-urlencoded",
    )
    assert ret.data.decode("utf-8") == "peter@capusotto.com"


def test_post_form_not_implemented(app, client):
    @app.route("/<username>", methods=["POST"])
    @on_submit_form(mdfile="index")
    def bla(form, username):
        raise NotImplementedError

    ret = client.post(
        "/peter@capusotto.com",
        data=data_test.DATA["peter@capusotto.com"],
        content_type="application/x-www-form-urlencoded",
    )
    assert ret.data.decode("utf-8") == data_test.RENDERED_JINJA_WTF_INDEX_PETER_RO


def test_in_app_from_mdfile(app):
    with app.app_context():
        meta, tmpl_str, Form = in_app_from_mdfile(
            "index", class_name=lambda s: "BlaBla"
        )
        assert Form.__name__ == "BlaBla"

    # Check that metatada markdown plugin is working.
    with app.app_context():
        meta, tmpl_str, Form = in_app_from_mdfile(
            "index_meta", class_name=lambda s: "BlaBla"
        )
        assert meta == {
            "title": ["My Document"],
            "summary": ["A brief description of my document."],
            "authors": ["Waylan Limberg", "John Doe"],
            "date": ["October 2, 2007"],
            "blank-value": [""],
            "base_url": [r"http://example.com"],
        }
