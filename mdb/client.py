from functools import partial

import pandas as pd
from tqdm import tqdm
from sqlalchemy import and_
import psycopg2

from . import database
from . import mapper


class MDBClient(mapper.SchemaMapper):
    """
    MDBClient is a high-level client for the madness database. There is an
    emphasis on user-friendliness and a thight integration with pandas.

    :param hostname: database hostname (string)
    :param username: database username (string)
    :param password: database password (string)
    :param database_name: name of the database to access (string)
    :param use_tqdm: how a tqdm progressbar if set to True. (boolean, optional)

    """
    def __init__(self, hostname, username, password, database_name, use_tqdm=True):
        self.sql_url = f"postgresql://{username}:{password}@{hostname}/{database_name}"
        Session, engine, models = database.init_db(self.sql_url)
        self.session = Session()
        self.engine = engine
        self.models = models

        self.dao =  DataAccessObject(self.session, self.models)
        self.rollback = self.dao.rollback

        self.use_tqdm = use_tqdm

    def __del__(self):
        self.session.close()

    def get(self, table_name, return_df=True, filters=None, limit=None, offset=None):
        """
        This method allows to read data stored in the database.

        :param table_name: (str or List(str)) name(s) of the table(s) to access
        :param return_df: (bool) returns a pandas.DataFrame if True
        :param filters: (list) list of fitlers 
        :param limit: (int or None) limits how many rows should be loaded.
        :param offset: (int or None) indicates how many rows to skip.
        
        :returns: List of queried object of pandas.DataFrame containing the data

        Typical usage:        
       
        .. code-block:: python

            client = MDBCLient('localhost', 'postgres', '', 'madness')
            df = client.get('fragment')
            df.head()

        It is also possible to acces data from many tables at the same time, as
        long as they are related. For instance, in the here-below example, we
        are joining both table `fragment` and `molecule` and filter for a
        specific smiles.
        
        .. code-block:: python

            client = MDBCLient('localhost', 'postgres', '', 'madness')
            df = client.get(['fragment', 'molecule'],
                            filters=[client.models.Molecule.smiles == 'C1=CC=CC=C1'])
            df.head()
        
        """
        data = self.dao.get(table_name, filters, limit, offset)
        if not return_df:
            return data
        df = pd.DataFrame.from_records([d.__dict__ for d in data])
        if '_sa_instance_state' in df.columns:
            del df['_sa_instance_state']
        return df
    
    def get_uuid(self, table_name, **kwargs):
        """
        This method helps finding the uuid of a specific item in the database.
        it will be usefule when adding data with relationships.

        :param table_name (str): name of the table
        :param kwargs: keyword arguments which will be used to build filters. Those 
        keywords have to correspond to existing column in the table.

        :returns: The uuid as a string. If the objects can't be find, a
        exception is raised.

        .. code-block:: python
            
            client = MDBCLient('localhost', 'postgres', '', 'madness')
            molecule_uuid = client.get_uuid('molecule', smiles='C1=CC=CC=C1')

        """
        model = getattr(self.models, table_name)
        filters = []
        for k, v in kwargs.items():
            field = getattr(model, k)
            if field is None:
                raise ValueError(f'{table_name} has no column {k}!')
            filters.append(field == v)

        q = self.get(table_name, filters=filters, return_df=False, limit=1)
        if q is None:
            raise ValueError(f'No row with the specified filters where found.  Filters: {filters}')
        return q.uuid

    def add(self, table_name, data):
        """
        This method can add data to any existing table in the database. This
        method will returns the events created in the eventstore which contains
        some information about the object such as its uuid.

        :param table_name: name of the table (string)
        :param data: data to add (list, pandas.DataFrame or dict)

        Example:

        .. code-block:: python
            
            client = MDBCLient('localhost', 'postgres', '', 'madness')
            event = client.add('molecule', {'smiles': 'C1=CC=CC=C1'})
            print(event.uuid)
        
        """
        if isinstance(data, dict):
            data = [data]
        if isinstance(data, list):
            data = pd.DataFrame.from_records(data)
        if not isinstance(data, pd.DataFrame):
            raise NotImplementedError("Incorrect data types")

        iter = data.iterrows()
        if self.use_tqdm:
            iter = tqdm(iter, total=len(data))

        events = []
        for i, record in enumerate(iter):
            events.append(self.dao.add(table_name, record[1].to_dict()))
            if i % 500 == 0:
                self.session.commit()
        self.session.commit()
        return events

    def update(self, table_name, data, uuid=None):
        """
        This method serves to update specifics rows of a table.

        :table_name (str): name of the table
        :data (pandas.DataFrame, list or dict): data to update
        :uuid (str or list): if data does not contains the uuid, it must be specified.

        Example:

        .. code-block:: python
            
            client = MDBClient('localhost', 'postgres', '', 'madness')
            df = client.get('molecule')
            df.at[0, 'smiles'] = 'C#N'
            client.update('molecule', df)
            df = client.get('molecule')
            df.head()
        """
        if isinstance(data, dict):
            data = [data]
        if isinstance(data, list):
            data = pd.DataFrame.from_records(data, exclude=['id', 'updated_on', 'created_on'])
        if not isinstance(data, pd.DataFrame):
            raise TypeError("lol")

        if not uuid:
            uuid = data['uuid'].tolist()
            del data['uuid']
        
        if 'updated_on' in data:
            del data['updated_on']

        if 'created_on' in data:
            del data['created_on']

        iter = data.iterrows()
        if self.use_tqdm:
            iter = tqdm(iter)

        events = []
        for i, (record, id) in enumerate(zip(iter, uuid)):
            events.append(self.dao.update(table_name, record[1].to_dict(), id))
            if i % 500 == 0:
                self.session.commit()
        self.session.commit()
        return events

    def delete(self, table_name, uuid):
        """
        This method deletes data from the database.

        :table_name (str): name of the table
        :uuid (str, List(str)): uuid to remove

        .. code-block:: python
            
            client = MDBClient('localhost', 'postgres', '', 'madness')
            df = client.get('molecule')
            client.delete('molecule', df['uuid'].tolist())
            

        """
        if isinstance(uuid, str):
            uuid = [uuid]

        events = []
        for i, id in enumerate(uuid):
            events.append(self.dao.delete(table_name, id))
            if i % 500 == 0:
                self.session.commit()
        self.session.commit()
        return events

    def rollback(self, before):
        """
        Performs a rollback on the database. For now, it only supports to be
        restored to a prior date.

        :before (datetime.datetime): prior date.
        
        Example:

        .. code-block:: python
        
            from datetime import datetime
            client = MDBClient('localhost', 'postgres', '', 'madness')
            client.rollback(datetime(1980, 12, 25)
        """

        self.dao.rollback(before)


