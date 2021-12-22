import decimal
import io
from datetime import date, time

TEXT_1 = """
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


JINJA_WTF_1 = """<p>Welcome to the form tester</p>
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

JINJA_WTF_BS4_1 = """<p>Welcome to the form tester</p>
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

TEXT_2 = """
Welcome to the form tester

name* = ___[30]
email* = @
avatar* = ...
day* = d/m/y
time* = hh:mm
skipme = ___
"""

JINJA_WTF_2 = """<p>Welcome to the form tester</p>
<p>{{ form.name.label }} {{ form.name }}
{{ form.e_mail.label }} {{ form.e_mail }}
{{ form.really_annoying_323_name.label }} {{ form.really_annoying_323_name }}</p>
<p>{{ form.user_name.label }} {{ form.user_name }}</p>"""


TEXT_3 = """
Welcome to the form tester

name* = ___[30]
_e-mail* = @"""


JINJA_WTF_BS4_3 = """<p>Welcome to the form tester</p>
<p>{{ wtf.form_field(form.name, form_type='horizontal', class="form-control", maxlength=30) }}
{{ wtf.form_field(form.e_mail, form_type='horizontal', class="form-control nolabel") }}</p>"""

RENDERED_JINJA_WTF_INDEX = """
<p>Welcome to the form tester</p>
<p><label for="name">name</label> <input id="name" maxlength="30" name="name" required type="text" value="">
<label for="email">email</label> <input id="email" name="email" required type="email" value="">
<label for="day">day</label> <input id="day" name="day" required type="date" value="">
<label for="time">time</label> <input id="time" name="time" required type="time" value="">
<label for="skipme">skipme</label> <input id="skipme" name="skipme" type="text" value=""></p>"""


RENDERED_JINJA_WTF_INDEX_JOHN = """
<p>Welcome to the form tester</p>
<p><label for="name">name</label> <input id="name" maxlength="30" name="name" required type="text" value="John Smith">
<label for="email">email</label> <input id="email" name="email" required type="email" value="john@smith.com">
<label for="day">day</label> <input id="day" name="day" required type="date" value="2020-12-23">
<label for="time">time</label> <input id="time" name="time" required type="time" value="02:18">
<label for="skipme">skipme</label> <input id="skipme" name="skipme" type="text" value="123"></p>"""

RENDERED_JINJA_WTF_INDEX_PETER = """
<p>Welcome to the form tester</p>
<p><label for="name">name</label> <input id="name" maxlength="30" name="name" required type="text" value="Peter Capusotto">
<label for="email">email</label> <input id="email" name="email" required type="email" value="peter@capusotto.com">
<label for="day">day</label> <input id="day" name="day" required type="date" value="2020-12-23">
<label for="time">time</label> <input id="time" name="time" required type="time" value="02:18">
<label for="skipme">skipme</label> <input id="skipme" name="skipme" type="text" value="123"></p>"""

RENDERED_JINJA_WTF_INDEX_PETER_RO = """
<p>Welcome to the form tester</p>
<p><label for="name">name</label> <input disabled id="name" maxlength="30" name="name" readonly required type="text" value="Peter Capusotto">
<label for="email">email</label> <a href='mailto:peter@capusotto.com'>peter@capusotto.com</a>
<label for="day">day</label> <input disabled id="day" name="day" readonly required type="date" value="2020-12-23">
<label for="time">time</label> <input disabled id="time" name="time" readonly required type="time" value="02:18">
<label for="skipme">skipme</label> <input disabled id="skipme" name="skipme" readonly type="text" value="123"></p>"""


DATA = {
    "john@smith.com": {
        "name": "John Smith",
        "email": "john@smith.com",
        # "avatar": (io.BytesIO(b"abcdef"), 'test.jpg'),
        "day": "2020-12-23",
        "time": "02:18",
        "skipme": "123",
    },
    "peter@capusotto.com": {
        "name": "Peter Capusotto",
        "email": "peter@capusotto.com",
        # "avatar": (io.BytesIO(b"abcdef"), 'test.jpg'),
        "day": "2020-12-23",
        "time": "02:18",
        "skipme": "123",
    },
    "other@capusotto.com": {
        "string_field": "string field content",
        "integer_field": 1,
        "decimal_field": 1.1,
        "float_field": 0.1,
        "text_area_field": "text area field content",
        "date_field": "2000-12-01",
        "time_field": "12:34",
        "email_field": "email@field.com",
        "radio_field": "A",
        "checkbox_field": "B",
        "select_field": "A",
        "file_field": (io.BytesIO(b"abcdef"), "test.jpg"),
    },
}


ALL_FIELDS = """
String Field = ___
Integer Field = ###
Decimal Field = #.#
Float Field = #.#f
Text Area Field = AAA
Date Field = d/m/y
Time Field = hh:mm
Email Field = @
Radio Field = (x) A () B
Checkbox Field = [x] A [] B
Select Field = {(A), B}
File Field = ...
skipme = ___
"""

SERIALIZED_ALL = {
    "string_field": "string field content",
    "integer_field": 1,
    "decimal_field": "1.1",
    "float_field": 0.1,
    "text_area_field": "text area field content",
    "date_field": "2000-12-01",
    "time_field": "12:34:00",
    "email_field": "email@field.com",
    "radio_field": "A",
    "checkbox_field": [
        "B",
    ],
    "select_field": "A",
    "file_field": "dummy",
}

FORM_KWARGS_ALL = {
    "string_field": "string field content",
    "integer_field": 1,
    "decimal_field": decimal.Decimal("1.1"),
    "float_field": 0.1,
    "text_area_field": "text area field content",
    "date_field": date.fromisoformat("2000-12-01"),
    "time_field": time.fromisoformat("12:34:00"),
    "email_field": "email@field.com",
    "radio_field": "A",
    "checkbox_field": [
        "B",
    ],
    "select_field": "A",
    "file_field": "dummy",
}
