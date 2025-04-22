# geoFoils
Paul Dechamps, 2024.

`geoFoils` is a tool used to write `.geo` files (gmsh) for the softwares [_DARTFLO_][dartflo-repo] and [_BLASTER_][blaster-repo].
The code only works for 2D airfoils and generates `.geo` files with adapted mesh parameters that can readily be used like in the test cases present in the software. The script `ransFoils.py` can be used to generate an unstructured mesh in a circular domain with a boundary layer mesh near the airfoil. To generate CFD meshes around lifting surfaces in 3D, use [_GmshCFD_][gmshcfd-repo] (@acrovato).

## Airfoil type

Only **sharp trailing edge airfoils** can be used (to form the wake). The airfoil must be formatted in **seilig format**.

Airfoil data can be downloaded from [_Airfoil Tools_][airfoiltools-website] or found in the [_UIUC database_][uiuc-website].

A good practice is to send the airfoil to the plotter in Airfoil Tools (if possible) and impose the parameters and the trailing edge type.

## Execution

To execute the code, use the following command line

`python3 geoFoils.py path/to/airfoil.dat`

The additional argument `--name` can be used to define the name of the output `.geo` file.

The additional argument `--gr` can be used convert to the farfield mesh size parameter to the growth ratio of the elements size. In that case, msF is computed using the following formula.

$$ms_{F} = ms_{Le} g_r^{(n - 1)},$$

where $ms_F$ is the farfield mesh size, $ms_{Le}$ is the leading edge mesh size, $g_r$ is the growth ratio and

$$n = \frac{\log_{10}(1 - \frac{(1 - g_r) L_x}{ms_{Le}})}{\log_{10}(g_r)}.$$

with $L_x$ the domain length in the $x$ direction, defined by xLgt.

The output file is written in a workspace/ folder.

### Example

The following line will generate a `.geo` file for the NACA 0012 airfoil

`python3 geoFoils.py foils/n0012_sharp.dat --name naca0012_airfoil --gr=True`


## Required packages

The code requires the following packages (author's version)
- python3 (3.11.8)
- numpy (1.26.1)
- pandas (2.1.3)
- gmsh (4.12.2)

### Remark

Numpy can be used instead of pandas to read input files as long as the airfoil file is formatted correctly (*i.e.* no double space between columns)

Replace l.18 & 19 by l.20 in geoFoils.py.




[blaster-repo]: https://gitlab.uliege.be/am-dept/blaster
[dartflo-repo]: https://gitlab.uliege.be/am-dept/dartflo
[gmshcfd-repo]: https://github.com/acrovato/gmshcfd
[airfoiltools-website]: http://airfoiltools.com/
[uiuc-website]: https://m-selig.ae.illinois.edu/ads/coord_database.html