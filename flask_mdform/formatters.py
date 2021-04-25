"""
    flask_mdform.formatters
    ~~~~~~~~~~~~~~~~~~~~~~~

    Generate a FlaskForm/WTForm from a Markdown based form.

    :copyright: 2020 by flask-mdform Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""


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

    def _inner(variable_name, variable_dict):
        args = ["form.%s" % variable_name]
        args.append("form_type='horizontal'")

        tag_class = ["form-control"]
        if variable_dict["nolabel"]:
            tag_class.append("nolabel")

        collapse_on = variable_dict.get("collapse_on")
        if collapse_on:
            if collapse_on.startswith("~"):
                collapse_on = collapse_on[1:]
                comparator = "==="
            else:
                comparator = "!=="

            tag_class.append("collapser")

            if jquery_var:
                args.append(
                    f""" onchange="{jquery_var}('#accordion-{variable_name}').toggle({jquery_var}(this).val() {comparator} '{collapse_on}');" """
                )

        args.append('class="%s"' % " ".join("%s" % c for c in tag_class))

        if variable_dict.get("length") is not None:
            args.append("maxlength=%d" % variable_dict["length"])

        return "{{ %sform_field(%s) }}" % (wtf_prefix, ", ".join(args))

    return _inner


def flask_wtf(variable_name, variable_dict):
    """Formatter that use"""
    return "{{ form.%s.label }} {{ form.%s }}" % (variable_name, variable_name)
