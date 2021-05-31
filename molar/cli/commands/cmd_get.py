# external
import click
from rich import print
from rich.table import Table

from ... import Client


@click.command(help="Get data from a table")
@click.argument("table-name", nargs=1)
@click.option("-l", "--limit", type=int, default=10)
@click.option("-s", "--offset", type=int, default=None)
@click.option("-o", "--order-by", type=str, default=None)
@click.pass_context
def get(ctx, table_name, limit, offset, order_by):
    console = ctx.obj["console"]
    client = Client(ctx.obj["client_config"])
    if table_name not in client.database_specs["table"]:
        console.log(f"{table_name} could not be found!")
        return

    # TODO add filtering options?
    data = client.get(table_name, None, limit, offset, order_by)
    column_names = [col for col in data[0].__dict__.keys()]
    table = Table(title=table_name)

    table_id = f"{table_name}_id"
    if table_id in column_names:
        index = column_names.index(table_id)
        column_names.pop(index)
        column_names.insert(0, table_id)

    if "created_on" in column_names:
        index = column_names.index("created_on")
        column_names.pop(index)
        column_names.insert(1, "created_on")

    if "updated_on" in column_names:
        index = column_names.index("updated_on")
        column_names.pop(index)
        column_names.insert(2, "updated_on")

    if "_sa_instance_state" in column_names:
        index = column_names.index("_sa_instance_state")
        column_names.pop(index)

    for col in column_names:
        table.add_column(col)

    for record in data:
        ordered_values = [str(record.__dict__[n]) for n in column_names]
        table.add_row(*ordered_values)

    print(table)
