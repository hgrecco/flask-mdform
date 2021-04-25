"""
    flask_mdform
    ~~~~~~~~~~~~

    Decorator for flask route.

    :copyright: 2020 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from mdform import FormExtension, Markdown

from .deco import use_mdform
from .formatters import flask_wtf, flask_wtf_bs4
from .forms import dict_to_formdict, form_to_dict, from_mdfile, from_mdstr

__all__ = [
    "use_mdform",
    "from_mdfile",
    "from_mdstr",
    "flask_wtf",
    "flask_wtf_bs4",
    "form_to_dict",
    "dict_to_formdict",
    "FormExtension",
    "Markdown",
]
