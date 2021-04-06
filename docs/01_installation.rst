Installation
============


Installing the python client
----------------------------

You can check out the latest version from gitlab and install it through the following command line:

.. code-block:: bash

    $ git clone git@gitlab.com:tgaudin/goldmine.git
    $ cd goldmine && pip install -e .

Alternatively you can download the code on `gitlab <https://gitlab.com/tgaudin/goldmine/>`_ directly.


Installing the backend
----------------------

You will need a running `PostgreSQL <https://www.postgresql.org>`_ server to install the database. You can choose to run a database locally, or choose a cloud provider that proposes managed database (`IBM Cloud <https://www.ibm.com/cloud/databases-for-postgresql>`_, `DigitalOcean <https://www.digitalocean.com/products/managed-databases/>`_, `Azure <https://azure.microsoft.com/en-us/services/postgresql/>`_, `ElephantSQL <https://www.elephantsql.com/>`_ to name a few).


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


