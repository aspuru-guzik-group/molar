# Molar 🦷

Molar is a database management system for PostgreSQL. Its main focus is to enable chemists and material scientist to store the results of their experiment, whether exprimental or not!

It consists of a REST API (implemented using FastAPI) and a python client. ITs main features are:

 - Creation / deletion of database o nuser request
 - User management per database (using JWT tokens and OAuth2)
 - Event sourcing to be sure not to lose any data
 - Client integrates with [PyData's pandas](https://pandas.pydata.org)
 - Support to have different database structure, thanks to [Alembic](https://alembic.sqlalchemy.org)
 - Easy to deploy (you just need 2 command lines, `using docker-compose`)

## Docs

[See on readthedocs](https://molar.readthedocs.io)


 ## Installation

You can install the package through PYPI.

 ```bash
  $ pip install molar
 ```

 If you want to install the backend, you will need extra dependancies.

 ```bash
  $ pip install molar[backend]
 ```

 Molar ships with a command line interface that makes it easy to deploy, all you need to do is (providing docker is already installed):

 ```bash
  $ molarcli install local
```
