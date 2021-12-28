"""
    flask_mdform.deco
    ~~~~~~~~~~~~~~~~~

    Flask decorators and other utils to use inside a flask app.

    :copyright: 2021 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import functools
import os

from flask import current_app, flash, request

from . import formatters
from .forms import from_mdstr

CONFIG_PREFIX = "MDFORM_"

CLASS_NAME = CONFIG_PREFIX + "CLASS_NAME"
BLOCK = CONFIG_PREFIX + "BLOCK"
EXTENDS = CONFIG_PREFIX + "EXTENDS"
FORMATTER = CONFIG_PREFIX + "FORMATTER"

DEFAULTS = {
    CLASS_NAME: "MDForm",
    EXTENDS: "form.html",
    BLOCK: "innerform",
    FORMATTER: formatters.flask_wtf,
}


def _flash_form_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                "Error in the %s field - %s" % (getattr(form, field).label.text, error),
                "danger",
            )


def in_app_get_config(key):
    return current_app.config.get(key, DEFAULTS.get(key))


def in_app_get_mdfile():
    return request.view_args.get("mdfile", request.endpoint.replace(".", "/"))


@functools.lru_cache(maxsize=None)
def in_app_from_mdfile(
    mdfile,
    *,
    read_only=False,
    class_name=None,
    block=None,
    extends=None,
    formatter=None
):
    """A cached version of `from_mdfile` that must be used within an flask app."""
    mdfile_name = mdfile + ".md"

    class_name = class_name or in_app_get_config(CLASS_NAME)
    block = block or in_app_get_config(BLOCK)
    extends = extends or in_app_get_config(EXTENDS)
    formatter = formatter or in_app_get_config(FORMATTER)

    tmp = os.path.join(current_app.template_folder, "md", mdfile_name)

    if callable(class_name):
        class_name = class_name(mdfile)

    with current_app.open_resource(tmp, mode="r") as fi:
        return from_mdstr(
            fi.read(),
            class_name=class_name,
            read_only=read_only,
            block=block,
            extends=extends,
            formatter=formatter,
        )


def render_mdform(
    mdfile=None,
    *,
    read_only=False,
    block=None,
    extends=None,
    formatter=None,
    data=None,
    on_submit=None,
    flash_form_errors=None
):
    """Renders an mdform with flask (with or without data)

    Requires to be called inside an app.

    Parameters
    ----------
    mdfile : str
        Filename of the markdown file (without .md extension)
        The file is loaded from the flask template folder.
    block :  str or None
        Name of the block where the form is inserted.
        If None, use app.config["MDFORM_BLOCK"] which is "innerform" by default.
    extends : str or None
        Name of the template that is extended.
        If None, use app.config["MDFORM_EXTENDS"] which is "form.html" by default.
    data : dict or None
        A dictionary that contains the data from to be shown in the
        form.
        If None, the data will be shown as empty.
    read_only : bool
        If true, the folder will be rendered as read-only.
    formatter : callable
        That format variable name and dict to string.
    on_submit : callable or None
        Functional that will be called upon form submission.
    flash_form_errors : bool
        Call flash errors for a given form. (default: True)

    Returns
    -------
    Return a rendered form.
    """

    meta, tmpl_str, Form = in_app_from_mdfile(
        mdfile, read_only=read_only, block=block, extends=extends, formatter=formatter
    )

    if data is None:
        form = Form()
    else:
        form = Form.from_plain_dict(data)

    if form.validate_on_submit():
        try:
            return on_submit(form, **request.view_args)
        except NotImplementedError:
            meta, tmpl_str, Form = in_app_from_mdfile(
                mdfile,
                read_only=True,
                block=block,
                extends=extends,
                formatter=formatter,
            )
            form = Form.from_plain_dict(form.to_plain_dict())
            return current_app.jinja_env.from_string(tmpl_str).render(
                form=form, meta=meta
            )

    if flash_form_errors:
        _flash_form_errors(form)

    return current_app.jinja_env.from_string(tmpl_str).render(form=form, meta=meta)


def on_get_form(
    mdfile=None,
    read_only=False,
    block=None,
    extends=None,
    formatter=None,
    flash_form_errors=True,
):
    """Flask decorator for app routes that renders a form,
    calling then wrapped function on successful form submission.

    Parameters
    ----------
    mdfile : str
        Filename of the markdown file (without .md extension)
        The file is loaded from the flask template folder.
    read_only : bool
        If true, the folder will be rendered as read-only.
    block :  str
        Name of the block where the form is inserted.
    extends : str
        Name of the template that is extended.
    formatter : callable
        That format variable name and dict to string.
    flash_form_errors : bool
        Call flash errors. (default: True)
    """

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):

            nonlocal mdfile

            mdfile = mdfile or in_app_get_mdfile()

            return render_mdform(
                mdfile,
                read_only=read_only,
                block=block,
                extends=extends,
                formatter=formatter,
                data=f(**request.view_args),
                on_submit=None,
                flash_form_errors=flash_form_errors,
            )

        return decorated_function

    return decorator


def on_submit_form(
    mdfile=None,
    read_only=False,
    block=None,
    extends=None,
    formatter=None,
    flash_form_errors=True,
):
    """Flask decorator for app routes that renders a form,
    calling then wrapped function on successful form submission.

    Parameters
    ----------
    mdfile : str
        Filename of the markdown file (without .md extension)
        The file is loaded from the flask template folder.
    read_only : bool
        If true, the folder will be rendered as read-only.
    block :  str
        Name of the block where the form is inserted.
    extends : str
        Name of the template that is extended.
    formatter : callable
        That format variable name and dict to string.
    flash_form_errors : bool
        Call flash errors. (default: True)
    """

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):

            nonlocal mdfile

            mdfile = mdfile or in_app_get_mdfile()

            return render_mdform(
                mdfile,
                read_only=read_only,
                block=block,
                extends=extends,
                formatter=formatter,
                data=None,
                on_submit=f,
                flash_form_errors=flash_form_errors,
            )

        return decorated_function

    return decorator
