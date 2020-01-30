import click
import coloredlogs

from . import admin as _admin

@click.group()
def cli():
    pass

@cli.group()
def admin():
    pass    
    

@cli.command()
def get():
    pass

@cli.command()
def add():
    pass

@cli.command()
def update():
    pass

@cli.command()
def delete():
    pass

@admin.command()
@click.option('-u', '--user', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-h', '--hostname', prompt=True)
@click.option('-d', '--db_name', prompt=True)
@click.option('-s', '--struct_file', prompt=True)
@click.option('-e', '--es_file', prompt=True)
@click.option('-c', '--config', help="Alembic configuration file")
@click.option('--admin_pass', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--user_pass', prompt=True, hide_input=True, confirmation_prompt=True)
def create_db(user, password, hostname, db_name, struct_file, es_file, config, admin_pass, user_pass):
    _admin.create_db(user, password, hostname, db_name, struct_file, es_file, admin_pass, user_pass, 'alembic.ini')


@admin.command()
@click.option('-u', '--user', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-h', '--hostname', prompt=True)
@click.option('-d', '--db_name', prompt=True)
@click.confirmation_option(prompt='Are you sure you want to drop the db?')
def drop_db(user, password, hostname, db_name):
    _admin.drop_db(user, password, hostname, db_name)


if __name__ == '__main__':
    coloredlogs.install('INFO')
    cli()
