.. image:: https://img.shields.io/pypi/v/flask-mdform.svg
    :target: https://pypi.python.org/pypi/flask-mdform
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/flask-mdform.svg
    :target: https://pypi.python.org/pypi/flask-mdform
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/flask-mdform.svg
    :target: https://pypi.python.org/pypi/flask-mdform
    :alt: Python Versions

.. image:: https://travis-ci.org/hgrecco/flask-mdform.svg?branch=master
    :target: https://travis-ci.org/hgrecco/flask-mdform
    :alt: CI

.. image:: https://coveralls.io/repos/github/hgrecco/flask-mdform/badge.svg?branch=master
    :target: https://coveralls.io/github/hgrecco/flask-mdform?branch=master
    :alt: Coverage



flask-mdform
============

An extension for Flask_ to generate `Flask-WTF`_ parsing Markdown
based document using mdforms_. Checkout the syntax in the mdform
page.


Installation
------------

.. code-block::

    pip install flask-mdform

Usage
-----

Use it like this to create a `WTForm`_ compatible template:

.. code-block::python

    >>> from flask_mdform import Markdown, FormExtension, flask_wtf
    >>> md = Markdown(extensions = [FormExtension(formatter=flask_wtf)])
    >>> html = md.convert(text)  # this is the jinja template with Flask WTForm
    >>> form_dict = md.Form      # this is the definition dict

or use it like this to create a `WTForm`_ compatible template that uses Bootstrap4_.

    >>> from flask_mdform import Markdown, FormExtension, flask_wtf_bs4
    >>> md = Markdown(extensions = [FormExtension(formatter=flask_wtf_bs4("jQuery", "wtf."))])
    >>> html = md.convert(text)  # this is the jinja template with Flask WTForm and BS4
    >>> form_dict = md.Form      # this is the definition dict

Here, the two arguments in the formatter can be use it to customize it. "jQuery" is the name
of the jQuery variable, "wtf." is the prefix where WTForm bootstrap **form_field** function
is located.

Other functions
---------------

**use_mdform**: decorator to be used in a flask route to parse, display, load and
store form and its values.

**form_to_dict**: iterates through a filled form and returns a dictionary
with the values in a json compatible format.

**dict_to_formdict**: iterates through a dict, parsing each value using the
spec defined in form_cls.

**from_mdfile**: generates form metadata, template, form from markdown file.

**from_mdstr**: generates form metadata, template, form from markdown string.

See AUTHORS_ for a list of the maintainers.

To review an ordered list of notable changes for each version of a project,
see CHANGES_


.. _Flask: https://github.com/pallets/flask
.. _`Flask-WTF`: https://github.com/lepture/flask-wtf
.. _mdforms: https://github.com/hgrecco/mdform
.. _`AUTHORS`: https://github.com/hgrecco/flask-mdform/blob/master/AUTHORS
.. _`CHANGES`: https://github.com/hgrecco/flask-mdform/blob/master/CHANGES
.. _`WTForm`: https://wtforms.readthedocs.io/
.. _Bootstrap4: https://pypi.org/project/Flask-Bootstrap4/