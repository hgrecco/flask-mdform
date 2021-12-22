"""
    flask_mdform.fields
    ~~~~~~~~~~~~~~~~~~~

    This module implements some new fields and re-export wtform fields
    that are supported by flask-mdform.

    Also generate wtforms.Field from mdform.fields.FieldDict

    :copyright: 2021 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from flask_wtf.file import FileAllowed, FileField, FileRequired, FileStorage
from markupsafe import Markup
from wtforms import (
    DateField,
    DecimalField,
    EmailField,
    FloatField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    TimeField,
)
from wtforms import validators as v
from wtforms import widgets

from mdform import fields as mdfields


class ListWidgetPlus(widgets.ListWidget):
    """
    Renders a list of fields as a `ul` or `ol` list.

    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """

    def __call__(self, field, **kwargs):
        subfield_kw = {k: v for k, v in kwargs.items() if k in ("disabled", "readonly")}
        kwargs.setdefault("id", field.id)
        html = ["<{} {}>".format(self.html_tag, widgets.html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append(f"<li>{subfield.label} {subfield(**subfield_kw)}</li>")
            else:
                html.append(f"<li>{subfield(**subfield_kw)} {subfield.label}</li>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """

    widget = ListWidgetPlus(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class RadioFieldPlus(SelectField):
    """
    Like a SelectField, except displays a list of radio buttons.

    Iterating the field will produce subfields (each containing a label as
    well) in order to allow custom rendering of the individual radio fields.
    """

    widget = ListWidgetPlus(prefix_label=False)
    option_widget = widgets.RadioInput()


class FileSize:
    """Validates that the uploaded file is within a minimum and maximum file size (set in bytes).

    Parameters
    ----------
    max_size : int
        maximum allowed file size (in bytes).
    min_size : int
        minimum allowed file size (in bytes). Defaults to 0 bytes.
    message : str
        error message
    """

    def __init__(self, max_size, min_size=0, message=None):
        self.min_size = min_size
        self.max_size = max_size
        self.message = message

    def __call__(self, form, field):
        if not (isinstance(field.data, FileStorage) and field.data):
            return

        file_size = len(field.data.read())
        field.data.seek(0)  # reset cursor position to beginning of file

        if (file_size < self.min_size) or (file_size > self.max_size):
            # the file is too small or too big => validation failure
            raise v.ValidationError(
                self.message
                or field.gettext(
                    "File must be between {min_size} and {max_size} bytes.".format(
                        min_size=self.min_size, max_size=self.max_size
                    )
                )
            )


def from_mdfield(f: mdfields.Field):
    validators = []

    if f.required:
        validators.append(v.DataRequired())

    sf = f.specific_field

    if length := getattr(sf, "length", None):
        validators.append(v.length(max=length))

    if isinstance(sf, mdfields.StringField):
        return StringField(f.label, validators=validators)
    elif isinstance(sf, mdfields.TextAreaField):
        return TextAreaField(f.label, validators=validators)
    elif isinstance(sf, mdfields.IntegerField):
        validators.append(v.NumberRange(min=sf.min, max=sf.max))
        return IntegerField(f.label, validators=validators)
    elif isinstance(sf, mdfields.FloatField):
        validators.append(v.NumberRange(min=sf.min, max=sf.max))
        return FloatField(f.label, validators=validators)
    elif isinstance(sf, mdfields.DecimalField):
        validators.append(v.NumberRange(min=sf.min, max=sf.max))
        return DecimalField(f.label, validators=validators, places=sf.places)
    elif isinstance(sf, mdfields.DateField):
        return DateField(f.label, validators=validators)
    elif isinstance(sf, mdfields.TimeField):
        return TimeField(f.label, validators=validators)
    elif isinstance(sf, mdfields.EmailField):
        validators.append(v.Email())
        if not f.required:
            # Not sure but this is needed, maybe not now tha this is an emailfied
            validators.append(v.Optional())
        return EmailField(f.label, validators=validators)
    elif isinstance(sf, mdfields.SelectField):
        return SelectField(f.label, choices=sf.choices, validators=validators)
    elif isinstance(sf, mdfields.RadioField):
        return RadioFieldPlus(f.label, choices=sf.choices, validators=validators)
    elif isinstance(sf, mdfields.CheckboxField):
        return MultiCheckboxField(f.label, choices=sf.choices, validators=validators)
    elif isinstance(sf, mdfields.FileField):
        validators.append(FileSize(max_size=5 * 1024 * 1024))
        validators.append(FileRequired())
        if sf.allowed:
            validators.append(FileAllowed(sf.allowed, sf.description or sf.allowed))
        return FileField(f.label, validators=validators)
    else:
        raise TypeError(f"Unknown specific field: {sf.__class__}")


class MyUrlWidget(widgets.TextInput):
    def __call__(self, field, **kwargs):
        html = "<a href='%s' target='_blank'> %s </a>"
        return Markup(html % (field._value(), field._value()))


class MyEmailWidget(widgets.TextInput):
    def __call__(self, field, **kwargs):
        html = "<a href='mailto:%s'>%s</a>"
        return Markup(html % (field._value(), field._value()))


def generate_LinkField(label):
    return StringField(label, widget=MyUrlWidget())


def generate_EmailField(label):
    return StringField(label, widget=MyEmailWidget())
