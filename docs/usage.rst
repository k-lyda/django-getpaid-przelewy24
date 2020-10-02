=====
Usage
=====

To use Getpaid-Przelewy24 in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'getpaid_przelewy24.apps.GetpaidPrzelewy24Config',
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
