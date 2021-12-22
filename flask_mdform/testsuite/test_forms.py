import pathlib

import pytest
import wtforms
from wtforms_components import ReadOnlyWidgetProxy

from flask_mdform import formatters, from_mdfile, from_mdstr
from flask_mdform.forms import (
    ReadOnlyFormMixin,
    filled_form_to_content,
    generate_form_kwargs,
)
from flask_mdform.testsuite import data_test

meta, html, BasicForm = from_mdstr(data_test.ALL_FIELDS, "BasicForm")


def dummy_upload_func(data):
    return "dummy"


def test_serialize(app):
    assert (
        generate_form_kwargs(BasicForm, data_test.SERIALIZED_ALL)
        == data_test.FORM_KWARGS_ALL
    )

    with pytest.raises(ValueError):
        generate_form_kwargs(
            BasicForm, data_test.SERIALIZED_ALL, on_missing_field="blip"
        )

    with pytest.raises(ValueError):
        generate_form_kwargs(
            BasicForm, {**data_test.SERIALIZED_ALL, "not_a_field": True}
        )

    assert (
        generate_form_kwargs(
            BasicForm,
            {**data_test.SERIALIZED_ALL, "not_a_field": True},
            skip=("not_a_field",),
        )
        == data_test.FORM_KWARGS_ALL
    )

    assert (
        generate_form_kwargs(
            BasicForm,
            {**data_test.SERIALIZED_ALL, "not_a_field": True},
            on_missing_field="add",
        )
        == {**data_test.FORM_KWARGS_ALL, "not_a_field": True}
    )

    with app.app_context():
        filled_form = BasicForm(**data_test.FORM_KWARGS_ALL)
        assert (
            filled_form_to_content(filled_form, dummy_upload_func, skip=("skipme",))
            == data_test.SERIALIZED_ALL
        )

        d1 = filled_form.to_plain_dict(dummy_upload_func, skip=("skipme",))
        assert "skipme" not in d1

        d2 = BasicForm.from_plain_dict(d1).to_plain_dict(
            dummy_upload_func, skip=("skipme",)
        )
        assert d1 == d2

        filled_form.blip_field = object()
        filled_form._fields["blip_field"] = object()
        with pytest.raises(ValueError):
            filled_form_to_content(filled_form, dummy_upload_func, skip=("skipme",))

    # Test how to react to data item that is not a field
    BasicForm.blip_field = object()
    with pytest.raises(ValueError):
        generate_form_kwargs(
            BasicForm, {**data_test.SERIALIZED_ALL, "blip_field": True}
        )

    # Test how to react to data item that is is a Field, but not known.
    BasicForm.blip_field = wtforms.DateTimeLocalField()
    with pytest.raises(ValueError):
        generate_form_kwargs(
            BasicForm, {**data_test.SERIALIZED_ALL, "blip_field": True}
        )


def test_from_mdstr(app):
    assert (
        from_mdstr(data_test.TEXT_1, "MDForm", formatter=formatters.flask_wtf)[1]
        == data_test.JINJA_WTF_1
    )
    assert (
        from_mdstr(
            data_test.TEXT_1, "MDForm", formatter=formatters.flask_wtf_bs4("jQuery")
        )[1]
        == data_test.JINJA_WTF_BS4_1
    )

    assert (
        from_mdstr(
            data_test.TEXT_1, "MDForm", formatter=formatters.flask_wtf, block="myform"
        )[1]
        == "{% block myform %}{{ super() }}" + data_test.JINJA_WTF_1 + "{% endblock %}"
    )
    assert (
        from_mdstr(
            data_test.TEXT_1, "MDForm", formatter=formatters.flask_wtf, extends="mypage"
        )[1]
        == '{%- extends "mypage" %}\n' + data_test.JINJA_WTF_1
    )

    meta, tmpl, form_cls = from_mdstr(
        data_test.TEXT_1, "MDForm", formatter=formatters.flask_wtf, read_only=True
    )

    field_names = (
        "name",
        "e_mail",
        "really_annoying_323_name",
        "user_name",
        "collapse_open",
        "collapse_close",
    )

    assert tmpl == data_test.JINJA_WTF_1
    assert issubclass(form_cls, ReadOnlyFormMixin)
    assert form_cls._read_only_attrs == field_names

    with app.test_request_context():
        o = form_cls()
        for name in field_names:
            field = getattr(o, name)
            assert isinstance(field.widget, ReadOnlyWidgetProxy)


def test_from_mdfile():
    # from_mdfile calls from_mdstr but creates class name if not provided
    mdfile = pathlib.Path(__file__).parent / "templates" / "md" / "form_tester.md"

    meta, tmpl, form = from_mdfile(mdfile)
    assert meta == {}
    assert form.__name__ == "form_tester"

    meta, tmpl, form = from_mdfile(mdfile, "MDForm")
    assert meta == {}
    assert form.__name__ == "MDForm"

    assert (
        from_mdfile(mdfile, formatter=formatters.flask_wtf)[1] == data_test.JINJA_WTF_1
    )
    assert (
        from_mdfile(mdfile, formatter=formatters.flask_wtf, block="myform")[1]
        == "{% block myform %}{{ super() }}" + data_test.JINJA_WTF_1 + "{% endblock %}"
    )
    assert (
        from_mdfile(mdfile, formatter=formatters.flask_wtf, extends="mypage")[1]
        == '{%- extends "mypage" %}\n' + data_test.JINJA_WTF_1
    )
