# external
from sqlalchemy import text
import sqlalchemy as sa


def create_connection(user, password, hostname, database):
    return sa.create_engine(
        f"postgresql://{user}:{password}@{hostname}/{database}"
    ).connect()


def create_user(connection, user, password):
    query = text(f"create role {user} with login password :password")
    connection.execute(
        query, user=sa.sql.expression.literal_column(user, True), password=password
    )


def transfer_ownership(connection, database, new_owner):
    connection.execute(
        (
            "do $$declare r record;\n"
            "begin\n"
            "   for r in select table_name from information_schema.tables\n"
            "                             where table_schema = 'public'\n"
            "   loop\n"
            "       execute 'alter table public.'|| "
            "               quote_ident(r.table_name) "
            f"               ||' owner to {new_owner};'; \n"
            "    end loop;\n"
            "end$$;\n"
        )
    )

    connection.execute(f"alter table sourcing.eventstore owner to {new_owner}")
    connection.execute(f"alter schema public owner to {new_owner};")
    connection.execute(f"alter schema sourcing owner to {new_owner};")
    connection.execute(f"alter database {database} owner to {new_owner};")
    connection.execute(f"alter function sourcing.on_event owner to {new_owner};")


def grant_access_right(connection, user):
    connection.execute(f"grant usage on schema public to {user};")
    connection.execute(f"grant usage on schema sourcing to {user};")
    connection.execute(f"grant execute on function sourcing.on_event to {user};")
    connection.execute(f"grant usage on all sequences in schema public to {user};")
    connection.execute(f"grant usage on all sequences in schema sourcing to {user};")
    connection.execute(f"grant select, insert on table sourcing.eventstore to {user};")
    connection.execute(
        (
            "grant select, insert, update, delete on all tables in "
            f"schema public to {user};"
        )
    )
