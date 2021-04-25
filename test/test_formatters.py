from flask_mdform import formatters
from mdform import FormExtension, Markdown

TEXT = """
Welcome to the form tester

name* = ___[30]
e-mail* = @
really annoying 323 name = ...

[section:user]
name* = ___
"""


JINJA_WTF = """<p>Welcome to the form tester</p>
<p>{{ form.name.label }} {{ form.name }}
{{ form.e_mail.label }} {{ form.e_mail }}
{{ form.really_annoying_323_name.label }} {{ form.really_annoying_323_name }}</p>
<p>{{ form.user_name.label }} {{ form.user_name }}</p>"""

JINJA_WTF_BS4 = """<p>Welcome to the form tester</p>
<p>{{ wtf.form_field(form.name, form_type='horizontal', class="form-control", maxlength=30) }}
{{ wtf.form_field(form.e_mail, form_type='horizontal', class="form-control") }}
{{ wtf.form_field(form.really_annoying_323_name, form_type='horizontal', class="form-control") }}</p>
<p>{{ wtf.form_field(form.user_name, form_type='horizontal', class="form-control") }}</p>"""


FORM = {
    "name": dict(
        label="name", type="StringField", required=True, length=30, nolabel=False
    ),
    "e_mail": dict(label="e-mail", type="EmailField", required=True, nolabel=False),
    "really_annoying_323_name": dict(
        label="really annoying 323 name",
        type="FileField",
        required=False,
        allowed=None,
        description=None,
        nolabel=False,
    ),
    "user_name": dict(
        label="name", type="StringField", required=True, length=None, nolabel=False
    ),
}


def test_flask_wtf():
    md = Markdown(extensions=[FormExtension(formatter=formatters.flask_wtf)])
    assert md.convert(TEXT) == JINJA_WTF
    assert md.mdform_definition == FORM


def test_flask_wtf_bs4():
    md = Markdown(
        extensions=[FormExtension(formatter=formatters.flask_wtf_bs4("jQuery"))]
    )
    assert md.convert(TEXT) == JINJA_WTF_BS4
    assert md.mdform_definition == FORM
