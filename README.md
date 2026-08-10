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
The latest versions of these tables are stored in the repository (see ./data/*)

    import beer
    beer.reportTables(outdir='') # you can specify output directory

Calculate and plot chopper transmission functions for various operation modes:

    beer.reportChoppers(outdir='')

Plot profiles of neutron guides in given coordinate system. 
Options are: ISCS or FP (focal point for W2 beamport):

    beer.plotGuides(outdir='', coord='ISCS')

### Run simulation with McStas (if installed):

The latest BEER instrument file for the primary beamline (source to sample) is available at 
[beer/resources/BEER_reference.instr](beer/resources/BEER_reference.instr). The `beer` package can be used for running the simulations as follows.

Try the script [run_mcstas.py](./run_mcstas.py), e.g.:

    python run_mcstas.py n=1e6 modes=F0 force=1 plot=1 workpath=my_path

or use the beer.mcstas package:

    import beer.mcstas as mcstas

    # configure workspace and McStas environment 
    mcstas.configure(workpath='my_path',
                    PATH='/usr/bin', 
                    MCSTAS='/usr/share/mcstas/3.4')

    # create instrument file 
    mcstas.create_instrument()

    # compile instrument file
    mcstas.compile_instrument(force=True)

    # run simulation for selected modes
    result = mcstas.execute(modes='F0,F1', n=1e6, plot=True)

    # or run simulation for all modes 
    result = mcstas.execute(modes='all', n=1e7, plot=True)

    # to replot results:  
    mcstas.plot_result(result, title='Test simulation', pdf='myresult')

    # or run simulation for selected modes
    result = mcstas.execute(modes='F0,F1', n=1e6, plot=True)

    # or run simulation for all modes 
    import beer.modes as bmodes
    result = mcstas.execute(modes=bmodes.getModeKeys(), n=1e7, plot=True)

    # Simulation using an instrument template provided by user
    mcstas.create_instrument(template='BEER_user', 
                            inpath='.', 
                            instname='BEER_Vexperiment')
    mcstas.compile_instrument(force=True)
    result = mcstas.execute(modes='F0', n=1e6, plot=True, monoutputs=1)

    # Only generate the instrument file
    mcstas.conf.parseTemplate(instname='my_instrument_name', 
                            template='my_instrument_template',
                            inpath='.',
                            outpath='.')

### Run simulations with SIMRES (if installed):

First define the JRE environment variable to point to the Java RE interpreter.

Then try the script [run_simres.py](./run_simres.py), e.g.:

    python run_simres.py runetup=1 modes=F0,PS1 n=1e4 

or use the beer.simres package:
    
    import beer.simres as simres
    import beer.modes as bmodes

    # Configure environment to define workspace directory.
    # Optionally, you van also set `java` path and `simresdir` to define the 
    # JRE interpreter and SIMRES installation directory, respectively.
    simres.configure(workpath='my_path')

    # Create script `BEER_setup.inp`  for updating instrument configuration. 
    # Set scriptonly=False to also start SIMRES and run the script.
    simres.update(scriptonly=False)

    # Run a single simulation for given BEER operation mode
    simres.execute(modes='PS2', n=10000, plot=True)

    # Run simulation for all reference modes (takes a long time):
    simres.execute(modes=bmodes.getModeKeys(), n=10000, plot=True)

