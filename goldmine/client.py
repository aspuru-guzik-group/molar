import pandas as pd
from tqdm import tqdm
from sqlalchemy import and_
import psycopg2

from . import database


class  GoldmineClient:
    """
    GoldmineClient is a client to connect to the database with an emphasis on
    user-friendliness and pandas integration where it is possible.

    Args:
        * hostname (str): hostname of the database
        * username (str): name of the user in the db
        * password (str): password of the user
        * database_name (str): name of the database
        * use_tqdm (bool): if True, tqdm will be used to show a progress bar (default: True)
    """
    def __init__(self, hostname, username, password, database_name, use_tqdm=True):
        self.sql_url = f"postgresql://{username}:{password}@{hostname}/{database_name}"
        Session, engine = database.init_db(self.sql_url)
        from . import models
        self.__models = models
        self.session = Session()
        self.engine = engine
        self.use_tqdm = use_tqdm

    def __repr__(self):
        return f"Goldmine Client <{self.sql_url}>"

    def get_models(self):
        """
        Returns the scheme of the database. Useful for filtering.
        """
        return self.__models

    def _read_query(self, table_name, filters=None, limit=None, offset=None):
        if not isinstance(table_name, list):
            table_name = [table_name]

        t = table_name.pop(0)
        model = getattr(self.__models, t, None) 
        if model is None:
            raise ValueError(f'{t} not found!')
        query = self.session.query(model)

        for t in table_name:
            model_ = getattr(self.__models, t, None)
            if model_ is None:
                raise ValueError(f'{t} not found!')
            query = query.join(model_)
        
        if filters:
            filter = True
            for f in filters:
                filter = and_(filter, f)
            query = query.filter(filter)
        if limit is None:
            return query.all()
        if offset is not None:
            query = query.offset(offset)
        query = query.limit(limit)
        return query

    def _write_query(self, event, type, data=None, uuid=None):
        params = {'event': event,
                  'type': type,
                  'data': data,
                  'uuid': uuid,
                  'user_id': 1}
        event = self.__models.eventstore(**params)
        self.session.add(event)
        return event

    def _query_to_df(self, query):
        records = [q.__dict__ for q in query]
        df = pd.DataFrame.from_records(records)
        try:
            del df['_sa_instance_state']
        except KeyError:
            pass
        return df

    def get(self, table_name, dataframe=True, filters=None, limit=None, offset=None):
        """
        This method corresponds to a `select` query in the database (read-access).
        ::

            client = GoldmineClient('localhost', 'postgres', '', 'molecdb')
            df = client.get('molecule')
            df.head()

        Args:
            * table_name (str): name of the table to get in the database
            * dataframe (bool): if true, the result will be an instance of pandas.DataFrame
            * filters (list): list of filters to apply on the query
            * limit (int or None): if limit is specified, only the first N example will be fetched
            * offset (int or None): if specified, the query will start from offset
        """
        query = self._read_query(table_name, filters, limit, offset)
        if not dataframe:
            return query
        return self._query_to_df(query)

    def add(self, table_name, data):
        """
        This method can be used to add data to a table. data can either be a
        list of dict a pandas.DataFrame instance or a dictionary.
        ::

            client = GoldmineClient('localhost', 'postgres', '', 'molecdb')
            client.add('molecule', {'smiles': 'C1=CC=CC=C1'})
            df = client.get('molecule')
            df.head()
    
        Args:
            * table_name (str): name of the table where to add data
            * data (list, pandas.DataFrame or dict): data to add.
        """
        if isinstance(data, pd.DataFrame):
            iter = data.iterrows()
            events = []
            if self.use_tqdm:
                iter = tqdm(data.iterrows(), total=len(data))
            for i, row in enumerate(iter):
                event = self._write_query('create', table_name, row[1].to_dict())
                events.append(event)
                if i % 500 == 0:
                    self.session.commit()
            self.session.commit()
            return events
        elif isinstance(data, list):
            events = []
            iter = data
            if self.use_tqdm:
                iter = tqdm(data)
            for i, d in enumerate(iter):
                event = self._write_query('create', table_name, d)
                events.append(event)
                if i % 500 == 0:
                    self.session.commit()
            self.session.commit()
            return events
        elif isinstance(data, dict):
            event = self._write_query('create', table_name, data)
            self.session.commit()
            return event
        else:
            error_msg = f"data has type {type(data)} but "
            error_msg += f"{self.add.__name__} is expecting either:\n"
            error_msg += f"\t* a instance of pandas.DataFrame\n"
            error_msg += f"\t* a list containing dict\n"
            error_msg += f"\t* a dict\n"
            raise TypeError(error_msg)

    def update(self, table_name, data, uuid=None):
        """
        This method updates a table with the content of the data. It accepts
        also pandas.DataFrame instance. Which could be handy:
        ::

            client = GoldmineClient('localhost', 'postgres', '', 'molecdb')
            df = client.get('molecule')
            df.at[0, 'smiles'] = 'C#N'
            client.update('molecule', df)
            df = client.get('molecule')
            df.head()

        Args:
            * table_name (str): name of the table to update
            * data (pandas.DataFrame, dict or list): data to update
            * uuid (str or list): if data is a dict or list, uuid must be speicified"
        """
        if isinstance(data, pd.DataFrame):
            iter = data.iterrows()
            if self.use_tqdm:
                iter = tqdm(data.iterrows(), total=len(data))
            for row in iter:
                row = row[1].to_dict()
                uuid = row['uuid']
                del row['uuid']
                del row['created_on']
                del row['updated_on']
                self._write_query('update', table_name, row, uuid=uuid)
            self.session.commit()
        elif isinstance(data, dict) and uuid is not None:
            self._write_query('update', table_name, data=data, uuid=uuid)
            self.session.commit()
        elif isinstance(data, list) and isinstance(uuid, list):
            iter = zip(uuid, data)
            if self.use_tqdm:
                iter = tqdm(iter)
            for _id, d in iter:
                self._write_query('update', table_name, data=d, uuid=_id)
            self.session.commit()
        else:
            error_msg = f"data has type {type(data)} but "
            error_msg = f"{self.update.__name__} is expecting either:\n"
            error_msg = f"\t* a instance of pandas.DataFrame containing a row named uuid\n"
            error_msg = f"\t* a dict and a uuid\n"
            error_msg = f"\t* a list of dict and a list of uuid\n"
            raise TypeError(error_msg)

    def delete(self, table_name, uuid):
        """
        Remove elements of the database.

        For example to flush a table:
        ::

            client = GoldmineClient('localhost', 'postgres', '', 'molecdb')
            df = client.get('molecule')
            client.delete('molecule', df['uuid'].tolist())

        Args:
            * table_name (str): name of the table where to remove data
            * uuid (str, list): id or list of id to remove from the database
        """
        if isinstance(uuid, str):
            self._write_query('delete', table_name, uuid=uuid)
            self.session.commit()
        elif isinstance(uuid, list):
            for _id in uuid:
                self._write_query('delete', table_name, uuid=_id)
            self.session.commit()
        else:
            raise TypeError("uuid should either be a list of a str, got a {type(uuid)}")

    def rollback(self, before):
        self._write_query('rollback', None, data={'before': before.isoformat()})
        self.session.commit()

    def get_fragment(self, smiles):
        """
        Get the fragment with a particular smiles

        Args:
            * smiles (str): smiles of a particular fragment to get
        """
        if not isinstance(smiles, list):
            smiles = [smiles]
        filters = [self.__models.fragment.smiles == s for s in smiles]
        fragment = self.get('fragment', filters=filters)
        return fragment

    def add_fragment(self, smiles):
        """
        Add a fragment if it's not already in the database.

        Args:
            * smiles (str): smiles of the fragment to add
        """
        if not isinstance(smiles, list):
            smiles = [smiles]
        events = []
        for s in smiles:
            fragment = self.get_fragment(smiles)
            if fragment.empty:
                event = self.add('fragment', {'smiles': s})
                events.append(event)
                continue
            events.append(fragment[0].to_dict())
        return events

    def del_fragment(self, smiles):
        """
        Delete a fragment, or a list of fragments.

        Args:
            smiles (str or list): smiles or list of smiles of the fragment to
            delete.
        """
        if not isinstance(smiles, list):
            smiles = [smiles]
        fragments = [self.get_fragment(s) for s in smiles]
        for f in fragments:
            if not f.empty:
                self.delete('fragment', f.uuid[0])

    def _add_molecule(self, fragment, smiles):
        if not isinstance(fragment, list) and not isinstance(smiles, str):
            raise TypeError(f"fragment should be a list of string, got a {type(fragment)} and smiles should be a str, got a {type(smiles)}")
        event = self.add('molecule', {'smiles': smiles})
        mol_uuid = event.uuid
        events = self.add_fragment(fragment)
        params = [{'molecule_id': mol_uuid,
                   'fragment_id': f.uuid,
                   'order': i} for i, f in enumerate(events)]
        self.add('molecule_fragment', params)

    def add_molecule(self, fragment, smiles):
        """
        Add a molecule and its fragments.
        
        ::

            client = GoldmineClient('localhost', 'postgres', '', 'molecdb')
            client.add_molecule(fragment=['A', 'B', 'C'], smiles='D')

        Args:
            * fragment (list of smiles or list of list of smiles): fragment to add.
            * smiles (str or list): molecule to add.
        """
        if isinstance(fragment, list) and isinstance(smiles, str):
            self._add_molecule(fragment, smiles)
        elif isinstance(fragment, list) and isinstance(smiles, list):
            for frag_list, smi in zip(fragment, smiles):
                self._add_molecule(frag_list, smi)
        else:
            raise TypeError("fragment should be a list and smiles a str")

    def del_molecule(self, smiles):
        """
        Delete a molecule, or a list of molecule. This will not remove the fragments.

        Args:
            * smiles (str, list): smiles or list of smiles to remove
        """
        if not isinstance(smiles, list):
            smiles = [smiles]
        for s in smiles:
            molecule = self.get('molecule', filters=[self.__models.molecule.smiles == s], dataframe=False)
            for rel in molecule[0].molecule_fragment_collection:
                self.delete('molecule_fragment', rel.uuid)
            self.delete('molecule', molecule[0].uuid)

    def add_conformation(self, molecule, atoms, properties):
        pass

    def add_calculation(self, conformation_uuid, data):
        pass

    def add_software(self, name, version):
        pass
