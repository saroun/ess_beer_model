# -*- coding: utf-8 -*-
"""Functions for running McStas simulations for default BEER operation modes.

Usage
-----

import beer.mcstas as mcstas

# configure workspace and McStas environment 
mcstas.configure(workpath='my_path',
                 PATH='/usr/bin', 
                 MCSTAS='/usr/share/mcstas/3.4')

# create instrument file 
mcstas.create_instrument()

# compile instrument file
mcstas.compile_instrument(force=True)

# run simulation for one modes
result = mcstas.execute(modes='PS2', n=1e7, plot=True)

# or run simulation for selected modes
result = mcstas.execute(modes='F0,F1', n=1e7, plot=True)

# or run simulation for all modes 
import beer.modes as bmodes
result = mcstas.execute(modes=bmodes.getModeKeys(), n=1e7, plot=True)

# to replot results:  
mcstas.plot_result(result, title='Test simulation', pdf='myresult')

# create instrument file 
mcstas.create_instrument()

# compile instrument file
mcstas.compile_instrument(force=True)

# run simulation for one modes
result = mcstas.execute(modes='PS2', n=1e7, plot=True)

# or run simulation for selected modes
result = mcstas.execute(modes='F0,F1', n=1e6, plot=True)

# or run simulation for all modes 
import beer.modes as bmodes
result = mcstas.execute(modes=bmodes.getModeKeys(), n=1e7, plot=True)

# to replot results:  
mcstas.plot_result(result, title='Test simulation', pdf='myresult')



# Simulation using an instrument template provided by user
mcstas.create_instrument(template='BEER_user', 
                         inpath='.', 
                         instname='BEER_Vexperiment')
mcstas.compile_instrument(force=True)
result = mcstas.execute(modes='F0', n=1e6, plot=True, monoutputs=1)

# Only generate the instrument file
mcstas.conf.parseTemplate(instname='BEER_user', 
                          template='BEER_user',
                          inpath='.',
                          outpath='.')

------------------------------------------------------
Created on Mon Jul 20 16:58:52 2020
@author: J. Saroun, saroun@ujf.cas.cz
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez 
"""


import beer.mcstas.run as _exe

_IS_MCSTAS=None
_IS_MCSTAS_CONFIG=None


def configure_workspace(**kwargs):
    """Set McStas instrument project configuration.
    
    Create workspace files and directories if needed. 
    
    Shortcut to :func:`beer.mcstas.run.setConfig`.
    
    Parameters
    ----------
    workpath : str
        Root project directory with instrument data and output. 
        If not defined, the work path is set in the user profile (home) 
        directory (./beer_optics/mcstas) 
    instname : str
        Name of the McStas instrument to run. Default is `BEER_reference` 
        with the template defined in resources.
    outpath : str
        Path where McStas saves results (mode name is added as a subdirectory).
        If relative, it is assumed to be a child of `workpath`. 
    
    """
    _exe.setConfig(**kwargs)
    _exe.createWorkspace() 
    
    
def configure_mcstas(**kwargs):
    """Set McStas compiler configuration.
    
    This funciton allows to set environment variables needed by McStas compiler
    if not defined by the system environment. 
    
    Shortcut to :func:`beer.mcstas.run.setMcStas`.
    
    Parameters
    ----------
    version : int
        Version 2 or 3 of McStas
    PATH:
        Path to mcstas binary, to be added to the environment variable PATH
    MCSTAS:
        Path to McStas component libraries
    MCSTAS_CC:
        Environment variable MCSTAS_CC (c compiler, e.g. gcc)
    MCSTAS_CFLAGS:
        Environment variable MCSTAS_CFLAGS, options for C compiler
    
    """
    _exe.setMcStas(**kwargs)
    

def verify_workspace():
    """Check the workspace and McStas configurations."""
    global _IS_MCSTAS_CONFIG,_IS_MCSTAS
    # Check the configuration
    _IS_MCSTAS_CONFIG = _exe.verifyConfig()
    _IS_MCSTAS = _exe.verifyMcStas()
    
    
def configure(version=3, PATH='', MCSTAS='', MCSTAS_CC='', 
              MCSTAS_CFLAGS='', workpath='', instname='BEER_reference', 
              outpath='out'):
    """Configure the instrument project workspace and McStas compiler.
    
    - Create workspace files and directories if needed and populate them with 
      required content.
    - Set environment for McStas compiler.
    
    This function encapsulates all configuration tasks required to compile 
    and run McStas instrument simulation.

    Parameters
    ----------
    version : int
        Version 2 or 3 of McStas
    PATH:
        Path to mcstas binary, to be added to the environment variable PATH
    MCSTAS:
        Path to McStas component library (lib) 
    MCSTAS_CC:
        Environment variable MCSTAS_CC (c compiler, e.g. gcc)
    MCSTAS_CFLAGS:
        Environment variable MCSTAS_CFLAGS, options for C compiler        
    workpath : str
        Root project directory with instrument data and output. 
        If not defined, the work path is set in the user profile (home) 
        directory (./beer_optics/mcstas) 
    instname : str
        Name of the McStas instrument to run. Currently only `BEER_reference` 
        is defined in resources.
    outpath : str
        Path where McStas saves results (mode name is added as a subdirectory).
        If relative, it is assumed to be a child of `workpath`. 

    """
    configure_mcstas(version=version,
                        PATH=PATH, 
                        MCSTAS=MCSTAS, 
                        MCSTAS_CC=MCSTAS_CC,
                        MCSTAS_CFLAGS=MCSTAS_CFLAGS)
    configure_workspace(workpath=workpath, 
                     instname=instname, 
                     outpath=outpath)
    verify_workspace()


