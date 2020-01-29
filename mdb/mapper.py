

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


