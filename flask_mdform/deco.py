import functools
import os

from flask import current_app, flash, request

from .forms import from_mdfile


def flash_errors(form):
    """Flashes form errors
    """
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                "Error in the %s field - %s" % (getattr(form, field).label.text, error),
                "danger",
            )


def render_mdform(
    mdfile=None, block="innerform", extends="form.html", data=None, read_only=False
):

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


def mdform(
    mdfile=None,
    block="innerform",
    extends="form.html",
    data_loader=None,
    read_only=False,
):
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
