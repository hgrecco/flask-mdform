"""
    flask_mdform.deco
    ~~~~~~~~~~~~~~~~~

    Flask decorators and other utils to use inside a flask app.

    :copyright: 2021 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import functools

from flask import current_app, flash, request

from . import formatters
from .forms import from_mdstr

CONFIG_PREFIX = "MDFORM_"

CLASS_NAME = CONFIG_PREFIX + "CLASS_NAME"
BLOCK = CONFIG_PREFIX + "BLOCK"
EXTENDS = CONFIG_PREFIX + "EXTENDS"
FORMATTER = CONFIG_PREFIX + "FORMATTER"
TMPL_CONTEXT = CONFIG_PREFIX + "TMPL_CONTEXT"
EXTENSIONS = CONFIG_PREFIX + "EXTENSIONS"

BLOCK_PAGE = CONFIG_PREFIX + "BLOCK_PAGE"
EXTENDS_PAGE = CONFIG_PREFIX + "EXTENDS_PAGE"

DEFAULTS = {
    CLASS_NAME: "MDForm",
    EXTENDS: "form.html",
    BLOCK: "innerform",
    FORMATTER: formatters.flask_wtf,
    TMPL_CONTEXT: dict(),
    EXTENSIONS: [],
    EXTENDS_PAGE: "simple.html",
    BLOCK_PAGE: "inner_simple",
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
    formatter=None,
    extensions=None,
    config_suffix="",
):
    """A cached version of `from_mdfile` that must be used within an flask app."""
    mdfile_name = mdfile + ".md"

    class_name = class_name or in_app_get_config(CLASS_NAME)
    formatter = formatter or in_app_get_config(FORMATTER)
    extensions = extensions or in_app_get_config(EXTENSIONS)

    block = block or in_app_get_config(BLOCK + config_suffix)
    extends = extends or in_app_get_config(EXTENDS + config_suffix)

    if callable(class_name):
        class_name = class_name(mdfile)

    source, _, _ = current_app.jinja_loader.get_source(
        current_app.jinja_env, f"md/{mdfile_name}"
    )

    return from_mdstr(
        source,
        class_name=class_name,
        read_only=read_only,
        block=block,
        extends=extends,
        formatter=formatter,
        extensions=extensions,
    )


def render_mdpage(
    mdfile=None,
    *,
    block=None,
    extends=None,
    tmpl_context=None,
):
    """Renders an md page with flask (with or without data)

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
    tmpl_context : dict or None
        the variables that should be available in the context of the template.

    Returns
    -------
    Return a rendered form.
    """

    tmpl_context = tmpl_context or {}

    meta, tmpl_str, Form = in_app_from_mdfile(
        mdfile, block=block, extends=extends, config_suffix="_PAGE"
    )

    if Form._mdform_def:
        raise ValueError("Cannot use render_mdpage if the template contains a form.")

    cfg_tmpl_context = in_app_get_config(TMPL_CONTEXT)
    if cfg_tmpl_context:
        tmpl_context = {**cfg_tmpl_context, **tmpl_context}

    return current_app.jinja_env.from_string(tmpl_str).render(meta=meta, **tmpl_context)


def render_mdform(
    mdfile=None,
    *,
    read_only=False,
    block=None,
    extends=None,
    formatter=None,
    data=None,
    on_submit=None,
    flash_form_errors=None,
    tmpl_context=None,
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
    flash_form_errors : bool or callable
        Call flash errors for a given form. (default: True)
        Alternatively, a callable that takes a `flask_wtf.FlaskForm` form object
        and calls `flask.flash` can be used to customize the error message.
    tmpl_context : dict or None
        the variables that should be available in the context of the template.

    Returns
    -------
    Return a rendered form.
    """

    tmpl_context = tmpl_context or {}

    for key in ("form", "meta"):
        if key in tmpl_context:
            raise ValueError(
                f"'{key}' cannot be a key in the `tmpl_context` dict as it is reserved by flask-mdform"
            )

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

    if callable(flash_form_errors):
        flash_form_errors(form)
    elif flash_form_errors:
        _flash_form_errors(form)

    cfg_tmpl_context = in_app_get_config(TMPL_CONTEXT)
    if cfg_tmpl_context:
        tmpl_context = {**cfg_tmpl_context, **tmpl_context}

    return current_app.jinja_env.from_string(tmpl_str).render(
        form=form, meta=meta, **tmpl_context
    )


def on_get_page(
    mdfile=None,
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
    block :  str or None
        Name of the block where the form is inserted.
        If None, use app.config["MDFORM_BLOCK"] which is "innerform" by default.
    extends : str or None
        Name of the template that is extended.
        If None, use app.config["MDFORM_EXTENDS"] which is "form.html" by default.
    formatter : callable
        That format variable name and dict to string.
    flash_form_errors : bool or callable
        Call flash errors for a given form. (default: True)
        Alternatively, a callable that takes a `flask_wtf.FlaskForm` form object
        and calls `flask.flash` can be used to customize the error message.
    """

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):

            nonlocal mdfile

            mdfile = mdfile or in_app_get_mdfile()

            tmpl_context = f(**request.view_args)

            return render_mdpage(
                mdfile,
                block=block,
                extends=extends,
                tmpl_context=tmpl_context,
            )

        return decorated_function

    return decorator


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
    block :  str or None
        Name of the block where the form is inserted.
        If None, use app.config["MDFORM_BLOCK"] which is "innerform" by default.
    extends : str or None
        Name of the template that is extended.
        If None, use app.config["MDFORM_EXTENDS"] which is "form.html" by default.
    read_only : bool
        If true, the folder will be rendered as read-only.
    formatter : callable
        That format variable name and dict to string.
    flash_form_errors : bool or callable
        Call flash errors for a given form. (default: True)
        Alternatively, a callable that takes a `flask_wtf.FlaskForm` form object
        and calls `flask.flash` can be used to customize the error message.
    """

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):

            nonlocal mdfile

            mdfile = mdfile or in_app_get_mdfile()

            data = f(**request.view_args)

            if isinstance(data, tuple):
                data, tmpl_context = data
            else:
                tmpl_context = dict()

            return render_mdform(
                mdfile,
                read_only=read_only,
                block=block,
                extends=extends,
                formatter=formatter,
                data=data,
                on_submit=None,
                flash_form_errors=flash_form_errors,
                tmpl_context=tmpl_context,
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
    block :  str or None
        Name of the block where the form is inserted.
        If None, use app.config["MDFORM_BLOCK"] which is "innerform" by default.
    extends : str or None
        Name of the template that is extended.
        If None, use app.config["MDFORM_EXTENDS"] which is "form.html" by default.
    read_only : bool
        If true, the folder will be rendered as read-only.
    formatter : callable
        That format variable name and dict to string.
    flash_form_errors : bool or callable
        Call flash errors for a given form. (default: True)
        Alternatively, a callable that takes a `flask_wtf.FlaskForm` form object
        and calls `flask.flash` can be used to customize the error message.
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
