from flask_mdform import formatters
from mdform import FormExtension, Markdown

TEXT = """
Welcome to the form tester

name* = ___[30]
e-mail* = @
really annoying 323 name = ...

[section:user]
name* = ___

[section]
collapse_open = {Yes[o], No}

[collapse:collapse_open]
This will be collapsed
[endcollapse]

collapse_close = {Yes[c], No}

[collapse:collapse_close]
This will be collapsed close
[endcollapse]
"""


JINJA_WTF = """<p>Welcome to the form tester</p>
<p>{{ form.name.label }} {{ form.name }}
{{ form.e_mail.label }} {{ form.e_mail }}
{{ form.really_annoying_323_name.label }} {{ form.really_annoying_323_name }}</p>
<p>{{ form.user_name.label }} {{ form.user_name }}</p>
<p>{{ form.collapse_open.label }} {{ form.collapse_open }}</p>
<div id="accordion-collapse_open">
This will be collapsed
</div>

<p>{{ form.collapse_close.label }} {{ form.collapse_close }}</p>
<div id="accordion-collapse_close">
This will be collapsed close
</div>"""

JINJA_WTF_BS4 = """<p>Welcome to the form tester</p>
<p>{{ wtf.form_field(form.name, form_type='horizontal', class="form-control", maxlength=30) }}
{{ wtf.form_field(form.e_mail, form_type='horizontal', class="form-control") }}
{{ wtf.form_field(form.really_annoying_323_name, form_type='horizontal', class="form-control") }}</p>
<p>{{ wtf.form_field(form.user_name, form_type='horizontal', class="form-control") }}</p>
<p>{{ wtf.form_field(form.collapse_open, form_type='horizontal', onchange="jQuery('#accordion-collapse_open').toggle(jQuery(this).val() === 'Yes');" , class="form-control collapser") }}</p>
<div id="accordion-collapse_open">
This will be collapsed
</div>

<p>{{ wtf.form_field(form.collapse_close, form_type='horizontal', onchange="jQuery('#accordion-collapse_close').toggle(jQuery(this).val() !== 'Yes');" , class="form-control collapser") }}</p>
<div id="accordion-collapse_close">
This will be collapsed close
</div>"""


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
    "collapse_open": dict(
        label="collapse_open",
        collapse_on="~Yes",
        type="SelectField",
        choices=(("Yes", "Yes"), ("No", "No")),
        default=None,
        required=False,
        nolabel=False,
    ),
    "collapse_close": dict(
        label="collapse_close",
        collapse_on="Yes",
        type="SelectField",
        choices=(("Yes", "Yes"), ("No", "No")),
        default=None,
        required=False,
        nolabel=False,
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
    print(md.convert(TEXT))
    assert md.convert(TEXT) == JINJA_WTF_BS4
    assert md.mdform_definition == FORM
