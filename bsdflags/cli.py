"""BSD file flags viewer
More info: https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemDetails/FileSystemDetails.html#//apple_ref/doc/uid/TP40010672-CH8-SW8
"""

import click
from tabulate import tabulate

from .click import Group, Command
from .flags import Flag, FLAGS, NAMES
from .file import File


def getflag(ctx, name):
    """return the Flag object for a given name or alias"""
    if not name:
        return

    if not name in NAMES:
        raise click.BadParameter(f"No such flag: {name}")

    return FLAGS.get(name)


def to_str(val, if_true="yes", if_false="no") -> str:
    """Return if_true for True or if_false for False"""
    return if_true if val else if_false


@click.group(cls=Group)
@click.pass_context
@click.option("-d", "--debug", is_flag=True)
def cli(ctx, *args, **kwargs):
    """getflags -- BSD flag viewer"""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG_MODE'] = kwargs.get("debug")
    if ctx.invoked_subcommand is None:
        ctx.invoke(file_flags, *args, **kwargs)

@cli.command("file", default=True, aliases=["f"])
@click.pass_context
@click.argument("filename", type=click.Path(exists=True))
@click.argument("flag", callback=getflag, required=False, autocompletion=FLAGS.keys())
@click.option("-v", "--verbose", is_flag=True,
              help="print file info")
@click.option("-a", "--all", "fltr", flag_value="all",
              help="print all flags (valid with --long)")
@click.option("-l", "--long", "fmt", flag_value="long",
              help="print one flag per name followed by on/off")
@click.option("-s", "--short", "fmt", flag_value="short", default="short",
              help="space seperated list of names")
def file_flags(ctx, filename, flag=None, fmt=None, fltr=None, verbose=False):
    """Print the flags for a file"""
    flags = {}
    fp = File(filename)

    if ctx.obj['DEBUG_MODE']:
        print(click.style("DEBUG>", fg="yellow"), f"{filename=}, {flag=}, {fmt=}, {fltr=}")

    if fltr == "all":
        flags = { name: "off" for name in FLAGS }

    if flag:
        flags = { flag.name: to_str(fp.has_flag(flag), "on", "off") }
    else:
        flags.update({ name: "on" for name in fp.flags })

    width = max(map(len, flags))

    if verbose:
        print(fp.pretty)
        print(max([width+4, len(fp.pretty)]) * "-")

    if fmt == "short":
        click.echo(" ".join([n for (n,o) in flags.items() if o == "on"]))

    elif fmt == "long":
        for name, enabled in flags.items():
            print(f"{name:<{width}} {enabled}")


@cli.command("list", aliases=["ls"])
def ls():
    """list all BSD flags"""
    flags = [ [flag.name, ", ".join(flag.aliases), flag.desc] for flag in FLAGS.values() ]
    print(tabulate(flags, headers=["Name", "Aliases", "Description"]))


if __name__ == "__main__":
    cli()
