.. Goldmine documentation master file, created by
   sphinx-quickstart on Mon Jun 24 11:16:54 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

*********
MapleDB
*********

MapleDB is a database meant to store computational and experimental data coming from chemistry labs. It is designed with several goals in mind:

 * be resilient to data-loss, by implementing ``event sourcing`` which tracks all changes thus allowing to rollback the database at any point of time if needed,
 * facilitate data sharing among teams,
 * lower the "access barrier" to the database with a python client that has a tight integration with `PyData's pandas <https://pandas.pydata.org/>`_ 
 * grant users some flexibility in the structure by implementing part of the schema with `NewSQL <https://en.wikipedia.org/wiki/NewSQL>`_.

A typical usage of MapleDB is to be the cornerstone of any data intensive project at the interface between chemistry, machine learning and automation as illustrated by the following picture.

.. raw:: html
    :file: _images/data_framework.svg

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   01_installation
   02_accessing_the_database
   03_writing_data.ipynb
   04_reading_data.ipynb
   05_event_sourcing.ipynb
   06_schema
   07_client_api
   08_contributing
   09_admin_guide 
