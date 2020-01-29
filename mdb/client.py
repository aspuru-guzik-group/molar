from functools import partial

import pandas as pd
from tqdm import tqdm
from sqlalchemy import and_
import psycopg2

from . import database


class MDBClient:
    def __init__(self, hostname, username, password, database_name,
            use_tqdm=True, convert_smiles=True, convert_synth_hid=True,
            convert_lab_short_name=True):
        self.sql_url = f"postgresql://{username}:{password}@{hostname}/{database_name}"
        Session, engine, models = database.init_db(self.sql_url)
        self.session = Session()
        self.engine = engine
        self.models = models

        self.dao =  DataAccessObject(self.session, self.models)
        self.mapper = SchemaMapper(self.dao)
        self.rollback = self.dao.rollback

        mapper_methods = [func for func in dir(self.mapper) if \
                          callable(getattr(self.mapper, func)) \
                          and not func.startswith("__")]

        for fname, func in self.mapper.__class__.__dict__.items():
            if fname.startswith('__'):
                continue
            func = ArgumentsFetcher(func,
                                    self.dao,
                                    convert_smiles,
                                    convert_synth_hid,
                                    convert_lab_short_name)
            setattr(self, fname, func)

        self.use_tqdm = use_tqdm

    def __del__(self):
        self.session.close()

    def get(self, table_name, return_df=True, filters=None, limit=None, offset=None):
        data = self.dao.get(table_name, filters, limit, offset)
        if not return_df:
            return data
        df = pd.DataFrame.from_records([d.__dict__ for d in data])
        if '_sa_instance_state' in df.columns:
            del df['_sa_instance_state']
        return df
    
    def get_uuid(self, table_name, **kwargs):
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
        self.dao.rollback(before)


class DataAccessObject:
    """
    Data Access Object.

    Define the low level interactions between MDBClient and the database.

    Parameters:

        * session: (sqlalchemy.orm.session.Session)
        * models: (sqlalchemy.orm.mapper)
    """
    def __init__(self, session, models):
        self.session = session
        self.models = models

    def get(self, table_name, filters=None, limit=None, offset=None):
        """
        Reads data from a table

        Parameters:

            * table_name
            * filters
            * limit
            * offset
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
            
            * before:
        """

        params = {'event': 'rollback',
                  'data': {'before': before.isoformat()}}
        event = self.models.eventstore(**params)
        self.session.add(event)
        return event


