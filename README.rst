.. image:: https://img.shields.io/pypi/v/flask-mdform.svg
    :target: https://pypi.python.org/pypi/flask-mdform
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/flask-mdform.svg
    :target: https://pypi.python.org/pypi/flask-mdform
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/flask-mdform.svg
    :target: https://pypi.python.org/pypi/flask-mdform
    :alt: Python Versions

.. image:: https://github.com/hgrecco/flask-mdform/workflows/CI/badge.svg
    :target: https://github.com/hgrecco/flask-mdform/actions?query=workflow%3ACI
    :alt: CI

.. image:: https://github.com/hgrecco/flask-mdform/workflows/Lint/badge.svg
    :target: https://github.com/hgrecco/flask-mdform/actions?query=workflow%3ALint
    :alt: LINTER


.. image:: https://coveralls.io/repos/github/hgrecco/flask-mdform/badge.svg?branch=main
    :target: https://coveralls.io/github/hgrecco/flask-mdform?branch=main
    :alt: Coverage



flask-mdform
============

If you arrive here, you probably know mdform_. If not, briefly it allows
you to write a form in an easy-to-read plain text format that can be
parsed to produce a fully functional form. You can checkout
its expressive syntax in the mdform_ repo.

Flask-mdform brings this power to Flask_ by providing functions and
decorators to generate `Flask-WTF`_ forms within your app.


Installation
------------

.. code-block::

    pip install flask-mdform

Usage
-----

Just put your markdwn form files in **templates/md/**, for example your **personal.md**

.. code-block:: markdown

    name* = ___
    age* = ###

and then add the ``on_get_form`` decorator to your route.

.. code-block:: python

    @app.route("/by_endpoint", methods=["GET"])
    @on_get_form()
    def personal():
        """As the endpoint is named `personal`, flask-mdform
        will load, parse and display:

            templates/md/personal.md

        This function should return a dictionary
        that maps form labels to the values to show.

        (missing values in the dict will just leave
        the form field as is)
        """
        return dict(name="John", age=42)

If you want to set the name of the form file independently of the endpoint
just use the ``mdfile`` keyword argument:

.. code-block:: python

    @app.route("/by_arg", methods=["GET"])
    @on_get_form(mdfile="personal")
    def by_arg():
        """This will also load, parse and display:

            templates/md/personal.md
        """
        return dict(name="John", age=42)


To handle the form submission, use the ``on_submit_form`` decorator.

.. code-block:: python

    @app.route("/submit", methods=["POST"])
    @on_submit_form(mdfile="personal")
    def submit(form):
        """This will get the form definition from:

            templates/md/personal.md

        The argument `form` is contains the filled form after validation.

        Use `form.to_plain_dict()` to obtain a dictionary mapping label names
        to values.

        By the way, you can can call `Form.from_plain_dict(values)` to fill
        obtain a filled form object from Form class.

        This function should return the webpage to show after. Any flask
        response will work (a string, rendering a template, a redirect, etc).
        """

        # If you have a save function, you can:
        #   save(form.to_plain_dict())
        return "Thanks for submitting!"

If you just want to render a read-only version of the form with the submitted
data, just raise ``NotImplementedError``

.. code-block:: python

    @app.route("/submit", methods=["POST"])
    @on_submit_form(mdfile="personal")
    def submit(form):
        # If you have a save function, you can:
        #   save(form.to_plain_dict())
        raise NotImplementedError


In certain cases, you might want load a form depending on the route. Just provide a
route argument named ``mdfile``.

.. code-block:: python

        @app.route("/form/<mdfile>", methods=["GET"])
        @on_get_form()
        def by_view_arg(mdfile):
            return dict(name="John", age=42)

this will return the **templates/md/personal.md** if you navigate to */form/personal*.


Customizing decorators
----------------------

Arguments of these decorators (``on_get_form`` and ``on_submit_form``) can
be used to customize the output:

- **mdfile**: (str) Allows you to customize the mdform file name, do not use
  the extension here.
  All files will be looked in **templates/md/** folder and should have the
  extension ``.md``  (Default: ``None``, which means that  defaults first to ``mdform`
  view argument or then to `endpoint`)
- **read_only**: (bool) If True, the form will be displayed as non-editable readonly
  form.
  (Default: False)
- **block**: (str) Name of the Jinja_ block where the form will be inserted.
  (Default: None, which means it should use the config value in `MDFORM_BLOCK`)
- **extends**: (str) Name of the Jinja_ template to use.
  (Default: None, which means it should use the config value in `MDFORM_EXTENDS`)
- **formatter**: (callable) Function to write a field to a template. mdform_
  (Default: None, which means it should use the config value in `MDFORM_FORMATTER`)
- **flash_form_errors**: (bool) If True, calls FlashError_ for the form arguments.
  Showing the errors must be called in the template.
  (Default: True)


Configuration Handling
----------------------

Flask allows to write application wide configurations. `Flask-mdforms` has the following
keys and values by default:

.. code-block:: python

    MDFORM_EXTENDS = "form.html"
    MDFORM_BLOCK = "innerform"
    MDFORM_FORMATTER = formatters.flask_wtf


(A little) lower level
----------------------

In certain cases you want to handle your the routes yourself. The function
**render_mdform** is analogous to the Flask ``render_template`` but it allows
you to show and mdform. Ito has the same arguments as ``on_get_form`` and
``on_submit_form`` with two additional arguments

- **data**: (dict) mapping from labels to values to fill the form with.
- **on_submit**: (callable) function to be called upon submission.
  Arguments are ``on_submit(form, **request.view_args)`` and should
  return the page to show.

Finally, you can check some simple demonstrations in the the **examples** for folder.


Enjoy!

----

See AUTHORS_ for a list of the maintainers.

To review an ordered list of notable changes for each version of a project,
see CHANGES_

.. _Flask: https://github.com/pallets/flask
.. _`Flask-WTF`: https://github.com/lepture/flask-wtf
.. _mdform: https://github.com/hgrecco/mdform
.. _`AUTHORS`: https://github.com/hgrecco/flask-mdform/blob/master/AUTHORS
.. _`CHANGES`: https://github.com/hgrecco/flask-mdform/blob/master/CHANGES
.. _`WTForm`: https://wtforms.readthedocs.io/
.. _Bootstrap4: https://pypi.org/project/Flask-Bootstrap4/
.. _FlashError: https://flask.palletsprojects.com/en/2.0.x/patterns/flashing/
.. _Jinja: https://jinja.palletsprojects.com/