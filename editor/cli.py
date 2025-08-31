import click
from pathlib import Path
from .core import new_level as core_new_level, add_object as core_add_object
from .core import export as core_export, stats as core_stats


@click.group()
def cli():
    pass


@cli.command("new-level")
@click.option("--name", required=True)
@click.option("--width", type=int, required=True)
@click.option("--height", type=int, required=True)
def new_level_cmd(name, width, height):
    p = core_new_level(name, width, height)
    click.echo(f"Created: {p}")


@cli.command("add-object")
@click.option("--level", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option(
    "--type",
    type=click.Choice(["wall", "spawn", "enemy", "coin", "door"]),
    required=True,
)
@click.option("--x", type=int, required=True)
@click.option("--y", type=int, required=True)
def add_object_cmd(level, type, x, y):
    core_add_object(Path(level), type, x, y)
    click.echo("Added.")


@cli.command("export")
@click.option("--level", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--out", type=click.Path(dir_okay=False), required=True)
def export_cmd(level, out):
    p = core_export(Path(level), Path(out))
    click.echo(f"Exported: {p}")


@cli.command("stats")
@click.option("--level", type=click.Path(exists=True, dir_okay=False), required=True)
def stats_cmd(level):
    s = core_stats(Path(level))
    click.echo(s)


if __name__ == "__main__":
    cli()
