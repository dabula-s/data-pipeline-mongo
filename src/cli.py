import click

from src.commands.database import database
from src.commands.pipeline import pipeline


@click.group()
def cli():
    pass


cli.add_command(database)
cli.add_command(pipeline)

if __name__ == '__main__':
    cli()
