django_multitenant_sockets
================

**django_multitenant_sockets** is a set of Django model and Rest_Framework serializer fields that encrypt upon deserialization and decrypt upon serialization so that the fields are stored encrypted in the underlying database.

Features
--------

- A simplified interface for interacting with keyczar's crypter for symmetric crypting.
- An extension to `rest_framework's <http://www.django-rest-framework.org/>`_ charfield that encrypts before deserialization and decrypts when serializing. When used with a `ModelSerializer <http://www.django-rest-framework.org/api-guide/serializers/#modelserializer>`_, the field is stored in the database encrypted.
- A simplified interface for generating a symmmetric key string that can be saved in a database. 


Installing
------------

You can install django_rest_cryptingfields at the command line with the following command:

    $ pip install -e git+https://github.com/russellmorley/django_rest_cryptingfields#egg=django_rest_cryptingfields

or by adding the following line to your requirement.txt:

    --e git+https://github.com/russellmorley/django_rest_cryptingfields#django_rest_cryptingfields

Check the `CHANGES <https://github.com/russellmorley/django_rest_cryptingfields/blob/master/CHANGES>`_
before installing.


Getting Started
-----------


Documentation
-----------

For complete documentation see `Django Save Logger <http://django_rest_cryptingfields.readthedocs.org>`_.

Testing
------------

Run tests by first setting the database ROLE and PASSWORD in tests/test_settings.py then executing the following command:

    $./runtests.py

Contributing
------------

Bug reports, bug fixes, and new features are always welcome. Please raise issues on the
`django_rest_cryptingfields project site <https://github.com/russellmorley/django_rest_cryptingfields>`_, and submit
pull requests for any new code.

    
More information
----------------

The django_rest_cryptingfields project was developed by Russell Morley. You can get the code
from the `django_rest_cryptingfields project site <https://github.com/russellmorley/django_rest_cryptingfields>`_.
    
-  `Website <http://www.compass-point.net/>`_
