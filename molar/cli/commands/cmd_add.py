# external
import click

from ... import Client
from ...registry import REGISTRIES


@click.command(help="Add data to a table")
@click.argument("mapper", nargs=1)
@click.pass_context
def add(ctx, mapper):
    console = ctx.obj["console"]
    client = Client(ctx.obj["client_config"])

    if mapper not in client.registered_mappers:
        console.log(f"Could not find any mapper named {mapper}!")
        console.log(
            f"The available mappers are: {[k for k in client.registered_mappers.keys()]}"
        )
        return
    # external
    import ipdb

    ipdb.set_trace()
