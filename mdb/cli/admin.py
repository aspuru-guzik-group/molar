from sqlalchemy import create_engine
import sqlalchemy
from alembic.config import Config
from alembic import command
import logging


def create_db(user, password, hostname, new_db_name, structure_file,
        event_sourcing_file, admin_password, user_password, alembic_conf):
    logger = logging.getLogger('INFO')
    engine = create_engine(f'postgresql://{user}:{password}@{hostname}/postgres')
    conn = engine.connect()
    conn.execution_options(isolation_level="AUTOCOMMIT").execute(f"CREATE DATABASE {new_db_name};")
    conn.close()

    engine = create_engine(f'postgresql://{user}:{password}@{hostname}/{new_db_name}')
    conn = engine.connect()

    structure = sqlalchemy.text(open(structure_file, 'r').read())
    event_sourcing = sqlalchemy.text(open(event_sourcing_file, 'r').read())


    conn.execute('CREATE EXTENSION "uuid-ossp";') 
    conn.execute(structure)
    conn.execute(event_sourcing)

    conn.execute(f'CREATE ROLE {new_db_name}_admin WITH LOGIN PASSWORD \'{admin_password}\';')
    conn.execute(f'CREATE ROLE {new_db_name} WITH LOGIN PASSWORD \'{user_password}\';')
    
    # Transferring ownership to admin
    # Transferring tables
    conn.execute(f'''
    DO $$DECLARE r record; 
    BEGIN 
        FOR r in SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\' 
        LOOP 
            EXECUTE \'ALTER TABLE public.\'|| quote_ident(r.table_name) ||\' OWNER TO {new_db_name}_admin;\'; 
        END LOOP; 
    END$$;
    ''') 
    # sequences
    #conn.execute(f'''
    #DO $$DECLARE r record; 
    #BEGIN 
    #    FOR r in SELECT sequence_schema, sequence_name FROM information_schema.sequences WHERE sequence_schema = \'public\' or sequence_schema = \'sourcing\' 
    #    LOOP 
    #        EXECUTE \'ALTER SEQUENCE \'|| quote_ident(r.sequence_schema) || \'.\' || quote_ident(r.sequence_name) || \' OWNER TO {new_db_name}_admin;\'; 
    #    END LOOP; 
    #END$$;
    #''')
    
    conn.execute(f'ALTER TABLE sourcing.eventstore OWNER TO {new_db_name}_admin;')
    conn.execute(f'ALTER SCHEMA public OWNER TO {new_db_name}_admin;')
    conn.execute(f'ALTER SCHEMA sourcing OWNER TO {new_db_name}_admin;')
    conn.execute(f'ALTER DATABASE {new_db_name} OWNER TO {new_db_name}_admin;')
    conn.execute(f'ALTER FUNCTION public.create_synthesis_hid OWNER TO {new_db_name}_admin;') 
    conn.execute(f'ALTER FUNCTION sourcing.on_event OWNER TO {new_db_name}_admin;')


    conf = get_alembic_conf(
        f'postgresql://{new_db_name}_admin:{admin_password}@{hostname}/{new_db_name}',
        alembic_conf
    )
    conf.attributes['connection'] = conn
    command.upgrade(conf, 'head')

    # Granting rights
    conn.execute(f'GRANT USAGE ON SCHEMA public TO {new_db_name};')
    conn.execute(f'GRANT USAGE ON SCHEMA sourcing TO {new_db_name};')
    conn.execute(f'GRANT EXECUTE ON FUNCTION public.create_synthesis_hid TO {new_db_name};')
    conn.execute(f'GRANT EXECUTE ON FUNCTION sourcing.on_event TO {new_db_name};')
    conn.execute(f'GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO {new_db_name};')
    conn.execute(f'GRANT USAGE ON ALL SEQUENCES IN SCHEMA sourcing TO {new_db_name};')
    conn.execute(f'GRANT SELECT, INSERT ON TABLE sourcing.eventstore TO {new_db_name};')
    conn.execute(f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {new_db_name};')
    conn.close()


def drop_db(user, password, hostname, db_name):
    engine = create_engine(f'postgresql://{user}:{password}@{hostname}/postgres')
    conn = engine.connect()
    conn.execution_options(isolation_level="AUTOCOMMIT").execute(f'DROP DATABASE {db_name};')
    conn.execute(f'DROP ROLE {db_name};')
    conn.execute(f'DROP ROLE {db_name}_admin;')
    conn.close()


def get_alembic_conf(sql_url, alembic_conf):
    conf = Config(alembic_conf)
    conf.set_main_option('sqlalchemy.url', sql_url)
    return conf 
