"""
    flask_mdform
    ~~~~~~~~~~~~

    Decorator for flask route.

    :copyright: 2021 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import pkg_resources
from mdform import FormExtension, Markdown

from .deco import on_get_form, on_get_page, on_submit_form, render_mdform, render_mdpage
from .formatters import flask_wtf, flask_wtf_bs4
from .forms import filled_form_to_content, from_mdfile, from_mdstr, generate_form_kwargs

try:  # pragma: no cover
    __version__ = pkg_resources.get_distribution("flask-mdform").version
except Exception:  # pragma: no cover
    # we seem to have a local copy not installed without setuptools
    # so the reported version will be unknown
    __version__ = "unknown"


__all__ = [
    "on_get_form",
    "on_submit_form",
    "on_get_page",
    "render_mdpage",
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
