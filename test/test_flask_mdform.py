from io import BytesIO

from flask_mdform import from_mdstr

TEXT = """
Welcome to the form tester

name* = ___[30]
email* = @
avatar* = ...
dia* = d/m/y
hora* = hh:mm
skipme = ___
"""

JINJA = """<p>Welcome to the form tester</p>
<p>{{ form.name }}
{{ form.e_mail }}
{{ form.really_annoying_323_name }}</p>
<p>{{ form.user_name }}</p>"""

JINJA_WTF = """<p>Welcome to the form tester</p>
<p>{{ wtf.form_field(form.name, form_type='horizontal', class="form-control", maxlength=30) }}
{{ wtf.form_field(form.e_mail, form_type='horizontal', class="form-control") }}
{{ wtf.form_field(form.really_annoying_323_name, form_type='horizontal', class="form-control") }}</p>
<p>{{ wtf.form_field(form.user_name, form_type='horizontal', class="form-control") }}</p>"""

FORM = {
    "name": dict(label="name", type="StringField", required=True, length=30),
    "e_mail": dict(label="e-mail", type="EmailField", required=True),
    "really_annoying_323_name": dict(
        label="really annoying 323 name",
        type="FileField",
        required=False,
        allowed=None,
        description=None,
    ),
    "user_name": dict(label="name", type="StringField", required=True, length=None),
}


meta, html, BasicForm = from_mdstr(TEXT, "BasicForm")


def upload_func(data):
    return "dummy"


def test_plain_form(app, client):
    @app.route("/", methods=["POST"])
    def index():
        form = BasicForm()
        assert form.name.data is not None
        assert form.email.data is not None
        assert form.avatar.data is not None
        assert form.avatar.data.filename == "flask.png"
        assert form.dia.data is not None
        assert form.hora.data is not None
        assert form.skipme.data is not None

        d = form.to_plain_dict(upload_func, skip=("skipme",))
        assert d["name"] == "Juan Carlos"
        assert d["email"] == "juan@bla.com"
        assert d["avatar"] == "dummy"
        assert d["dia"] == "2020-12-23"
        assert d["hora"] == "02:18:00"
        assert "skipme" not in d

        d2 = BasicForm.from_plain_dict(d).to_plain_dict(upload_func, skip=("skipme",))
        assert d == d2

    client.post(
        "/",
        data={
            "name": "Juan Carlos",
            "email": "juan@bla.com",
            "avatar": (BytesIO(), "flask.png"),
            "dia": "2020-12-23",
            "hora": "02:18",
            "skipme": "123",
        },
    )
