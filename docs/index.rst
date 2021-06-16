.. Molar documentation master file, created by
   sphinx-quickstart on Mon Jun 24 11:16:54 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

*********
Overview
*********

Molar (for Molecule Library) is a database management system for PostgreSQL. Its main focus is to enable chemists and material scientists to store the results of their experiment, whether computational or not!

It consists of a REST API implemented (using `FastAPI <https://fastapi.tiangolo.com/>`_) and a python client. Its main features are:

 - Creation/deletion of database on user request.
 - User management *per database* (using JWT tokens and OAuth2)
 - Event sourcing to be sure not to lose any data
 - Client integrated with `PyData's pandas <https://pandas.pydata.org>`_
 - Support to have different database structure, thanks to `Alembic <https://alembic.sqlalchemy.org/en/latest/>`_
 - Ease of deployment (Deployed in 2 command lines!).


.. toctree::
   :maxdepth: 0
   :caption: Contents:
   
   02_client_usage.ipynb
   03_backend_usage.ipynb
   04_client_api.rst
