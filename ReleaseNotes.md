Release of GudPy for version 1.0. This is the first major version.

This version of GudPy supplies a refined, rigid, GUI that offers all basic functionality of the Java Gudrun version.

On top of this, the following additional features have been added:

 - Objectify Composition - components can be defined and named and then used for defining sample compositions using ratios. These components can also be defined and their composition determined from a chemical formula.
 - Plotting - Various plots have been implemented. Currently the focus is on mdcs01/mint01 and mgor01/mdor01 data. These plots can be viewed logarithmically. On each sample page, if the aforementioned data files exist, they will be plotted.
 - Results/Communication of purge_det/gudrun_dcs - Progress bars have been implemented for all tasks in the GUI involving purge_det or gudrun_dcs. The number of detectors that made it through the purge are displayed after running purge_det. The results of gudrun_dcs for each sample, as outputted in the .gud files, are presented on each sample page.
 - Iteration - Iteration is possible through the GUI.
 - Qt6 - We migrated from PyQt5 to PySide6 to use Qt6.
