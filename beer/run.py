# -*- coding: utf-8 -*-
"""
Encapsulates functions for running McStas and SIMRES simulations for 
default BEER operation modes. 

Usage:
------

**McStas**

import beer.run as do

# configure McStas environment 
 
do.mcstasConfig(BINPATH='/usr/bin', MCSTAS='/usr/share/mcstas/2.6')

# create instrument file 
import beer.mcstasexe
beer.mcstasexe.createInstrFile(statinfo=False, shielding=False)

# compile instrument file  

do.mcstasCompile(force=False)

# run simulation for one modes

result =do.mcstasRun(modes='PS2', n=1e7, plot=True)

# or run simulation for all modes 
 
import beer.modes

result = do.mcstasRun(modes=beer.modes.getModeKeys(), n=1e7, plot=True)

# to replot results:  

do.plotResults(result, pdf='myresult')


**SIMRES**

import beer.run as do

# configure SIMRES environment (provide path to java command)

do.simresConfig(java='java')

# run simulation for one mode

result = do.simresRun(modes='PS2', n=10000, runsetup=False, plot=True)

# or run simulation for all modes

import beer.modes

result = do.simresRun(modes=beer.modes.getModeKeys(), n=10000, runsetup=False, plot=True)

# replot resutls:

do.plotResults(result, pdf='myresult')

# If beamline configuration has changed, you can update the instrument file:

import beer.simresexe as simexe

simexe.runSetup()

----------------------------------------
Created on Mon Jul 13 17:07:39 2020
@author: J. Saroun, saroun@ujf.cas.cz
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez 
"""

import os
import beer.modes as BMOD
import beer.mcstasexe as mcexe
import beer.simresexe as simexe

_IS_MCSTAS=None
_IS_MCSTAS_CONFIG=None
_IS_SIMRES=None
_IS_SIMRES_CONFIG=None

