# GudPy

_Last Release: 0.5.0, Monday 18th March 2024_

_Release Build::_ [![Release Build Status](https://github.com/disorderedmaterials/GudPy/actions/workflows/release.yml/badge.svg)](https://github.com/disorderedmaterials/GudPy/actions/workflows/release.yml)
_Development Build::_ [![Development Build Status](https://github.com/disorderedmaterials/GudPy/actions/workflows/continuous.yml/badge.svg)](https://github.com/disorderedmaterials/GudPy/actions/workflows/continuous.yml)

Python-based Batch Processing and Alternative GUI for the Gudrun software by A. K. Soper (https://github.com/disorderedmaterials/Gudrun).

GudPy offers a range of additional functionality unavailable in the Gudrun Java GUI, whilst also making some existing functionality/workflows easier to perform/carry-out. For further reference, you can visit the Gudrun manual.

## Running GudPy
### IDAaaS
The continuous build is released on IDAaaS on a nightly basis, this is where you can find the most cutting-edge (yet experimental) version of GudPy.
For development on IDAaaS make sure you use `python3.11` (the system default is 3.6). You will also need to install a higher version of PySide6 (e.g. 6.5.0) with version 3.11 of Python as well as `xcb-util-cursor.x86_64` in order for the xcb platform plugin to function correctly.
### Stable Release
Stable releases are available on the [release page](https://github.com/disorderedmaterials/GudPy/releases).
### From Source
Requires `python>=3.8` and `pip`.
1. Clone the repository.
2. Download the latest [Gudrun binaries and startup files](https://github.com/disorderedmaterials/Gudrun/releases), and unzip/untar into the `bin` directory.
4. `python3 -m pip install -r requirements.txt`
5. Manually compile the resources: `pyside6-rcc gudpy/gui/widgets/resources/resources.qrc > gudpy/gui/widgets/resources/resources_rc.py`
6. `python3 gudpy`

## Additional functionality
### Components
- `Components` can be defined within the "Components" tab.
- These components can be used to define compositions of Sample throughout the GUI.
- Components can be created manually, or parsed from a chemical formula.
- When performing processing, the combination of components and ratios defined for each Sample composition, are converted to an exact composition.
- Sample compositions can be normalised to 1, for readability.
### Output
- The output of the most recent `process` can be seen in the `Output` tab.
- This includes the output of purging detectors, running Gudrun and each iteration workflow.
- The output is split into "General" output, and then output per-sample.
- In the case of iterations, the output is split per-iteration.
- This makes debugging much easier, since there is no need to refer to the terminal output.
- The output files produced by Gudrun are organised.
- In the simple case, the output for each sample is stored in a directory, with sub-directories for outputs/diagnostics.
- The sample parameters are also stored in said directory.
- When iterating, a root directory is created at each iteration, storing the output for each sample during that iteration.
- When performing Inelasticity Subtractions, this is separated into Q iterations and Wavelength iterations.
- This reduces cluttering in the input file directory, and aims to make output easier to traverse.
- The `Export Archive` menu option can be used to produce a zip archive of mint01 files and sample parameter files used to produce them.
### Plotting
- Unlike the Gudrun Java GUI, plots are embedded within GudPy.
- Plots are shown for each sample alongside their parameters. Each plot is relative to just that sample.
- The plotting mode can be changed easily using the combo box.
- Two plots can be shown, plotting different information.
- Plots can be resized (relative to eachother, and the sample parameter area) using the splitters.
- Plots can be copied to the clipboard by using the context menu, or the device-specific native keyboard copy shortcut.
- Plots for all samples can be found in the "Plot Results" tab.
- Plots are updated between runs.
### Results
- The results of Gudrun are displayed alongside the plots for each sample.
- This includes the DCS Level, Error and Suggested Tweak Factor.
- Before running, the expected DCS level is computed and displayed - this is updated as you alter the sample composition, and is calculated as such: `average bound scattering cross section / 4.0 / pi` .
### Quality of life
- New input files can be created using Instrument configurations.
- The clear heirarchy of objects can be manipulated easily using the context menu or device-specific native keyboard shortcuts. This includes cutting, copying, pasting, duplicating, inserting, deleting etc.
- Fourier Transform parameters can be defined for containers when "running as sample".
- Warnings are produced if a purge has not been performed, before running Gudrun.
- Instrument configurations come with a "good detector threshold" - if the number of detectors that make it through a purge are not within this threshold, then a warning is produced. The number of good detectors is also shown at the bottom of the "Instrument" page.
- The Packing fraction is shown for samples/containers in the GUI, and can be be used instead of/alongside the tweak factor.
### Further iteration workflows
#### Basic
These iteration workflows work similarly to iterating by tweak factor.
They iteratively run Gudrun, computing a coefficient, after each iteration, to apply to the target 'variable'.
This coefficient is the ratio of the produced DCS level against the expected DCS level (on a per-sample basis).
##### Iterate by density
- Performs `n` iterations of altering the density.
##### Iterate by thickness
 - Performs `n` iterations of altering the thickness. This is only valid for flatplate samples.
 - This is performed on both the upstream and downstream thickness.
##### Iterate by radius
 - Performs `n` iterations of altering the radius. This is only valid for cylindrical samples.
 - Can only be performed exclusively on the inner or outer radii.
#### Advanced
More advanced iteration workflows
##### Iterate by composition
 - Performs `n` iterations of altering the sample composition.
 - The pre-requisite to this iteration workflow, is that components have been defined and the target sample compositions have been defined using the components.
 - This iteration workflow can be performed on one or two components within a sample composition.
 - It iterates using an algorithm based on the `golden-section search`.
 - In the case of a single component it balances the ratio of that component against the others in the composition.
 - For two components, it balances the ratios of the two against eachother, without altering the total number of molecules in the composition.
 - Since this can be a particularly slow workflow, a convergence tolerance can be defined.
### Batch Processing
GudPy includes a Batch Processing pipeline, that is flexible and can interface with basic iteration workflows.
Outputs a diagnostics file which provides information into batch sizes, contents and final values (when iterating).
#### Basic
 - Process samples using a defined `batch size` and `step size`.
 - Datafiles are split into batches of size `batch size`.
 - The next batch begins a `step size` after the beginning of the first batch.
### Iterative
 - Process samples as in the basic case, but perform iterations.
 - Can iterate by tweak factor, thickness, inner/outer radius and density.
 - Iterate for `n` iterations, or until the error is within the optional convergence tolerance. 