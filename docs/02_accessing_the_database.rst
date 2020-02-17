Accessing the database
======================

The machine running the database is physically hosted by scinet.utoronto.ca, but it can also be access through a machine in the matterlab's network.

So there are 3 different cases:
    1. You are in the matterlab's network (either you are connected to a blue ethernet cable or to the compsci wifi)
    2. You are in scinet's network (running a calculation for instance)
    3. You do not have access to neither scinet or the matterlab networks.


From the matterlab's network
----------------------------

A relay has been installed in the matterlab's network, so you can access the database through ``mdb.matter.sandbox`` without having to run an SSH tunnel.

.. code-block:: python

    from mdb import MDBClient

    client = MDBClient(hostname='mdb.matter.sandbox', 
                       username='your_username', 
                       password='your_password',
                       database='database_name')
    ...
    


From scinet.utoronto.ca
-----------------------

Scinet is hosting the machine where the database is installed. Thus you can directly use it from the cluster (for instance to send directly your data after calculation).

Its hostname is ``nrcdb``.

.. code-block:: python

    from mdb import MDBClient

    client = MDBClient(hostname='nrcdb', 
                       username='your_username', 
                       password='your_password',
                       database='database_name')
    ...

From elsewhere
--------------

If you are neither in the matterlab or scinet's network, you need to create a client with an ssh tunnel.


.. code-block:: python
    client = MDBClientWithSSH(hostname='10.21.101.51',
                              username='postgres',
                              password='',
                              database='madness',
                              ssh_hostname='cs.toronto.edu',
                              ssh_username='aagdbvis@cs.toronto.edu',
                              ssh_keyfile='path/to/the/ssh/key')


Using a configuration file
--------------------------

Alternatively it is possible to use a config file. It is probably the most convenient way to store credentials and use the client.

Here is an example of configuration file:

.. code-block:: toml

    use_tqdm = true
    use_ssh = true

    [database]
    hostname = 'db_host'
    database = 'db_name'
    username = 'db_user'
    password = 'db_pass'

    [ssh]
    hostname = 'ssh_hostname'
    username = 'ssh_username'
    keyfile = '/path/to/keys/id_ed25519'
    proxy_cmd = ''


If you access the database locally (through ``mdb.matterlab.sandbox`` or ``nrcdb`` you should set ``use_ssh`` to false.

And how to use this file:

.. code-block:: python

    import mdb

    client = mdb.load_client_from_config('path/to/config_file.conf')
    

