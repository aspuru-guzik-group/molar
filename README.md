![test](https://gitlab.com/tgaudin/goldmine/badges/master/pipeline.svg) ![coverage](https://gitlab.com/tgaudin/goldmine/badges/master/coverage.svg)

# Madness DB

Madness DB is a database meant to hold all data created by the madness project.

This repo contains the code of the python client and all the backend-side code.
Here is an overview of how it's organized:


```
├── docs                    -- documentation src dir
├── mdb                     -- client source code
├── migrations              -- database migration code (alembic base dir)
├── pgsql                   -- code for the database
├── tests                   -- unit test for the client
├── README.md               -- this file
├── docker-compose.yml      -- to spin up the db locally
├── setup.cfg
└── setup.py
```

## Installing the client

If you have git and python installed, it's as easy as:

```bash
$ git clone git@gitlab.com:tgaudin/goldmine.git
$ cd goldmine && pip install -e .
```

## Using the client

A more complete documentation is available [here](http://www.cs.toronto.edu/~tgaudin/madnessdb/)
(user: `madness`, pw: `darpa-madness`)

If you are in the matterlab's network:

```python
from mdb import MDBClient

client = MDBClient(hostname='mdb.matter.sandbox', 
                   username='postgres', 
                   password='',
                   database='madness')

client.get('molecule')

```

If you are not in the matterlab's network

```python
from mdb import MDBClientWithSSH

client = MDBClientWithSSH(hostname='localhost',
                          username='postgres',
                          password='',
                          database='madness',
                          ssh_hostname='cs.toronto.edu',
                          ssh_username='username@cs.toronto.edu',
                          ssh_keyfile='path/to/the/ssh/key',
                          ssh_tunnel_hostname='mdb.matter.sandbox')

client.get('molecule')
```

Alternatively, if you have a config file you can just do:

```python
import mdb

client = mdb.load_client_from_config('path/to/config_file.conf')

client.get('molecule')
```

## Documentation

It's [here](http://www.cs.toronto.edu/~tgaudin/madnessdb/) (user: `madness`, pw:
`darpa-madness`)
