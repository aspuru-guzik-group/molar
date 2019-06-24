from flask import Flask
from flask_graphql import GraphQLView

import toml

from . view import JWTGraphQLView
from . import database

auth_settings = None


def create_app(settings_file, settings_name):
    settings = toml.load(open(settings_file, 'r'))
    if settings_name is not None:
        settings = settings[settings_name]
    sql_url = "postgresql://{user}:{pass}@{host}/{db_name}".format(**settings['database'])
    Session, engine = database.init_db(sql_url)

    #settings['auth']['private_key'] = open(settings['auth']['private_key'], 'r').read()
    #settings['auth']['public_key'] = open(settings['auth']['public_key'], 'r').read()
    global auth_settings
    auth_settings = settings['auth']

    from .gql.schema import schema
    app = Flask(__name__)
    app.add_url_rule(
        '/graphql',
        view_func=JWTGraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=settings['graphiql'],
            session_maker=Session,
            private_key=settings['auth']['private_key'],
            public_key=settings['auth']['public_key'],
            expiration_token=settings['auth']['expiration_token']
        )
    )
    return app
