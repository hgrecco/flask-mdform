import pytest
from flask import Flask as _Flask

from flask_mdform import formatters


class Flask(_Flask):
    testing = True
    secret_key = __name__

    def make_response(self, rv):
        if rv is None:
            rv = ""

        return super().make_response(rv)


@pytest.fixture
def app():
    app = Flask(__name__, template_folder="templates")
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["MDFORM_FORMATTER"] = formatters.flask_wtf
    app.config["MDFORM_CLASS_NAME"] = "MdForm"
    return app


@pytest.yield_fixture
def app_ctx(app):
    with app.app_context() as ctx:
        yield ctx


@pytest.yield_fixture
def req_ctx(app):
    with app.test_request_context() as ctx:
        yield ctx


@pytest.fixture
def client(app):
    return app.test_client()
