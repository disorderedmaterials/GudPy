import click
import os
import sys
import ast
import shutil

from core import gudpy as gp
from core import enums
from core import config
from core import optimise as opt
from core import data
from core import utils


def loadProject(ctx, project):
    if not project:
        return echoError("No project directory specified")
    ctx.obj = gp.GudPy()
    ctx.obj.loadFromProject(project)
    echoTick(f"GudPy project sucessfuly loaded at {project}")


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
    click.echo("    " + text)


def echoTick(text):
    echoIndent(click.style(u"\u2714 ", fg="green", bold=True) + text)


def echoWarning(text):
    click.secho("  (!) " + f"WARNING: {text}\n",
                fg="yellow", bold=True)


def echoProcess(name):
    click.secho("\n  " + f">>  {name}\n", bold=True, fg="cyan")


def echoError(msg):
    click.secho("  (X) " + f"ERROR: {msg}",
                fg="red", bold=True)
    return 1


@click.group()
def cli():
    pass


@cli.group()
@click.option(
    "--project", "-p",
    type=click.Path(exists=True),
    help="Loads from a project"
)
@click.option(
    "--config",
    type=click.Choice(["NIMROD2012", "SANDALS2011"]),
    help="Loads from a config file"
)
@click.pass_context
def gudpy(ctx, project, config):
    click.echo("============================================================"
               "============================================================")
    click.secho("                                                       "
                "GudPy v0.5.0", bold=True)
    click.echo("============================================================"
               "============================================================"
               "\n")

    if project:
        if loadProject(ctx, project):
            sys.exit()
    elif config:
        loadConfig(ctx, config)
    else:
        click.echo(
            "Error: no project path, file or config provided. "
            "See --help for options.", err=True)


@gudpy.command()
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Run processes verbosely, displaying the output"
)
@click.pass_context
def gudrun(ctx, verbose):
    echoProcess("gudrun_dcs")
    ctx.obj.runGudrun()
    if verbose:
        click.echo_via_pager(ctx.obj.gudrun.output)
    echoTick("Gudrun Complete")
    echoTick(f"Outputs avaliable at {ctx.obj.projectDir}/Gudrun")


@gudpy.command()
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Run processes verbosely, displaying the output"
)
@click.pass_context
def purge(ctx, verbose):
    echoProcess("purge_det")
    ctx.obj.runPurge()
    if verbose:
        click.echo_via_pager(ctx.obj.purge.output)
    echoTick(" Purge Complete")
    echoIndent("Number of Good Detectors: " +
               click.style(f"{ctx.obj.purge.detectors}", bold=True))
    thresh = ctx.obj.gudrunFile.instrument.goodDetectorThreshold
    if thresh and ctx.obj.purge.detectors < thresh:
        click.secho(
            f"WARNING: The acceptable minimum for Good Detectors is"
            f"{thresh}", fg="yellow", bold=True)


@gudpy.command()
@click.option(
    "--sample",
    type=str
)
@click.argument(
    "attribute",
    type=str
)
@click.argument(
    "value",
    type=str
)
@click.argument(
    "path",
    type=click.Path()
)
@click.pass_context
def edit(ctx, sample, attribute, value, path):
    echoProcess("Modifying GudrunFile")

    targetObj = None
    for sbg in ctx.obj.gudrunFile.sampleBackgrounds:
        for s in sbg.samples:
            if s.name == sample:
                targetObj = s

    if sample and targetObj is None:
        return echoError("No sample found")
    elif not sample:
        targetObj = ctx.obj.gudrunFile

    if not hasattr(targetObj, attribute):
        return echoError(f"Invalid Attribute: {attribute}")
    literalValue = ast.literal_eval(value)
    attr = targetObj.__dict__[attribute]

    if not isinstance(literalValue, type(attr)):
        return echoError(
            f"Value is of incorrect type. {attribute} is of type {type(attr)}"
        )

    setattr(targetObj, attribute, literalValue)

    projectDir = utils.makeDir(path)
    ctx.obj.setSaveLocation(projectDir)
    ctx.obj.save()

    echoTick(
        f"{attribute} have been set to: {targetObj.__dict__[attribute]}"
    )
    echoTick(f"Updated GudPy Project saved to {projectDir}")


@gudpy.command()
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Run processes verbosely, displaying the output"
)
@click.argument(
    "simulationData",
    type=click.Path(exists=True),
    nargs=1
)
@click.argument(
    "actualData",
    type=click.Path(exists=True),
    nargs=1
)
@click.argument(
    "sample",
    type=str,
    nargs=1
)
@click.option(
    "--ncalls", "-n",
    type=int,
    help="Number of calls for optimisation"
)
@click.option(
    "--output", "-o",
    type=click.Path(exists=False),
    help="Location to create new project"
)
@click.pass_context
def optimise(ctx, verbose, simulationdata, actualdata, sample, ncalls, output):
    echoProcess("Bayesian Optimisation")
    dir = output if output else os.path.join(
        ctx.obj.projectDir,
        f"BayesianOptimisation_{sample}"
    )
    ctx.obj.setSaveLocation(dir)
    echoProcess("gudrun_dcs")
    ctx.obj.runGudrun()

    samp = None
    for sbg in ctx.obj.gudrunFile.sampleBackgrounds:
        for s in sbg.samples:
            if s.name == sample:
                samp = s

    if samp is None:
        echoIndent("No sample found")

    opti = opt.BayesianOptimisation(
        gudrunFile=ctx.obj.gudrunFile,
        targetSample=samp,
        simulation=simulationdata,
        actual=actualdata,
        limit=2.0
    )

    initError = data.meanSquaredError(opti.actual, opti.simulation)
    echoIndent(f"Initial MSE: {round(initError, 5)}\n")

    result = opti.optimise(ncalls=ncalls)
    optExponents = [result.x[0:2] + [0.0], result.x[2:] + [0.0]]

    echoTick("Optimisation complete")
    echoTick(f"Optimum exponentialValues: {optExponents}")
    echoTick(f"New MSE: {round(result.fun, 5)}")

    samp.exponentialValues = optExponents

    echoProcess("gudrun_dcs")
    ctx.obj.runGudrun()
    shutil.copyfile(
        ctx.obj.gudrun.gudrunOutput.output(
            name=sample,
            dataFile=samp.dataFiles[0],
            type=".mint01"
        ),
        os.path.join(
            ctx.obj.projectDir,
            f"{sample}_optimised.mint01"
        )
    )
    echoTick("Gudrun Complete")
    echoTick("New mintfile avaliable at " +
             os.path.join(
                 ctx.obj.projectDir,
                 f"{sample}_optimised.mint01"
             ))


@cli.command()
@click.argument(
    'data1',
    type=click.Path(exists=True)
)
@click.argument(
    'data2',
    type=click.Path(exists=True)
)
def mse(data1, data2):
    echoProcess("Mean Squared Error")
    d1 = data.NpDataSet(data1, 0.5)
    d2 = data.NpDataSet(data2, 0.5)
    err = data.meanSquaredError(d1, d2)

    echoIndent(str(round(err, 5)))


if __name__ == "__main__":
    cli()
