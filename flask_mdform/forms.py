"""
    flask_mdform.mdform_definitions
    ~~~~~~~~~~~~~~~~~~

    Generate a FlaskForm/WTForm from a Markdown based form.

    :copyright: 2020 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""


import pathlib
from datetime import date, time
from typing import Any, Callable, Dict
from warnings import warn

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired, FileStorage
from wtforms import (
    Field,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms import validators as v
from wtforms.fields.html5 import DateField
from wtforms.widgets.core import HTMLString, TextInput
from wtforms_components import TimeField, read_only

from mdform import FormExtension, Markdown

FORMATTERS: Dict[str, Callable[[Dict[str, Any]], Field]] = {}


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
                    "File must be between {min_size} and {max_size} bytes.".mdform_definitionat(
                        min_size=self.min_size, max_size=self.max_size
                    )
                )
            )


def form_to_dict(form, upload_func=None, *, skip=()):
    """Iterates through a filled form and returns a dictionary with the
    values in a json compatible format.

    - files are uploaded and the value is replaced by the file id.
    - date and times are serialized to string.

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
    form : FlaskForm or WTForm
    upload_func: func
        uploads a file and return the url
    skip : tuple of strings
        fields to skip.
    date_fmt : str
        formatting string for dates (following Arrow spec)
    time_fmt : str
        formatting string for times (following Arrow spec)

    Returns
    -------
    dict
    """
    data = {}
    # noinspection PyProtectedMember
    for name, field in form._fields.items():
        if name in skip:
            continue
        if field.type == "FileField":
            if field.data is None:
                data[name] = None
                continue
            data[name] = upload_func(field.data)
        elif field.type == "DateField":
            data[name] = field.data.isoformat()
        elif field.type == "TimeField":
            data[name] = field.data.isoformat()
        else:
            data[name] = field.data

    return data


def dict_to_formdict(form_cls, data):
    """Iterates through a dict, parsing each value using the
    spec defined in form_cls.

    - date and times are serialized from string.

    Parameters
    ----------
    form_cls : FlaskForm or WTForm class (not instance)
    date_fmt : str
        formatting string for dates (following Arrow spec)
    time_fmt : str
        formatting string for times (following Arrow spec)

    Returns
    -------
    dict
    """
    out = {}
    for name, value in data.items():
        field = getattr(form_cls, name, None)
        if field is None:
            out[name] = value
            continue
        field_type = field.__dict__["field_class"].__name__
        if field_type == "DateField":
            out[name] = date.fromisoformat(value)
        elif field_type == "TimeField":
            out[name] = time.fromisoformat(value)
        else:
            out[name] = value

    return out


class DictForm:
    """A form mixin to serialize the data from and to a dict with
    json compatible values.
    """

    def to_plain_dict(self, upload_func=None, skip=("csrf_token", "submit")):
        return form_to_dict(self, upload_func, skip=skip)

    @classmethod
    def from_plain_dict(cls, data):
        data = dict_to_formdict(cls, data)
        return cls(**data)


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


class ReadOnlyForm:
    """A form that convert all fields into read-only."""

    _read_only_attrs = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._read_only_attrs:
            for attr_name in self._read_only_attrs:
                read_only(getattr(self, attr_name))


def generate_field(varname, field, on_exc_raise=True):
    """Generate a WTForm.Field object from a mdform.Field object
    trying to match one of the registered parsers.

    Parameters
    ----------
    varname : str
    field : Dict[str, Any]

    Returns
    -------
    WTForm.Field

    Raises
    ------
    Exception
        If a formatter is not found for a given field type.
        If a formatter fails.

    Warnings
    --------
    UserWarning
        If a formatter is not found for a given field type.
        If a formatter fails.
    """
    try:
        fmt = FORMATTERS[field["type"]]
    except KeyError:
        msg = "# Could not find formatter for %s (%s)" % (varname, field["type"])
        if on_exc_raise:
            raise Exception(msg)
        else:
            warn(msg)
        fmt = generate_dummy

    try:
        s = fmt(field)
    except Exception as ex:
        msg = "# Could not format %s (%s)\n%s" % (varname, field["type"], ex)
        if on_exc_raise:
            raise Exception(msg)
        else:
            warn(msg)

        s = generate_dummy(field)

    return s


def generate_fields(fields):
    """Generate all WTForm.fields from a collection of mdform.Fields specified as dicts.

    Parameters
    ----------
    fields : Dict[str, Dict[str, Any]]

    Yields
    ------
    WTForm.Field
    """
    for label, field in fields.items():
        yield generate_field(label, field)


def generate_form_cls(name, fields, base_cls=FlaskForm):
    """Generate a FlaskForm derived class with an attribute for each field.
    It also adds a submit button.

    Parameters
    ----------
    name : str
        name of the class
    fields : Dict[str, Dict[str, Any]]
        fields organized by their labels

    Returns
    -------
    FlaskForm
    """
    cls = type(
        name,
        (
            DictForm,
            base_cls,
        ),
        {},
    )
    for label, field in fields.items():
        setattr(cls, label, generate_field(label, field))

    setattr(cls, "submit", SubmitField("Submit"))

    return cls


def generate_read_only_form_cls(name, fields, base_cls=FlaskForm):
    """Generate a Flask derived class that is read-only.

    For this purpose, it overwrite the type certain fields.

    Parameters
    ----------
    name : str
        name of the class
    fields : Dict[str, Dict[str, Any]]
        fields organized by their labels

    Returns
    -------
    FlaskForm

    """
    cls = type(name, (ReadOnlyForm, DictForm, base_cls), {})
    for label, field in fields.items():
        if field["type"] == "FileField":
            field = {**field, "type": "LinkField"}
        elif field["type"] == "DateField":
            field = {**field, "type": "StringField"}
        elif field["type"] == "TimeField":
            field = {**field, "type": "StringField"}
        elif field["type"] == "DateTimeField":
            field = {**field, "type": "StringField"}
        setattr(cls, label, generate_field(label, field))

    cls._read_only_attrs = tuple(fields.keys())

    return cls


##############
# Generators
##############


def register(func):
    """Register a function to generate a WTForm.Field object from
    a mdform.Field object, matching the suffix in the name

    e.g. generate_XYZ will match field objects with type XYZ.

    Parameters
    ----------
    func : callable
        mdform.Field -> wtforms.Field

    Returns
    -------

    """
    t = func.__name__.split("_", 1)[1]
    FORMATTERS[t] = func
    return func


def generate_dummy(field):
    return StringField(field["label"])


def _required(field):
    out = []
    if field["required"]:
        out.append(v.DataRequired())
    return out


@register
def generate_StringField(field):
    validators = _required(field)
    if field["length"]:
        validators.append(v.length(max=field["length"]))
    return StringField(field["label"], validators=validators)


@register
def generate_TextAreaField(field):
    validators = _required(field)
    if field["length"]:
        validators.append(v.length(max=field["length"]))
    return TextAreaField(field["label"], validators=validators)


@register
def generate_DateField(field):
    validators = _required(field)
    return DateField(field["label"], validators=validators)  # format='%d/%m/%y',


@register
def generate_TimeField(field):
    validators = _required(field)
    return TimeField(field["label"], validators=validators)


@register
def generate_EmailField(field):
    validators = [v.Email()]
    if field["required"]:
        validators.append(v.DataRequired())
    else:
        validators.append(v.Optional())
    return StringField(field["label"], validators=validators)


@register
def generate_SelectField(field):
    validators = _required(field)
    # if field.length:
    #     validators.append('v.length(max=%d)' % field.length)
    if field["default"] is None:
        return SelectField(
            field["label"], choices=field["choices"], validators=validators
        )
    else:
        return SelectField(
            field["label"], choices=field["choices"], validators=validators
        )


@register
def generate_RadioField(field):
    validators = _required(field)
    print(field["choices"])
    return RadioField(field["label"], choices=field["choices"], validators=validators)


@register
def generate_FileField(field):
    # TODO: It would be nice to make this pluggable.
    validators = [FileSize(max_size=5 * 1024 * 1024)]
    if field["required"]:
        validators.append(FileRequired())
    if field["allowed"]:
        validators.append(
            FileAllowed(field["allowed"], field["description"] or field["allowed"])
        )
    return FileField(field["label"], validators=validators)


class MyUrlWidget(TextInput):
    def __init__(self):
        super(MyUrlWidget, self).__init__()

    def __call__(self, field, **kwargs):
        html = "<a href='%s' target='_blank'> %s </a>"
        return HTMLString(html % (field._value(), field._value()))


@register
def generate_LinkField(field):
    return StringField(field["label"], widget=MyUrlWidget())