def create_instrument(version=None, template=None, instname='', inpath=None, 
                      outpath=None, GPU=True, **options):
    """Create McStas instrument file from a template.
    
    If not defined the template is derived from the instrument name. 
    Default is `BEER_reference`.
    The created file is saved in the workspace as defined by :func:`configure`. 
    
    The template file is searched for in the package resources, 
    unless `inpath` is defined.
    
    Parameters
    ----------
    version : int
        McStas version, 2 or 3. The version passed to configure is used by 
        default.
    template : str
        Template name. If not defined, derive one from the instrument name, 
        McStas version and the GPU value.
    instname : str
        Instrument name (without instr extension). If empty, use the name 
        defined by :func:`configure_workspace`
    inpath : str
        Path where to search for instrument template. If not defined, use
        package resources.
    outpath : str
        Path where to save the instrument file. If None, use the workspace setting. 
    GPU : bool
        Set true to use the template with GPU-related definitions
    """    
    config = _exe.getConfig()
    if not instname:
        instname = config['INSTR']
    else:
        _exe.setConfig(instname=instname)
    if not version in [2,3]:
        version = _exe.getMcStas()['version']
    if template is None:
        template = instname
        if version==2:
            template += '_2x'
        elif version==3:
            template += '_3x'
        if GPU:
            template += '_GPU'
    _exe.createInstrument(template=template, 
                          inpath=inpath,
                          outpath=outpath,
                          instname=instname,
                          **options)


def compile_instrument(force=False, mpi=0):
    """Compile default instrument file.
    
    Parameters
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
        print('Try to run {}.configure() again.'.format(fn))
        return
    
    if not _IS_MCSTAS:
        print('ERROR: McStas compiler configuration failed?')
        print('Try to run {}.configure() again.'.format(fn))
        return

    out = _exe.compileInstrument(mpi=mpi, verify=False)
    if not out:
        print('WARNING: could not compile instrument file')
    

def execute(modes=None, n=1e5, plot=False, docompile=False, mpi=0, quiet=False, 
            **params):
    """Run McStas simulation for given BEER modes and number of neutrons.
    
    Parameters
    ----------
    modes: str or list
        List of ID's (or a single ID) for BEER modes to be simulated. 
        The list can also be passed as a comma-separated string.
        If modes not defined or equal 'all', run all pre-defined modes.
        The modes are defined in beer.modes.
        Use :func:`beer.modes.listModes` to print a list.
        Use :func:`beer.modes.getModeKeys` to get a list of ID's.
    n: int
        Number of neutrons to run
    plot: boolean
        Plot results after simulation.
    docompile: boolean
        Create and compile the instrument file (BEER_reference.instr)
        before simulation. Requires McStas installed and configured.
        See :func:`configure_mcstas`.
    mpi : int
        Number of CPU cores for MPI mode.
    params
        Instrument parameters.
        
    Return
    ------
    
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
        print('Try to run {}.configure_mcstas() again.'.format(fn))
        return

    if docompile and (not _IS_MCSTAS):
        print('ERROR: McStas compiler configuration failed?')
        print('Try to run {}.configure_mcstas() again.'.format(fn))
        return

    if docompile:
        # compile
        out = _exe.compileInstrument(mpi=mpi, statinfo=False, shielding=False, 
                                      verify=False)
        if not out:
            print('WARNING: could not compile instrument file.')
        
    counts = max(10000,n)
    # derive timeout from counts
    timeout = int(counts/1e8*3600)+60

    # define modes to run  
    modeid = ''
    if not modes or modes =='all':
        modes = bmodes.getModeKeys()
    elif isinstance(modes,str):
        ms = modes.split(',')
        if len(ms)>1:
            modes = ms
        else:
           modeid = modes
    datas = None
    # execute simulation for a single mode:
    if modeid:
        out = _exe.runSimulation(modeid, mpi=mpi, n=counts, quiet=quiet, **params)
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
        out = _exe.runModes(modes=modes, mpi=mpi, counts=counts, timeout=timeout,
                            **params)
        if out:
            # retrieve results:
            datas = _exe.processResults(modes)
            if plot:
                if isinstance(plot, str):
                    fout = plot
                else:
                    fout = 'results'
                try:
                    _exe.plotResults(datas, title='McStas', pdf=fout)
                except Exception as e:
                    print(e)
        else:
            print('Simulation not completed.')
    return datas


def plot_result(datas, title='McStas', pdf=''):
    """Plot results retrieved by :func:`execute`.
    
    Parameters
    ----------
    datas: 
        Result of :func:`execute`
    title: str
        Title to be shown on graph
    pdf: str
        File name to export (pdf format, without extension).
        Leave empty to suppress file export.
        
    """
    _exe.plotResults(datas, title=title, pdf=pdf)

