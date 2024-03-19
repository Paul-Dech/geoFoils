# geoFoils
Paul Dechamps, 2024.

geoFoils is a tool used to write .geo files (gmsh) for the softwares [_DARTFLO_][dartflo-repo] and [_BLASTER_][blaster-repo].
The code only works for 2D airfoils and generates geo files with adapted mesh parameters that can readily be used like the test cases present in both softwares. To generate CFD meshes around lifting surfaces in 3D, use [_GmshCFD_][gmshcfd-repo] (@acrovato).

## Airfoil type

Only **sharp trailing edge airfoil** can be used (to form the wake). The airfoil must be formated in **seilig format**.

Airfoil data can be downloaded from [_Airfoil Tools_][airfoiltools-website] of found in the [_UIUC database_][uiuc-website].

A good practice is to send the airfoil to the plotter in Airfoil Tools (if possible) and impose the parameters and the trailing edge type.


## Required packages

The code requires the following packages
 - python3 (The code was written and tested with python@3.11.8)
- numpy (1.26.1)
- pandas (2.1.3) (you can use numpy if your airfoil file is formatted correctly (i.e no double space between columns) (geoFoils.py l.18-19 -> l.20))
- gmsh (4.12.2) to read the output files




[blaster-repo]: https://gitlab.uliege.be/am-dept/blaster
[dartflo-repo]: https://gitlab.uliege.be/am-dept/dartflo
[gmshcfd-repo]: https://github.com/acrovato/gmshcfd
[airfoiltools-website]: http://airfoiltools.com/
[uiuc-website]: https://m-selig.ae.illinois.edu/ads/coord_database.html