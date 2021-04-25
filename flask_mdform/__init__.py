"""
    flask_mdform
    ~~~~~~~~~~~~

    Decorator for flask route.

    :copyright: 2020 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from .deco import use_mdform
from .formatters import flask_wtf, flask_wtf_bs4
from .forms import from_mdfile, from_mdstr

__all__ = ["use_mdform", "from_mdfile", "from_mdstr", "flask_wtf", "flask_wtf_bs4"]
