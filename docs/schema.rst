SQL Schema
==========

All the code and material regarding the database can be found in the `pgsql` folder of the source code:

::

    pgsql
    ├── event_sourcing.sql  -- The implementation of the event sourcing
    ├── postgresql.conf     -- A configuration of postgresql that is a bit less minimal than the default one
    ├── setup.sh            -- Shell script to set up the event sourcing and the structure in the database
    └── structure.sql       -- Structure of the database

The structure looks like this:

.. image:: _static/schema.png
