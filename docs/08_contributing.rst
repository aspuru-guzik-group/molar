Contributing
============

Contributions are welcome! If you add new featues please add tests.


Running the tests
-----------------

There are two level of tests. One on the backend and one on the client.

The test on the backend rely on `pgtap <https://pgtap.org/>`_ and can be run using `pg_prove`:

.. code-block:: shell

    $ pg_prove --dbname mdb pgsql/tests/test_eventsourcing.sql -h localhost -U postgres


The test on the client uses `pytest <https://docs.pytest.org/en/latest/>`_.

To run them:

.. code-block:: shell

    $ python setup.py test
