import sqlalchemy as sa


def create_connection(user, password, hostname, database):
    return sa.create_engine(
        f"postgresql://{user}:{password}@{hostname}/{database}"
    ).connect()


def create_user(connection, user, password):
    connection.execute(f"create role {user} with login password '{password}'")

