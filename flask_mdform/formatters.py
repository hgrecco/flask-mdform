"""
    flask_mdform.formatters
    ~~~~~~~~~~~~~~~~~~~~~~~

    Field formatters for different.

    :copyright: 2021 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations


def flask_wtf_bs4(jquery_var="jQuery", wtf_prefix="wtf."):
    """Formatter that use flask, WTF and Bootstrap4

    Parameters
    ----------
    jquery_var : str
        Name of the jQuery variable

    Returns
    -------
    callable (str, dict) -> str
    """

    def _inner(variable_name, field):
        args = ["form.%s" % variable_name]
        args.append("form_type='horizontal'")

        tag_class = ["form-control"]
        if field.is_label_hidden:
            tag_class.append("nolabel")

        collapse_on = getattr(field.specific_field, "collapse_on", None)
        if collapse_on:
            if collapse_on.startswith("~"):
                collapse_on = collapse_on[1:]
                comparator = "==="
            else:
                comparator = "!=="

            tag_class.append("collapser")

            if jquery_var:
                args.append(
                    f"""onchange="{jquery_var}('#accordion-{variable_name}').toggle({jquery_var}(this).val() {comparator} '{collapse_on}');" """
                )

        args.append('class="%s"' % " ".join("%s" % c for c in tag_class))

        length = getattr(field.specific_field, "length", None)
        if length:
            args.append("maxlength=%d" % length)

        return "{{ %sform_field(%s) }}" % (wtf_prefix, ", ".join(args))

    return _inner


def flask_wtf(variable_name, field):
    """Formatter that use"""
    return "{{ form.%s.label }} {{ form.%s }}" % (variable_name, variable_name)
