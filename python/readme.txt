Python scripts for BEER geometry and configuration files.
=========================================================

Beam geometry and components definitions and functions:
========================================================
BEERgeometry.py:
Primary source of BEER beam geometry (beam axis and neutron optics profile). It is used by all other scripts producing components tables, beam axis table, or configuration files for simulations. It also defines coordinate systems and provides function for coordinate conversions:
TCS: Target coordinate system
FP (or FOC): W2 beamport coordinates (origin at the moderator focal point)
ISCS: Instrument coordinates

BEERcomponents.py:
Defines the components of BEER with basic parameters, which are stored in the hash map BEER[]. The command
table=writeComponents(file = 'components_list.txt', gaps=True)
can be used to export the table of components ready for copy/paste into the official BEER component list (ESS-0478295)

BEERmodes.py:
Defines a set of reference operation modes for BEER. It is used by BEER_mcstas.py to create the simulation model for McStas, "BEER_primary.instr" .

Other useful scripts:
===========================
BEER_beamaxis.py:
Calculates beam axis positions at various critical points. It also exports a detailed table of the beam axis in the three coordinate systems.

BEER_simres.py:
Generates input script "simres_setup.inp" for SIMRES (ray-tracing simulation program). It assumes that the sequence of components in SIMRES is already defined with cooresponding names and component types. Running the script then updates all component parameters according to the current version of BEERgeometry.py and BEERcomponents.py.

BEER_mcstas.py:
Generates McStas model of BEER (source to sample). The file "BEER_primary.instr" is generated from the template "BEER_primary.instr.template" by replacing specific tags by the code with actual BEER setup, using the definition in  BEERgeometry.py and BEERcomponents.py. See the comments in the file for explanation of parameters etc. The model permits to easily select one of the 13 pre-defined reference modes as they are defined in the script BEER_modes.py.

BEER_beam_calc.py:
Various calculations of beam slices (coordinates of the corners) etc. May serve as an example for other calculations ... 

guide_profiles.py:
Collects files with guide profiles exported from SIMRES and creates plots in FP/W2 coordinates.