class SchemaMapper:
    """
    SchemaMapper map the schema of the database. It contains some utility function to
    add data to the database.

    It is meant to be used through MDBClient.
    """
    def __init__(self, dao):
        self.dao = dao
    
    def add_fragment(self, smiles):
        event = self.dao.add('fragment', {'smiles': smiles})
        self.dao.session.commit()
        return event

    def add_molecule(self, smiles, fragments_uuid):
        event = self.dao.add('molecule', {'smiles': smiles})
        if not isinstance(fragments_uuid, list):
            fragments_uuid = [fragments_uuid]
        self.dao.session.commit()
        for order, uuid in enumerate(fragments_uuid):
            data = {'molecule_id': event.uuid, 'fragment_id': uuid, 'order': order}
            self.dao.add('molecule_fragment', data)
        self.dao.session.commit()
        return event

    def add_conformer(self, molecule_uuid, x, y, z, atomic_numbers, metadata):
        data = {'molecule_id': molecule_uuid, 'x': x, 'y': y, 'z': z,
                'atomic_numbers': atomic_numbers, 'metadata': metadata}
        event = self.dao.add('conformer', data)
        self.dao.session.commit()
        return event
    
    def add_calculation_type(self, name):
        data = {'name': name}
        event = self.dao.add('calculation_type', data)
        self.dao.session.commit()
        return event

    def add_calculation(self, input, output, command_line, calculation_type, software_uuid, conformer_uuid,
            metadata, output_conformer_uuid=None):
        data = {'input': input,
                'output': output,
                'command_line': command_line,
                'calculation_type_id': calculation_type,
                'software_id': software_uuid,
                'conformer_id': conformer_uuid,
                'metadata': metadata}
        if output_conformer_uuid is not None:
            data['output_conformer_id'] = output_conformer_uuid
        event = self.dao.add('calculation', data)
        self.dao.session.commit()
        return event

    def add_software(self, name, version):
        data = {'name': name, 'version': version}
        event = self.dao.add('software', data)
        self.dao.session.commit()
        return event

    def add_lab(self, name, short_name):
        data = {'name': name, 'short_name': short_name}
        event = self.dao.add('lab', data)
        self.dao.session.commit()
        return event

    def add_synthesis_machine(self, name, metadata, lab_uuid):
        data = {'name': name, 'metadata': metadata, 'lab_id': lab_uuid}
        event = self.dao.add('synthesis_machine', data)
        self.dao.session.commit()
        return event

    def add_synthesis(self, machine_uuid, targeted_molecule_uuid, xdl, notes):
        data = {'targeted_molecule_id': targeted_molecule_uuid,
                'machine_id': machine_uuid,
                'xdl': xdl,
                'notes': notes}
        event = self.dao.add('synthesis', data)
        self.dao.session.commit()
        return event

    def add_synth_molecule(self, synth_uuid, molecule_uuid, yield_):
        data = {'synth_id': synth_uuid, 'molecule_id': molecule_uuid, 'yield': yield_}
        event = self.dao.add('synth_molecule', data)
        self.dao.session.commit()
        return event

    def add_synth_fragment(self, synth_uuid, fragment_uuid, yield_):
        data = {'synth_id': synth_uuid, 'fragment_id': fragment_uuid, 'yield': yield_}
        event = self.dao.add('synth_fragment', data)
        self.dao.session.commit()
        return event

    def add_synthesis_machine(self, name, metadata, lab_uuid):
        data = {'name': name, 'metadata': metadata, 'lab_id': lab_uuid}
        event = self.dao.add('synthesis_machine', data)
        self.dao.session.commit()
        return event

    def add_experiment_machine(self, name, metadata, type_uuid, lab_uuid):
        data = {'name': name, 'lab_id': lab_uuid, 'type_id': type_uuid, 'metadata': metadata}
        event = self.dao.add('experiment_machine', data)
        self.dao.session.commit()
        return event

    def add_experiment_type(self, name):
        data = {'name': name}
        event = self.dao.add('experiment_type', data)
        self.dao.session.commit()
        return event

    def add_experiment(self, synth_uuid, x, y, x_units_uuid, y_units_uuid,
            machine_uuid, metadata, notes):
        data = {'synth_id': synth_uuid, 
                'metadata': metadata,
                'notes': notes}
        event = self.dao.add('experiment', data)
        self.dao.session.commit()
        self.add_xy_data_experiment(event.uuid, x, y, x_units_uuid, y_units_uuid)
        return event

    def add_xy_data_experiment(self, experiment_uuid, x, y, x_units_uuid, y_units_uuid):
        data = {'experiment_uuid': experiment_uuid,
                'x': x,
                'y': y,
                'x_units_uuid': x_units_uuid,
                'y_units_uuid': y_units_uuid}
        event = self.dao.add('xy_data', data)
        self.dao.session.commit()
        return event

    def add_xy_data_calculation(self, calculation_uuid, x, y, x_units_uuid,
            y_units_uuid):
        data = {'calculation_uuid': calculation_uuid,
                'x': x,
                'y': y,
                'x_units_uuid': x_units_uuid,
                'y_units_uuid': y_units_uuid}
        event = self.dao.add('xy_data', data)
        self.dao.session.commit()
        return event

    def add_data_unit(self, name):
        data = {'name': name}
        event = self.dao.add('data_unit', data)
        self.dao.session.commit()
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
