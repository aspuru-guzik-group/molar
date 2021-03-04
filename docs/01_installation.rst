Installation
============


Installing the python client
----------------------------

Linux, OS X, *BSD
^^^^^^^^^^^^^^^^^

If you have git installed on your computer you can just git clone.

.. code-block:: bash

    $ git clone git@gitlab.com:tgaudin/goldmine.git
    $ cd goldmine && pip install -e .

Alternatively you can download the code on `gitlab <https://gitlab.com/tgaudin/goldmine/>`_ directly.

Windows
^^^^^^^

TODO!


Installing the backend locally
------------------------------

Even though running the database locally is not necessary, it may be useful for developpment purpose.

Make sure to first install `psql <http://postgresguide.com/setup/install.html>`_, and some postgresql-client (the client version doesnt matter that much, see `here <postgresql-client>`_).


Using `docker-compose <https://docs.docker.com/compose/>`_ is a convenient way to run postgresql locally:

.. code-block:: bash

    $ git clone git@gitlab.com:tgaudin/goldmine.git
    $ cd goldmine && pip install -e .

    # Creating a folder for postgresql data
    $ mkdir -p data
    $ docker-compose up -d postgres
    # Then when postgres is ready:
    $ mdbcli admin create-db \
        -u postgres \
        -p '' \
        -h localhost \
        -d mdb \
        -s pgsql/structure.sql \
        -e pgsql/event_sourcing.sql \
        -c alembic.ini \
        --admin_pass '' \
        --user_pass ''
If the username and database name were not configured as above then the line ``sqlalchemy.url=`` in the ``alembic.ini`` file  must be changed accordingly.

This command creates a database named ``mdb``. More info about the command line tool can be found in the :ref:`command_line_interface` section.

.. note:: To test your install, try accessing the db with ``psql -U <user> -h <host> -d <db_name>``. Then maybe try running ``select * from public.lab;``.


