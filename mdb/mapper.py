

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

    def add_molecule(self, smiles, fragments_id=[]):
        event = self.dao.add('molecule', {'smiles': smiles})
        if not isinstance(fragments_id, list):
            fragments_id = [fragments_id]
        self.dao.session.commit()
        for order, id in enumerate(fragments_id):
            data = {'molecule_id': event.uuid, 'fragment_id': id, 'order': order}
            self.dao.add('molecule_fragment', data)
        self.dao.session.commit()
        return event

    def add_conformer(self, molecule_id, x, y, z, atomic_numbers, metadata):
        data = {'molecule_id': molecule_id, 'x': x, 'y': y, 'z': z,
                'atomic_numbers': atomic_numbers, 'metadata': metadata}
        event = self.dao.add('conformer', data)
        self.dao.session.commit()
        return event
    
    def add_calculation_type(self, name):
        data = {'name': name}
        event = self.dao.add('calculation_type', data)
        self.dao.session.commit()
        return event

    def add_calculation(self, input, output, command_line, calculation_type_id, software_id, conformer_id,
            metadata, output_conformer_id=None):
        data = {'input': input,
                'output': output,
                'command_line': command_line,
                'calculation_type_id': calculation_type_id,
                'software_id': software_id,
                'conformer_id': conformer_id,
                'metadata': metadata}
        if output_conformer_id is not None:
            data['output_conformer_id'] = output_conformer_id
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

    def add_synthesis_machine(self, name, metadata, lab_id):
        data = {'name': name, 'metadata': metadata, 'lab_id': lab_id}
        event = self.dao.add('synthesis_machine', data)
        self.dao.session.commit()
        return event

    def add_synthesis(self, synthesis_machine_id, targeted_molecule_id, xdl, notes):
        data = {'molecule_id': targeted_molecule_id,
                'synthesis_machine_id': synthesis_machine_id,
                'xdl': xdl,
                'notes': notes}
        event = self.dao.add('synthesis', data)
        self.dao.session.commit()
        return event

    def add_synth_molecule_outcome(self, synthesis_id, molecule_id, yield_):
        data = {'synthesis_id': synthesis_id, 
                'molecule_id': molecule_id, 
                'yield': yield_}
        event = self.dao.add('synth_molecule', data)
        self.dao.session.commit()
        return event

    def add_synth_unreacted_fragment(self, synthesis_id, fragment_id, yield_):
        data = {'synthesis_id': synthesis_id, 
                'fragment_id': fragment_id, 
                'yield': yield_}
        event = self.dao.add('synth_fragment', data)
        self.dao.session.commit()
        return event

    def add_synthesis_machine(self, name, metadata, lab_id):
        data = {'name': name, 'metadata': metadata, 'lab_id': lab_id}
        event = self.dao.add('synthesis_machine', data)
        self.dao.session.commit()
        return event

    def add_experiment_machine(self, name, metadata, experiment_type_id, lab_id):
        data = {'name': name, 
                'lab_id': lab_id, 
                'experiment_type_id': experiment_type_id, 
                'metadata': metadata}
        event = self.dao.add('experiment_machine', data)
        self.dao.session.commit()
        return event

    def add_experiment_type(self, name):
        data = {'name': name}
        event = self.dao.add('experiment_type', data)
        self.dao.session.commit()
        return event

    def add_experiment(self, synthesis_id, experiment_machine_id, metadata, notes):
        data = {'synthesis_id': synthesis_id, 
                'experiment_machine_id': experiment_machine_id,
                'metadata': metadata,
                'notes': notes}
        event = self.dao.add('experiment', data)
        self.dao.session.commit()
        return event

    def add_xy_data_experiment(self, experiment_id, name, x, y, x_units_id, y_units_id):
        data = {'experiment_id': experiment_id,
                'name': name,
                'x': x,
                'y': y,
                'x_units_id': x_units_id,
                'y_units_id': y_units_id}
        event = self.dao.add('xy_data', data)
        self.dao.session.commit()
        return event

    def add_xy_data_calculation(self, calculation_id, name, x, y, x_units_id, y_units_id):
        data = {'calculation_id': calculation_id,
                'name': name,
                'x': x,
                'y': y,
                'x_units_id': x_units_id,
                'y_units_id': y_units_id}
        event = self.dao.add('xy_data', data)
        self.dao.session.commit()
        return event

    def add_data_unit(self, name):
        data = {'name': name}
        event = self.dao.add('data_unit', data)
        self.dao.session.commit()
        return event
