# -*- coding: utf-8 -*-
"""

Encapsulates functions for running McStas simulations for 
default BEER operation modes. 

Usage:
------

    import beer.mcstas as mcstas

    # configure workspace and McStas environment 
    mcstas.configure(workpath='mypath', BINPATH='/usr/bin', MCSTAS='/usr/share/mcstas/2.6')

    # create instrument file 
    mcstas.createInstrument(statinfo=False, shielding=False)

    # compile instrument file
    mcstas.compileInstrument(force=False)

    # run simulation for one modes
    result = mcstas.execute(modes='PS2', n=1e7, plot=True)

    # or run simulation for all modes 
    import beer.modes as bmodes
    result = mcstas.execute(modes=bmodes.getModeKeys(), n=1e7, plot=True)

    # to replot results:  
    mcstas.plotResults(result, pdf='myresult')

------------------------------------------------------
Created on Mon Jul 20 16:58:52 2020
@author: J. Saroun, saroun@ujf.cas.cz
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez 
"""


import beer.mcstas.run as _exe

_IS_MCSTAS=None
_IS_MCSTAS_CONFIG=None


def configure(workpath='', BINPATH='', MCSTAS='', MCSTAS_CC='gcc', 
                 MCSTAS_CFLAGS='-O2'):
    """
    Set environment for McStas.
    
    Must be executed before mcstasRun().
    
    Parameters:
    -----------
    workpath:
        Working directory. If empty, creates one in user's profile.
    BINPATH:
        Add a path to mcstas compiler to the environment variable PATH,
        e.g. C:\mcstas-2.6\bin
    MCSTAS:
        Set environment variable MCSTAS: McStas path, e.g. C:\mcstas-2.6\lib
    MCSTAS_CC:
        Set environment variable MCSTAS_CC (c compiler, e.g. gcc)
    MCSTAS_CFLAGS:
        Set environment variable MCSTAS_CFLAGS, options for C compiler
    """
    global _IS_MCSTAS_CONFIG,_IS_MCSTAS
    _exe.setMcStas(PATH=BINPATH, 
              MCSTAS=MCSTAS,
              MCSTAS_CC=MCSTAS_CC,
              MCSTAS_CFLAGS=MCSTAS_CFLAGS
              )
    # Set the configuration
    # use `workpath=path` parameter to define a custom workspace directory 
    _exe.setConfig(workpath=workpath)
    # Check the configuration
    _IS_MCSTAS_CONFIG = _exe.verifyConfig()
    _IS_MCSTAS = _exe.verifyMcStas()


def createInstrument(statinfo = False, shielding=False, inpath=None):
    """ Creates McStas instrument file from a template corresponding
    to the instrument name. Default is `BEER_reference`.
    The created file is saved in the workspace as defined by setConfig(). 
    
    The template file is searched for in the package resources, 
    unless `inpath` is defined.
    
    Parameters:
    ----------
    statinfo: boolean
        if true, the simulation will produce tracing statistics
    shielding: boolean
        if true, the instrument file will include shielding logger
    inpath: str
        path where to search for instrument template. If not defined, use
        package resources.
    """    
    _exe.createInstrument(statinfo=statinfo, shielding=shielding, inpath=inpath)


def compileInstrument(force=False):
    """
    Compile default instrument file. 
    
    Parameters:
    ----------
    force: boolean
        if false, compile only if the target executable does not exist
    
    """
    import os
    global _IS_MCSTAS_CONFIG, _IS_MCSTAS
    
    if not force:
        exename = _exe.verifyInstrument(verbose=0)
        if exename:
            print('File "{}" already exists.'.format(exename))
            print('Compilation skipped.')
            return
    
    fn = os.path.basename(__file__)
    if (_IS_MCSTAS_CONFIG is None) or (_IS_MCSTAS is None):
        msg = 'ERROR: workspace and/or McStas not configured.'
        msg += 'Trying to use default settings.\n'
        print(msg)
        configure()
    
    if not _IS_MCSTAS_CONFIG:
        print('ERROR: workspace configuration failed?')
        print('Try to run {}.mcstasConfig() again.'.format(fn))
        return
    
    if not _IS_MCSTAS:
        print('ERROR: McStas compiler configuration failed?')
        print('Try to run {}.mcstasConfig() again.'.format(fn))
        return

    out = _exe.compileInstrument(verify=False)
    if not out:
        print('WARNING: could not compile instrument file')
    

def execute(modes=None, n=1e5, plot=False, docompile=False):
    """
    Run McStas simulation for given BEER modes and number of neutrons.
    
    Parameters:
    ----------
    modes: str or list
        List of ID's (or a single ID) for BEER modes to be simulated. 
        The modes are defined in beer.modes.
        Use beer.modes.listModes() to print a list.
        Use beer.modes.getModeKeys() to get a list of ID's.
    n: int
        Number of neutrons to run
    plot: boolean
        Plot results after simulation.
    docompile: boolean
        Create and compile the instrument file (BEER_reference.instr)
        before simulation. Requires McStas installed and configured.
        See mcstasConfigure().
        
    Returns:
    -------
    
    List of beer.mcplot.Data1D objects with results.
        
    """
    import os
    import beer.modes as bmodes
    global _IS_MCSTAS_CONFIG, _IS_MCSTAS
    
    fn = os.path.basename(__file__)
    if (_IS_MCSTAS_CONFIG is None) or (_IS_MCSTAS is None):
        msg = 'ERROR: workspace and/or McStas not configured.'
        msg += 'Trying to use default settings.\n'
        print(msg)
        configure()
        
    if not _IS_MCSTAS_CONFIG:
        print('ERROR: workspace configuration failed?')
        print('Try to run {}.mcstasConfig() again.'.format(fn))
        return

    if docompile and (not _IS_MCSTAS):
        print('ERROR: McStas compiler configuration failed?')
        print('Try to run {}.mcstasConfig() again.'.format(fn))
        return

    if docompile:
        # compile
        out = _exe.compileInstrument(statinfo=False, shielding=False, 
                                      verify=False)
        if not out:
            print('WARNING: could not compile instrument file.')
        
    counts = max(10000,n)
    # derive timeout from counts
    timeout = int(counts/1e8*3600)+60

    # define modes to run  
    modeid = ''
    if not modes:
        modes = bmodes.getModeKeys()
    elif isinstance(modes,str) and (not modes=='DS1'):
        modeid = modes
    datas = None
    # execute simulation for a single mode:
    if modeid:
        out = _exe.runSimulation(modeid, n=counts)
        if out:
            # process output files and get a list of data objects
            datas = _exe.processRun(modeid)
            # plot the retrieved data
            if plot:
                _exe.plotResults(datas, title='McStas '+modeid, pdf=modeid)
        else:
            print('Simulation not completed.')

    # execute simulation for multiple modes:
    else:
        out = _exe.runModes(modes=modes, counts=counts, timeout=timeout)
        if out:
            # retrieve results:
            datas = _exe.processResults(modes)
            # plot the retrieved results:
            if plot:
                _exe.plotResults(datas, title='McStas', pdf='results')
        else:
            print('Simulation not completed.')
    return datas

