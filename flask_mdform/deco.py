"""
    flask_mdform.deco
    ~~~~~~~~~~~~~~~~~

    Render markdown forms using mdforms, Flask, Flask-WTF, WTForms, Jinja2

    :copyright: 2020 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import functools
import os

from flask import current_app, flash, request

from .forms import from_mdfile


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                "Error in the %s field - %s" % (getattr(form, field).label.text, error),
                "danger",
            )


def render_mdform(
    mdfile=None, block="innerform", extends="form.html", data=None, read_only=False
):
    """

    Parameters
    ----------
    mdfile : str
        Filename of the markdown file (without .md extension)
        The file is loaded from the flask template folder.
    block :  str
        Name of the block where the form is inserted.
    extends : str
        Name of the template that is extended.
    data : dict
        A dictionary that contains the data from to be shown in the
        form. If None, the data will be shown as empty.
    read_only : bool
        If true, the folder will be rendered as read-only.

    Returns
    -------
    Return a rendered form.
    """

    mdfile_name = os.path.join(
        current_app.root_path, current_app.template_folder, "md", mdfile
    )

    meta, tmpl_str, Form = from_mdfile(
        mdfile=mdfile_name, read_only=read_only, block=block, extends=extends
    )

    if data is None:
        form = Form()
    else:
        form = Form.from_plain_dict(data)

    return current_app.jinja_env.from_string(tmpl_str).render(form=form)


def use_mdform(
    mdfile=None,
    block="innerform",
    extends="form.html",
    data_loader=None,
    read_only=False,
):
    """

    Parameters
    ----------
    mdfile : str
        Filename of the markdown file (without .md extension)
        The file is loaded from the flask template folder.
    block :  str
        Name of the block where the form is inserted.
    extends : str
        Name of the template that is extended.
    data_loader : callable
        Function to load the data from a datasource.
        it should return a dict.
        If None, no data will be loaded and the form will be loaded
        as empty.
    read_only : bool
        If true, the folder will be rendered as read-only.

    Returns
    -------

    """

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):

            mdfile_name = mdfile
            if mdfile_name is None:
                mdfile_name = request.endpoint.replace(".", "/") + ".md"

            mdfile_name = os.path.join(
                current_app.root_path, current_app.template_folder, "md", mdfile_name
            )

            meta, tmpl_str, Form = from_mdfile(
                mdfile=mdfile_name, block=block, extends=extends, read_only=read_only
            )

            if data_loader is not None:
                form = Form.from_plain_dict(data_loader(*args, **kwargs))
            else:
                form = Form()

            if form.validate_on_submit():
                ctx = f(form, *args, **kwargs)
                if ctx is None:
                    ctx = {}
                elif not isinstance(ctx, dict):
                    return ctx

            flash_errors(form)
            return current_app.jinja_env.from_string(tmpl_str).render(form=form)

        return decorated_function

    return decorator
