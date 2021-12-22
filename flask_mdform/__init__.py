"""
    flask_mdform
    ~~~~~~~~~~~~

    Decorator for flask route.

    :copyright: 2021 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from mdform import FormExtension, Markdown

from .deco import on_get_form, on_submit_form, render_mdform
from .formatters import flask_wtf, flask_wtf_bs4
from .forms import filled_form_to_content, from_mdfile, from_mdstr, generate_form_kwargs

__all__ = [
    "on_get_form",
    "on_submit_form",
    "render_mdform",
    "from_mdfile",
    "from_mdstr",
    "flask_wtf",
    "flask_wtf_bs4",
    "filled_form_to_content",
    "generate_form_kwargs",
    "FormExtension",
    "Markdown",
]
