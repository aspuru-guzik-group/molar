from sqlalchemy import create_engine
import sqlalchemy
from alembic.config import Config
from alembic import command
import logging


def create_connection(user, password, hostname, database):
    engine = create_engine(f'postgresql://{user}:{password}@{hostname}/{database}')
    return engine.connect()


def create_user(conn, user, password):
    conn.execute(f'CREATE ROLE {user} WITH LOGIN PASSWORD \'{password}\';')


def transfer_ownership(conn, new_owner):
    conn.execute(f'''
    DO $$DECLARE r record; 
    BEGIN 
        FOR r in SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\' 
        LOOP 
            EXECUTE \'ALTER TABLE public.\'|| quote_ident(r.table_name) ||\' OWNER TO {new_owner};\'; 
        END LOOP; 
    END$$;
    ''') 

    conn.execute(f'ALTER TABLE sourcing.eventstore OWNER TO {new_owner};')
    conn.execute(f'ALTER SCHEMA public OWNER TO {new_owner};')
    conn.execute(f'ALTER SCHEMA sourcing OWNER TO {new_owner};')
    conn.execute(f'ALTER DATABASE {new_db_name} OWNER TO {new_owner};')
    conn.execute(f'ALTER FUNCTION public.create_synthesis_hid OWNER TO {new_owner};') 
    conn.execute(f'ALTER FUNCTION sourcing.on_event OWNER TO {new_owner};')

def grant_access_right(conn, user):
    conn.execute(f'GRANT USAGE ON SCHEMA public TO {user};')
    conn.execute(f'GRANT USAGE ON SCHEMA sourcing TO {user};')
    conn.execute(f'GRANT EXECUTE ON FUNCTION public.create_synthesis_hid TO {user};')
    conn.execute(f'GRANT EXECUTE ON FUNCTION sourcing.on_event TO {user};')
    conn.execute(f'GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO {user};')
    conn.execute(f'GRANT USAGE ON ALL SEQUENCES IN SCHEMA sourcing TO {user};')
    conn.execute(f'GRANT SELECT, INSERT ON TABLE sourcing.eventstore TO {user};')
    conn.execute(f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {user};')


def create_db(user, password, hostname, new_db_name, structure_file,
        event_sourcing_file, admin_password, user_password, alembic_conf):
    logger = logging.getLogger('INFO')
    
    conn = create_connection(user, password, hostname, 'postgres')
    conn.execution_options(isolation_level="AUTOCOMMIT").execute(f"CREATE DATABASE {new_db_name};")
    conn.close()

    conn = create_connection(user, apssword, hostname, new_db_name)

    structure = sqlalchemy.text(open(structure_file, 'r').read())
    event_sourcing = sqlalchemy.text(open(event_sourcing_file, 'r').read())


    conn.execute('CREATE EXTENSION "uuid-ossp";') 
    conn.execute(structure)
    conn.execute(event_sourcing)

    admin_username = new_db_name +'_admin'
    create_user(conn, new_db_name, user_password)
    create_user(conn, admin_username, admin_password)

    # Transferring ownership to admin 
    transfer_ownership(conn, admin_username)

    conf = get_alembic_conf(
        f'postgresql://{new_db_name}_admin:{admin_password}@{hostname}/{new_db_name}',
        alembic_conf
    )
    conf.attributes['connection'] = conn
    command.upgrade(conf, 'head')

    # Granting rights
    grant_access_right(conn, new_db_name)
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