def mcstasConfig(workpath='', BINPATH='', MCSTAS='', MCSTAS_CC='gcc', 
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
    mcexe.setMcStas(PATH=BINPATH, 
              MCSTAS=MCSTAS,
              MCSTAS_CC=MCSTAS_CC,
              MCSTAS_CFLAGS=MCSTAS_CFLAGS
              )
    # Set the configuration
    # use `workpath=path` parameter to define a custom workspace directory 
    mcexe.setMcStasConfig(workpath=workpath)
    # Check the configuration
    _IS_MCSTAS_CONFIG = mcexe.verifyConfig()
    _IS_MCSTAS = mcexe.verifyMcStas()


def mcstasCompile(force=False):
    """
    Compile default instrument file. 
    
    Parameters:
    ----------
    force: boolean
        if false, compile only if the target executable does not exist
    
    """
    global _IS_MCSTAS_CONFIG, _IS_MCSTAS
    
    if not force:
        exename = mcexe.verifyInstrument(verbose=0)
        if exename:
            print('File "{}" already exists.'.format(exename))
            print('Compilation skipped.')
            return
    
    fn = os.path.basename(__file__)
    if (_IS_MCSTAS_CONFIG is None) or (_IS_MCSTAS is None):
        msg = 'ERROR: workspace and/or McStas not configured.'
        msg += 'Trying to use default settings.\n'
        print(msg)
        mcstasConfig()
    
    if not _IS_MCSTAS_CONFIG:
        print('ERROR: workspace configuration failed?')
        print('Try to run {}.mcstasConfig() again.'.format(fn))
        return
    
    if not _IS_MCSTAS:
        print('ERROR: McStas compiler configuration failed?')
        print('Try to run {}.mcstasConfig() again.'.format(fn))
        return

    out = mcexe.compileInstrument(verify=False)
    if not out:
        print('WARNING: could not compile instrument file')
    

def mcstasRun(modes=None, n=1e5, plot=False, docompile=False):
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
    global _IS_MCSTAS_CONFIG, _IS_MCSTAS
    
    fn = os.path.basename(__file__)
    if (_IS_MCSTAS_CONFIG is None) or (_IS_MCSTAS is None):
        msg = 'ERROR: workspace and/or McStas not configured.'
        msg += 'Trying to use default settings.\n'
        print(msg)
        mcstasConfig()
        
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
        out = mcexe.compileInstrument(statinfo=False, shielding=False, 
                                      verify=False)
        if not out:
            print('WARNING: could not compile instrument file.')
        
    counts = max(10000,n)
    # derive timeout from counts
    timeout = int(counts/1e8*3600)+60

    # define modes to run  
    modeid = ''
    if not modes:
        modes = BMOD.getModeKeys()
    elif isinstance(modes,str) and (not modes=='DS1'):
        modeid = modes
    datas = None
    # execute simulation for a single mode:
    if modeid:
        out = mcexe.runSimulation(modeid, n=counts)
        if out:
            # process output files and get a list of data objects
            datas = mcexe.processRun(modeid)
            # plot the retrieved data
            if plot:
                mcexe.plotResults(datas, title='McStas '+modeid, pdf=modeid)
        else:
            print('Simulation not completed.')

    # execute simulation for multiple modes:
    else:
        out = mcexe.runModes(modes=modes, counts=counts, timeout=timeout)
        if out:
            # retrieve results:
            datas = mcexe.processResults(modes)
            # plot the retrieved results:
            if plot:
                mcexe.plotResults(datas, title='McStas', pdf='results')
        else:
            print('Simulation not completed.')
    return datas

#%% SIMRES

def simresConfig(workpath='', java='java', simresdir=''):
    """
    Set environment for SIMRES: workspace directory, java command and 
    optionally SIMRES installation directory. 
    
    Must be executed before calling simresRun().
    
    Parameters:
    -----------
    workpath: str
        Working directory. If empty, creates one in user's profile.
    java: str
        Command for calling Java (needed to launch simulation)
    simresdir: str
        Optional: provide path to SIMRES installation.
        If not defined, uses default: `/opt/simres` on Linux and 
        `%programfiles%\Restrax\Simres` on Windows.
    """
    global _IS_SIMRES_CONFIG,_IS_SIMRES
    
    # Generate and save SIMRES project configuration
    try:
        simexe.setSimresConfig(workpath=workpath, java=java)
        _IS_SIMRES_CONFIG = True
    except Exception as e:
        _IS_SIMRES_CONFIG = False
        print(e)
    
    # set path to SIMRES if requested
    if simresdir:
        path = os.path.normpath(simresdir)
        if os.path.isdir(path):
            simexe.setSimresPath(path)
    # Verify SIMRES and workspace configuration            
    _IS_SIMRES_CONFIG = simexe.verifyConfig(verbose=0)
    _IS_SIMRES = simexe.verifySimres() and simexe.verifyJava()


def simresRun(modes=None, n=10000, plot=False, runsetup=False):
    """
    Run simulation using SIMRES for given BEER modes and number of neutrons.
    simresConfig() must be executed before simresRun().
    
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
    runsetup: boolean
        Create and run input script for updating BEER instrument configuration
        according to actual beam geometry definition.
    
    Returns:
    -------
    
    List of beer.mcplot.Data1D objects with results.
    """
    
    global _IS_SIMRES_CONFIG, _IS_SIMRES
    fn = os.path.basename(__file__)
    if (_IS_SIMRES_CONFIG is None) or (_IS_SIMRES is None):
        msg = 'ERROR: workspace and/or SIMRES not configured.\n'
        msg += 'Trying to use default settings.\n'
        print(msg)
        simresConfig()
    
    if not _IS_SIMRES:
        msg = 'SIMRES or Java not installed?\n'
        msg += 'Use {}.simresConfig(simresdir=..., java=...) '.format(fn)
        msg += 'to define path to SIMRES installation and java command.\n'
        print(msg)
        return
    if not _IS_SIMRES_CONFIG:
        msg = 'Workspace configuration failed? \n'
        msg += 'Use {}.simresConfig(workpath=...) '.format(fn)
        msg += 'to define valid path to your workspace directory.\n'
        print(msg)
        return
        
    # run setup script if requested
    if runsetup:
        out = simexe.runSetup(verify=False)
        if not out:
            raise Exception('Cannot run setup script.')
    
    datas = None
    counts = max(500,n)
    # derive timeout from counts
    timeout = int(counts/10)+300
    # define modes to run  
    modeid = ''
    if not modes:
        modes = BMOD.getModeKeys()
    elif isinstance(modes,str):
        modeid = modes
    elif len(modes)==1:
        modeid = modes[0]

    # execute simulation for a single mode:
    if modeid:
        print('\nStaring simulation for {}'.format(modeid))    
        downmodes = ['F0', 'F1']
        up = not (modeid in downmodes)
        # execute simulation:
        out = simexe.runSimulation(modeid, ncnt=counts, upstream=up, timeout=timeout)
        if out:
            # process output files and get a list of data objects
            datas = simexe.processRun(modeid) 
            # plot the retrieved data
            if plot:
                simexe.plotResults(datas, title='SIMRES '+modeid, pdf=modeid)
        else:
            print('Simulation not completed.')

    # execute simulation for multiple modes:
    else:
        print('\nStaring simulation for {}'.format(','.join(modes)))
        # execute simulation:
        out = simexe.runModes(modes=modes, counts=counts, timeout=timeout, 
                              verify=False)
        if out:
            # retrieve results:
            datas = simexe.processResults(modes)
            # plot the retrieved results:
            if plot:
                simexe.plotResults(datas, title='SIMRES', pdf='results')
        else:
            print('Simulation not completed.')
    return datas


def plotResults(datas, pdf=''):
    """
    Plot data. 
    
    Optionally, provide output PDF file name (without extension) as argument. 
    """
    if not datas or len(datas)<=0: return
    dformat = datas[0].dformat
    if dformat=='mcstas':
        mcexe.plotResults(datas, title='McStas', pdf=pdf)
    elif dformat=='simres':
        simexe.plotResults(datas, title='SIMRES', pdf=pdf)
    
