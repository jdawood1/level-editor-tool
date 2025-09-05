import click
from pathlib import Path
from .core import new_level as core_new_level, add_object as core_add_object
from .core import export as core_export, stats as core_stats
from .core import remove_object as core_remove_object


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

@cli.command("remove-object")
@click.option("--level", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--index", type=int, help="Remove by list index")
@click.option(
    "--type",
    "obj_type",
    type=click.Choice(["wall", "spawn", "enemy", "coin", "door"]),
    help="Match key: type (with --x and --y)",
)
@click.option("--x", type=int, help="Match key: x (with --type and --y)")
@click.option("--y", type=int, help="Match key: y (with --type and --x)")
@click.option("--all", "remove_all", is_flag=True, help="Remove all matches (with match mode)")
def remove_object_cmd(level, index, obj_type, x, y, remove_all):
    """
    Remove an object by --index OR by a match triple (--type/--x/--y).
    Match mode removes the first match by default; use --all to remove all.
    """
    if index is None and not (obj_type and x is not None and y is not None):
        raise click.UsageError("Provide --index OR the trio --type/--x/--y")

    try:
        n = core_remove_object(Path(level), index=index, type=obj_type, x=x, y=y, remove_all=remove_all)
    except (ValueError, IndexError) as e:
        raise click.UsageError(str(e))
    click.echo(f"Removed {n} object(s).")

if __name__ == "__main__":
    cli()
