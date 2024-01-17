import tempfile
import os
import sys
import subprocess

from core import config
from core import utils
from core import enums

SUFFIX = ".exe" if os.name == "nt" else ""


def gudrun(gudrunFile, iterator=None):
    PROCESS = "gudrun_dcs"

    if hasattr(sys, '_MEIPASS'):
        gudrun_dcs = os.path.join(sys._MEIPASS, f"{PROCESS}{SUFFIX}")
    else:
        gudrun_dcs = utils.resolve(
            os.path.join(
                config.__rootdir__, "bin"
            ), f"{PROCESS}{SUFFIX}"
        )

    if not os.path.exists(gudrun_dcs):
        return (-1, "MISSING_BINARY")

    with tempfile.TemporaryDirectory() as tmp:
        path = gudrunFile.outpath
        gudrunFile.setGudrunDir(tmp)
        path = os.path.join(
            tmp,
            path
        )
        gudrunFile.save(
            path=os.path.join(
                gudrunFile.projectDir,
                f"{gudrunFile.filename}"
            ),
            format=enums.Format.YAML
        )
        gudrunFile.write_out(path)

        # Run gudrun
        result = subprocess.run(
            path
            [gudrun_dcs, path], cwd=tmp, capture_output=True, text=True
        )

        if iterator is not None:
            gudrunFile.gudrunOutput = iterator.organiseOutput()
        else:
            gudrunFile.gudrunOutput = gudrunFile.organiseOutput()

        gudrunFile.setGudrunDir(gudrunFile.gudrunOutput.path)
        return result


def purge(gudrunFile):
    PROCESS = "purge_det"

    if hasattr(sys, '_MEIPASS'):
        purge_det = os.path.join(sys._MEIPASS, f"{PROCESS}{SUFFIX}")
    else:
        purge_det = utils.resolve(
            os.path.join(
                config.__rootdir__, "bin"
            ), f"{PROCESS}{SUFFIX}"
        )
    if not os.path.exists(purge_det):
        return (-1, "MISSING_BINARY")

    with tempfile.TemporaryDirectory() as tmp:
        gudrunFile.setGudrunDir(tmp)
        gudrunFile.purgeFile.write_out(os.path.join(
            gudrunFile.instrument.GudrunInputFileDir,
            f"{PROCESS}.dat"
        ))

        result = subprocess.run(
            [purge_det, "purge_det.dat"],
            cwd=tmp,
            capture_output=True,
            text=True
        )

    gudrunFile.purgeFile.organiseOutput()

    gudrunFile.setGudrunDir(
        gudrunFile.projectDir)

    return result