class DataAccessObject:
    """
    Data Access Object.

    Define the low level interactions between MDBClient and the database. It is
    not meant to be used on its own.

    :session: (sqlalchemy.orm.session.Session)
    :models: (sqlalchemy.orm.mapper)
    """
    def __init__(self, session, models):
        self.session = session
        self.models = models

    def get(self, table_name, filters=None, limit=None, offset=None):
        """
        Reads data from a table

        :table_name (str):
        :filters (list):
        :limit (int or None):
        :offset (int or None):
        """
        if not isinstance(table_name, list):
            table_name = [table_name]

        t = table_name.pop(0)
        model = getattr(self.models, t, None)
        assert model is not None, f'{t} does not correspond to any table!'

        query = self.session.query(model)

        for t in table_name:
            model = getattr(self.models, t, None)
            assert model is not None, f'{t} does not correspond to any table!'
            query = query.join(model)

        if filters:
            filter = True
            for f in filters:
                filter = and_(filter, f)
            query = query.filter(filter)
        
        if limit is None:
            return query.all()
        elif limit == 1:
            return query.one_or_none()

        if offset is not None:
            query = query.offset(offset)
        query = query.limit(limit)
        return query
        
    def add(self, table_name, data):
        """
        Add data to the database. This corresponds to a 'create' event on the
        eventstore with a 'type' of table_name

        Parameters:
        -----------

            * table_name
            * data
        """
        params = {'event': 'create',
                  'type': table_name,
                  'data': data}
        event = self.models.eventstore(**params)
        self.session.add(event)
        return event

    def delete(self, table_name, uuid):
        """
        Delete data from the databse. This corresponds to a 'delete' event on
        the eventstore with a 'type' of table_name

        Parameters:
        -----------

            * table_name
            * uuid
        """
        params = {'event': 'delete',
                  'type': table_name,
                  'uuid': uuid}
        event = self.models.eventstore(**params)
        self.session.add(event)
        return event

    def update(self, table_name, data, uuid):
        """
        Update data from the database. This corresponds to an 'update' event on
        the eventstore with a 'type' of table_name

        Parameters:
        -----------

            * table_name
            * data
            * uuid
        """
        params = {'event': 'update',
                  'type': table_name,
                  'data': data,
                  'uuid': uuid}
        event = self.models.eventstore(**params)
        self.session.add(event)
        return event

    def rollback(self, before):
        """
        Rollback the database. This corresponds to a 'rollback' event on the
        eventstore. For now, until rollback to a specific date is available.

        Parameters:
        -----------

            * before: (datetime.dateime)
        """

        params = {'event': 'rollback',
                  'data': {'before': before.isoformat()}}
        event = self.models.eventstore(**params)
        self.session.add(event)
        return event


