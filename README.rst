=============================
Getpaid-Przelewy24
=============================

.. image:: https://badge.fury.io/py/django-getpaid-przelewy24.svg
    :target: https://badge.fury.io/py/django-getpaid-przelewy24

.. image:: https://travis-ci.org/k-lyda/django-getpaid-przelewy24.svg?branch=master
    :target: https://travis-ci.org/k-lyda/django-getpaid-przelewy24

.. image:: https://codecov.io/gh/k-lyda/django-getpaid-przelewy24/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/k-lyda/django-getpaid-przelewy24

django-getpaid processor for Przelewy24

Documentation
-------------

The full documentation is at https://django-getpaid-przelewy24.readthedocs.io.

Quickstart
----------

Install Getpaid-Przelewy24::

    pip install django-getpaid-przelewy24

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        "getpaid",
        "getpaid_przelewy24.apps.GetpaidPrzelewy24Config",
        ...
    )

Add Getpaid-Przelewy24's URL patterns:

.. code-block:: python

    from getpaid_przelewy24 import urls as getpaid_przelewy24_urls


    urlpatterns = [
        ...
        url(r'^', include(getpaid_przelewy24_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
