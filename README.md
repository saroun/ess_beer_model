# BEER_optics

Neutron optics model for the diffractometer BEER at the European Spallation Source.  
Author: Jan Saroun, saroun@ujf.cas.cz  
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez, http://www.ujf.cas.cz

Repository: https://bitbucket.org/saroun/beer_optics 

## Summary
This Python package provides the definition of neutron optics geometry for the diffractometer BEER@ESS and associated tools:  
- Export of neutron beam axis coordinates and various functions for coordinate transformations between target, beamport and instrument reference frames.  
- Export of the table of neutron optics components (a text version of the document `ESS-0478295 - BEER Optics Specifications`)  
- Definition of components settings for reference operation modes of BEER (see `ESS-0238217 - Optics Report for the BEER Instrument`)  
- Calculation of chopper transmission functions for these reference modes  
- Binding to the simulation program `McStas`: export of instrument configuration files, functions for running simulations and plotting results.   
- Binding to the simulation program `SIMRES`: export of input scripts, functions for running simulations and plotting results.  

### See also:

Diffractometer BEER: https://europeanspallationsource.se/instruments/beer  
McStas: http://www.mcstas.org  
SIMRES: https://github.com/saroun/simres  

## Quick guide

Install:

    # from root package directory call
    pip install -e .
    # check pip docs for other ways of installation

Get beam axis, beam size and coordinate conversions:

    import beer.geometry as bg

    # get beam axis coordinates for given distance. The result is converted 
    # to required coordinate system (ISCS, TCS or FP). Distance is always defined
    # as x_ISCS.
    r_ISCS = bg.beamAxis(145000, coord='ISCS')

    # get beam axis angle in [rad] with respect to x-axis of given coordinate system
    angle = bg.beamAngle(145000, coord='FP')

    # get beam size at given distance: left, right, top, bottom, width and height, converted to required coordinates.
    [left, right, top, bottom, width, height] = bg.beamSize(145000, coord='FP')

    # convert a point from ISCS to TCS coordinates
    r_TCS = bg.ISCS2TCS(r_ISCS)
    # or to FP (W2 focal point) coordinates
    r_FP = bg.ISCS2FOC(r_ISCS)

Export configuration tables for BEER into given directory:  
`BEER_components.txt`, the contents of the components table, ESS-0478295.  
`BEER_beam.txt`, a table with beam axis coordinates in three reference frames (TCS, W2, ISCS).  
`BEER_modes.txt`, reference operation modes with corresponding components settings.

    import beer
    beer.reportTables(outdir='') # you can specify output directory

Calculate and plot chopper transmission functions for various operation modes:

    beer.reportChoppers(outdir='')

Plot profiles of neutron guides in given coordinate system. 
Options are: ISCS or FP (focal point for W2 beamport):

    beer.plotGuides(outdir='', coord='ISCS')

### Run simulation with McStas (if installed):

    import beer.mcstas as mcstas
    import beer.modes as bmodes

    # Configure environment to define workspace directory, 
    # path to mcstas compiler and path to McStas components library, e.g.
    mcstas.configure(workpath='mypath', BINPATH=r'C:\mcstas-2.6\bin', MCSTAS=r'C:\mcstas-2.6\lib')

    # Generate McSTas instrument file:
    mcstas.createInstrument(statinfo=False, shielding=False)

    # Compile the instrument file (force=true to force recompiling):
    mcstas.compileInstrument(force=False)

    # Run simulation of a single mode defined by ID string:
    mcstas.execute(modes='F0', n=1e7, plot=True)

    # Run simulation for all reference modes (takes a long time):
    mcstas.execute(modes=bmodes.getModeKeys(), n=1e7, plot=True)

### Run simulations with SIMRES (if installed):

    import beer.simres as simres
    import beer.modes as bmodes

    # Configure environment to define workspace directory and path to `java` command 
    simres.configure(workpath='mypath', java='java')

    # Create script `BEER_setup.inp`  for updating instrument configuration. 
    # Set scriptonly=False to also start SIMRES and run the script.
    simres.update(scriptonly=False)

    # Run a single simulation for given BEER operation mode
    simres.execute(modes='PS2', n=10000, plot=True)

    # Run simulation for all reference modes (takes a long time):
    simres.execute(modes=bmodes.getModeKeys(), n=10000, plot=True)