class ArgumentsFetcher:
    def __init__(self, func, dao, convert_smiles, convert_synth_hid, convert_lab_short_name):
        self.func = func
        self.dao = dao
        
        self.subs_mapper = {}

        if convert_smiles:
            self.subs_mapper['fragment_uuid'] = partial(self.molecule_to_uuid, table_name='fragment')
            self.subs_mapper['molecule_uuid'] = partial(self.molecule_to_uuid, table_name='molecule')
            self.subs_mapper['targeted_molecule_uuid'] = partial(self.molecule_to_uuid, table_name='molecule')
        if convert_synth_hid:
            self.subs_mapper['synth_uuid'] = self.synth_hid_to_uuid
        if convert_lab_short_name:
            self.subs_mapper['lab_uuid'] = self.lab_short_name_to_uuid

    def __call__(self, *args, **kwargs):
        # Check kwargs
        for k, v in kwargs.items():
            if k in self.subs_mapper.keys():
                kwargs[k] = self.subs_mapper[k](self.dao, v)

        varnames = self.func.__code__.co_varnames
        
        new_args = []
        for v, a in zip(varnames, args):
            if v in self.subs_mapper.keys():
                a = self.subs_mapper[v](self.dao, a)
            new_args.append(a)

        return self.func(*new_args, **kwargs)

    @staticmethod
    def molecule_to_uuid(dao, smiles, table_name):
        # TODO: check if smiles is a uuid
        model = getattr(dao.models, table_name)
        res = dao.get(table_name, filters=[model.smiles == smiles])
        assert len(res) == 1
        if res is None:
            res = dao.add(table_name, {'smiles': smiles})
            dao.session.commit()
            return res.uuid
        return res[0].uuid

    @staticmethod
    def synth_hid_to_uuid(dao, synth_hid):
        res = dao.get('synthesis', filters=[dao.models.synthesis.synth_hid == synth_hid])
        assert len(res) == 1
        return res[0].uuid

    @staticmethod
    def lab_short_name_to_uuid(dao, lab_short_name):
        res = dao.get('lab', filters=[dao.models.lab.short_name == lab_short_name])
        assert len(res) == 1
        return res[0].uuid
