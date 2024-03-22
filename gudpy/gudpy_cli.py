import click
import os
import sys

from core import iterators
from core import gudpy as gp
from core import enums
from core import config


def loadProject(ctx, project):
    if not project:
        project = click.prompt("Path to project", type=click.Path())
        return
    ctx.obj = gp.GudPy()
    ctx.obj.loadFromProject(project)
    echoTick(f" GudPy project sucessfuly loaded at {project}")


def loadFile(ctx, value):
    print(value)
    file, format = value
    if not file:
        file = click.prompt("Path to load file", type=click.Path())
    if not format:
        format = click.prompt(
            "File type",
            click.Tuple([click.Path(), click.Choice(["yaml", "txt"])]))
        if format == "yaml":
            format = enums.Format.YAML
        elif format == "txt":
            format = enums.Format.TXT
        else:
            return
    if not file or format:
        return
    ctx.obj = gp.GudPy()
    ctx.obj.loadFromFile(file, format)
    click.echo(click.style(u"\u2714", fg="green", bold=True) +
               f" GudPy input file {file} sucessfuly loaded")


def loadConfig(ctx, cfg):
    configDir = (
        os.path.join(sys._MEIPASS, "bin", "configs", "instruments")
        if hasattr(sys, "_MEIPASS")
        else os.path.join(
            config.__rootdir__, "bin", "configs", "instruments"
        )
    )
    if cfg == "NIMROD2012":
        cfg = os.path.join(configDir, "NIMROD_84modules_2012.config")
    elif cfg == "SANDALS2011":
        cfg = os.path.join(configDir, "SANDALS_2011.config")
    else:
        return

    ctx.obj = gp.GudPy()
    ctx.obj.loadFromFile(cfg, enums.Format.TXT, config=True)


def echoIndent(text):
    click.echo("     -  " + text)


def echoTick(text):
    click.echo("   " +
               click.style(u"\u2714", fg="green", bold=True) +
               f" {text}")


def echoWarning(text):
    click.secho("  (!) " + f"WARNING: {text}\n",
                fg='yellow', bold=True)


def echoProcess(name):
    click.secho("\n  " + f">>  {name}\n", bold=True, fg='cyan')


@click.group()
@click.option(
    "--project", "-p",
    type=click.Path(exists=True),
    help="Loads from a project"
)
@click.option(
    "--file", "-f",
    type=click.Tuple([click.Path(exists=True), click.Choice(["yaml", "txt"])]),
    nargs=2,
    help="Loads from a file"
)
@click.option(
    "--config",
    type=click.Choice(["NIMROD2012", "SANDALS2011"]),
    help="Loads from a config file"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Run processes verbosely, displaying the output"
)
@click.pass_context
def cli(ctx, project, file, config, verbose):
    click.echo("\n"
               "============================================================"
               "============================================================")
    click.secho("                                                       "
                "GudPy v0.5.0", bold=True)
    click.echo("============================================================"
               "============================================================"
               "\n")

    if project:
        loadProject(ctx, project)
    elif file:
        loadFile(ctx, file)
    elif config:
        loadConfig(ctx, config)
    else:
        click.echo(
            "Error: no project path, file or config provided. "
            "See --help for options.", err=True)

    ctx.obj.verbose = verbose


@cli.command(name="gudrun")
@click.pass_context
def run_purge(ctx, *args):
    echoProcess("purge_det")
    ctx.obj.runPurge()
    if ctx.obj.verbose:
        click.echo_via_pager(ctx.obj.purge.output)
    echoTick("Purge Complete")
    echoIndent("Number of Good Detectors: " +
               click.style(f"{ctx.obj.purge.detectors}", bold=True))
    thresh = ctx.obj.gudrunFile.instrument.goodDetectorThreshold
    if thresh and ctx.obj.purge.detectors < thresh:
        echoWarning(f"The acceptable minimum for Good Detectors is {thresh}")
    echoIndent(f"Outputs avaliable at {ctx.obj.projectDir}/Purge\n")


@cli.command(name="gudrun")
@click.option(
    "--purge",
    is_flag=True,
    default=False,
)
@click.pass_context
def run_gudrun(ctx, purge):
    if purge:
        ctx.invoke(run_purge, ctx)
    echoProcess("gudrun_dcs")
    ctx.obj.runGudrun()
    if ctx.obj.verbose:
        click.echo_via_pager(ctx.obj.gudrun.output)
    echoTick("Gudrun Complete")
    echoIndent(f"Outputs avaliable at {ctx.obj.projectDir}/Gudrun\n")


@cli.command()
@click.option(
    "--purge",
    is_flag=True,
    default=False,
)
@click.argument(
    "n",
    nargs=1,
    type=int
)
@click.pass_context
def iterate_inelasticity(ctx, purge, n):
    if purge:
        purge(ctx)
    echoProcess("Wavelength Inelasiticity Subtraction Iterator")

    iterator = iterators.InelasticitySubtraction(n)
    ctx.obj.iterateGudrun(iterator)
    if ctx.obj.verbose:
        click.echo_via_pager(ctx.obj.gudrunIterator.output)
    echoTick("Iterator Complete")
    echoIndent(f"Outputs avaliable at {ctx.obj.projectDir}/Gudrun\n")


if __name__ == '__main__':
    cli()
