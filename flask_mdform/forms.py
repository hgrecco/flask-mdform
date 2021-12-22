"""
    flask_mdform.forms
    ~~~~~~~~~~~~~~~~~~

    FlaskForm/WTForm from a Markdown based form.

    :copyright: 2021 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import decimal
import pathlib
from datetime import date, time

from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms_components import read_only

from mdform import FormExtension, Markdown
from mdform import fields as mdform_fields

from . import fields


def filled_form_to_content(
    form, upload_func=None, *, skip=(), skip_types=(SubmitField,)
):
    """Iterates through a filled form object and returns a dictionary
    with the values in a json compatible format.

    - files are uploaded and the value is replaced by the file id.
    - date and times are serialized to string in ISO format.

    In flask, a possible upload_func is:

        def upload_func(data):
            fileid = upload_set.save(data)
            return url_for("file", fileid=fileid, _external=True)

    where upload_set is an instance of flask_uploads.UploadSet
    and file is a view:

        @app.route("/file/<path:fileid>")
        def file(fileid):
            return send_from_directory(directory=upload_path, filename=fileid)

    Parameters
    ----------
    form : FlaskForm or WTForm object
    upload_func: func
        uploads a file and return the url
    skip : tuple of strings
        fields to skip.

    Returns
    -------
    dict
    """
    out = {}
    # noinspection PyProtectedMember
    for name, field in form._fields.items():
        if name in skip:
            continue

        if isinstance(
            field,
            (
                fields.StringField,
                fields.TextAreaField,
                fields.IntegerField,
                fields.FloatField,
                fields.EmailField,
                fields.RadioFieldPlus,
                fields.MultiCheckboxField,
                fields.SelectField,
            ),
        ):
            out[name] = field.data

        elif isinstance(field, fields.DecimalField):
            out[name] = str(field.data)

        elif isinstance(field, (fields.DateField, fields.TimeField)):
            out[name] = field.data.isoformat()

        elif isinstance(field, fields.FileField):
            if field.data is None:
                out[name] = None
                continue
            out[name] = upload_func(field.data)

        elif isinstance(field, skip_types):
            pass

        else:
            raise ValueError(f"Cannot serialize form field for {field}")

    return out


def generate_form_kwargs(form_cls, data, on_missing_field="raise", skip=tuple()):
    """Iterates through a dict, parsing each value using the
    spec defined in form_cls.

    - decimal fields are serialized a string.
    - date and time fields are serialized from string in ISO format.

    Parameters
    ----------
    form_cls : FlaskForm or WTForm class (not instance)
    data : Dict
    on_missing_field : str
        "raise" (default): raise an Exception.
        "add": add value to dictionary as is.
        "ignore": ignore and continue.
    skip : tuple of strings
        these keys in the data will not be passed to kwargs.

    Returns
    -------
    dict
    """
    assert isinstance(form_cls, type)

    if on_missing_field not in ("raise", "add", "ignore"):
        raise ValueError(
            f"on_missing_field must be 'raise', 'add' or 'ignore' not '{on_missing_field}'"
        )

    out = {}
    for name, value in data.items():
        if name in skip:
            continue
        field = getattr(form_cls, name, None)
        if field is None or not hasattr(field, "field_class"):
            if on_missing_field == "raise":
                raise ValueError(f"No field found named '{name}'")
            elif on_missing_field == "add":
                out[name] = value
            continue

        field_class = field.field_class

        if field_class in (
            fields.StringField,
            fields.TextAreaField,
            fields.IntegerField,
            fields.FloatField,
            fields.EmailField,
            fields.RadioFieldPlus,
            fields.MultiCheckboxField,
            fields.SelectField,
        ):
            out[name] = value

        elif field_class is fields.DecimalField:
            out[name] = decimal.Decimal(value)

        elif field_class is fields.DateField:
            out[name] = date.fromisoformat(value)

        elif field_class is fields.TimeField:
            out[name] = time.fromisoformat(value)

        elif field_class is fields.FileField:
            out[name] = value

        else:
            raise ValueError(f"Cannot generate form kwarg for {field_class}")

    return out


class DictFormMixin:
    """A form mixin to serialize the data from and to a dict with
    json compatible values.
    """

    def to_plain_dict(
        self, upload_func=None, skip=("csrf_token", "submit"), skip_types=(SubmitField,)
    ):
        return filled_form_to_content(
            self, upload_func, skip=skip, skip_types=skip_types
        )

    @classmethod
    def from_plain_dict(cls, data, on_missing_field="raise", skip=tuple()):
        data = generate_form_kwargs(
            cls, data, on_missing_field=on_missing_field, skip=skip
        )
        return cls(**data)


class ReadOnlyFormMixin:
    """A form that convert all fields into read-only."""

    _read_only_attrs = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._read_only_attrs:
            for attr_name in self._read_only_attrs:
                read_only(getattr(self, attr_name))


def from_mdstr(
    mdstr, class_name, read_only=False, block=None, extends=None, formatter=None
):
    """Generates form metadata, template, form from markdown form.

    Parameters
    ----------
    mdstr : str
        markdown content
    class_name : str
        class of the form.
    read_only : bool
        If true, the folder will be rendered as read-only.
    block :  str
        Name of the block where the form is inserted.
    extends : str
        Name of the template that is extended.
    formatter : callable
        That format variable name and dict to string.

    Returns
    -------
    dict, str, FlaskForm
    """
    md = Markdown(extensions=["meta", FormExtension(formatter=formatter)])
    html = md.convert(mdstr)

    if read_only:
        wtform = generate_read_only_form_cls(class_name, md.mdform_definition)
    else:
        wtform = generate_form_cls(class_name, md.mdform_definition)

    if extends:
        tmpl = '{%- extends "' + extends + '" %}\n'
    else:
        tmpl = ""

    if block:
        tmpl += "{% block " + block + " %}{{ super() }}"
        tmpl += html
        tmpl += "{% endblock %}"
    else:
        tmpl += html

    return md.Meta, tmpl, wtform


def from_mdfile(
    mdfile, class_name=None, read_only=False, block=None, extends=None, formatter=None
):
    """Generates form metadata, template, form from markdown form.

    Parameters
    ----------
    mdstr : str
        markdown content
    class_name : str
        class of the form.
    read_only : bool
        If true, the folder will be rendered as read-only.
    block :  str
        Name of the block where the form is inserted.
    extends : str
        Name of the template that is extended.
    formatter : callable
        That format variable name and dict to string.

    Returns
    -------
    dict, str, FlaskForm
    """

    mdfile = pathlib.Path(mdfile)

    class_name = class_name or mdfile.stem

    with mdfile.open(mode="r", encoding="utf-8") as fi:
        return from_mdstr(fi.read(), class_name, read_only, block, extends, formatter)


def generate_form_cls(name, fields_by_label, base_cls=FlaskForm):
    """Generate a FlaskForm derived class with an attribute for each field.
    It also adds a submit button.

    Parameters
    ----------
    name : str
        name of the class
    fields_by_label : Dict[str, Dict[str, Any]]
        fields organized by their labels

    Returns
    -------
    FlaskForm
    """
    cls = type(
        name,
        (
            DictFormMixin,
            base_cls,
        ),
        {},
    )
    for label, field in fields_by_label.items():
        setattr(cls, label, fields.from_mdfield(field))

    setattr(cls, "submit", SubmitField("Submit"))

    return cls


def generate_read_only_form_cls(name, fields_by_label, base_cls=FlaskForm):
    """Generate a Flask derived class that is read-only.

    For this purpose, it overwrite the type certain fields.

    Parameters
    ----------
    name : str
        name of the class
    fields_by_label : Dict[str, Field]
        fields organized by their labels

    Returns
    -------
    FlaskForm

    """
    cls = type(name, (ReadOnlyFormMixin, DictFormMixin, base_cls), {})
    for label, field in fields_by_label.items():
        if isinstance(field.specific_field, mdform_fields.EmailField):
            setattr(cls, label, fields.generate_EmailField(label))
        # elif field["type"] == "DateField":
        #     field = {**field, "type": "StringField"}
        # elif field["type"] == "TimeField":
        #     field = {**field, "type": "StringField"}
        # elif field["type"] == "DateTimeField":
        #     field = {**field, "type": "StringField"}
        else:
            setattr(cls, label, fields.from_mdfield(field))

    cls._read_only_attrs = tuple(fields_by_label.keys())

    return cls
