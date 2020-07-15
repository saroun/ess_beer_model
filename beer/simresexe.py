# -*- coding: utf-8 -*-
"""
Scripts for running simulations with SIMRES.

Usage:

- ``getSimresPath`` to get default SIMRES installation path.
- ``setSimresPath`` to change SIMRES installation path.
- ``setSimresConfig`` to set SIMRES project paths.
- ``runSimulation`` to run a SIMRES simulation for given BEER reference mode(s)
- ``runModes`` to run a set of simulations for given BEER reference modes

Created on Fri Jun 26 16:36:58 2020
@author: J. Saroun, saroun@ujf.cas.cz
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez
"""
import os, sys, subprocess
from beer.utils import getTemplate, copyResources
import beer.modes as BMOD
import beer.simres as BSIM
import beer.components as BC
import beer.mcplot as mcplot
import traceback

#%% Define global variables

# SIMRES installation path
# This is a trial to find it at default places for Windows and Linux:
if sys.platform.startswith('linux'):
    _SIMRES_PATH = '/opt/simres'
else:
    _SIMRES_PATH = os.path.join(os.environ['PROGRAMFILES'],'Restrax','Simres')

# Keep SIMRES project data as global variables
# Must be defined by user calling setSimresConfig() before running SIMRES
_SIMRES_JAVA = 'java'
_SIMRES_WORKPATH = ''
_SIMRES_CFG_FILE = 'BEER_reference.xml'
_SIMRES_CFG_DIR = ''
_SIMRES_OUT_DIR = ''
_SIMRES_PRJ_FILE = 'beer_simres.xml'
# global switch for up-stream tracing
_UPSTREAM = True

#%% SIMRES setup validation

def checkSimres(verify=True):
    """
    Return path to SIMRES GUI folder and name of the executable jar file.
    
    If verify, check that SIMRES path is valid 
    (./GUI and ./GUI/simresCON.jar exist).
    
    Raises Exception in case of failure.
    
    Parameters:
    ----------
    verify: boolean
        If true, verifies that the path exists and contains required files.
    
    Returns:
    --------
    
    dict with keys:
    
    GUI: str
        path to GUI folder
    jar: str
        absolute path to simresCON.jar
    
    """
    global _SIMRES_PATH
    guipath = os.path.join(_SIMRES_PATH,'GUI/')
    jarfile = os.path.join(guipath,'simresCON.jar')
    guipath = os.path.normpath(guipath)
    jarfile = os.path.normpath(jarfile)
    msg=''
    if verify:
        if not os.path.isdir(guipath):
            msg += 'Path {} does not exist'.format(guipath)
        if not os.path.isfile(jarfile):
            msg += 'File {} does not exist'.format(jarfile) 
        if msg:
            errmsg = 'Invalid SIMRES installation\n'
            errmsg += msg
            f = os.path.basename(__file__)
            msg = 'Use {}.setSimresPath() to define valid SIMRES installation\n'.format(f)
            errmsg += msg
            raise Exception(errmsg)
    res = {'GUI': guipath, 'jar': jarfile}
    return res


def checkConfig(config=None):
    """
    Check that SIMRES project configuration is valid.
    
    Raises exception in case of failure.
    
    Parameters:
    ----------
    config: dict
        configuration data in the format returned by getSimresConfig().
        If None, calls getSimresConfig() to get actual values.

    See also
    --------
    getSimresConfig
    """
    fn = os.path.basename(__file__)
    # check that all keys are present
    keys = ['WORKPATH','OUTPATH','CFGPATH','CFGFILE','JAVA','PRJFILE']
    if config is None:
        config = getSimresConfig()
    for key in keys:
        missing = []
        if not key in config:
            missing.append(key)
        if len(missing)>0:
            msg = 'Invalid config format. Missing keys {}'.format(','.join(missing))
            raise Exception('ERROR: {}, '.format(fn)+msg)
    # check that required workspace directories and files exist
    dirs = [config['WORKPATH'], config['OUTPATH'], config['CFGPATH']]
    msgs = ''
    
    sfx = 'Call {}.setSimresConfig() to define valid workspace.'.format(fn) 
    for d in dirs:
        if not os.path.isdir(d):
            msgs += 'Directory {} does not exist.\n'.format(d)
    if msgs:
        raise Exception('ERROR:\n'+msgs+sfx)

    # check at least that the instrument xml file exists
    fn = os.path.join(config['CFGPATH'],config['CFGFILE'])
    if not os.path.isfile(fn):
        msg = 'File {} does not exist.\n'.format(fn)
        raise Exception(msg+sfx)


#%% Generation of SIMRES scripts

def scriptAll(modes=[4],  ncnt=10000, lrange=[0.2, 10.2], misalign=0.02, 
              waviness=0.2,  overlap=0, file='', template='BEER_modes.inp'):
    """
    Generates a complete SIMRES script file for simulation of given BEER 
    modes.
    
    
    Arguments:
    ---------
    modes: list
        a list of mode indices or ID strings as defined in beer.modes
    ncnt: int
        if defined, include command for given final number of counts        
    lrange: list(2)
        wavelength range
    misalign: float
        guide misalignment [mm]
    waviness: float
        guide waviness [mrad], RMS
    overlap: int
        switch chopper period overlaping on/off
    file: str
        output file name, leave empty to just return the script content
    template: str
        template file name without ``.template`` extension

    Recognized template tokens (with @ prefix):
        
    -SRC    generating script name
    -DATE    replaced by creation date/time
    -SOURCE    source definition
    -WRANGE    initial wavelength range setting
    -MISALIGN   set misalignment to given value in mm (zero is default)
    -WAVINESS    set waviness to given valuein mrad (zero is default)
    -OVERLAP    set initial overlap for all choppers 
    -EXEC    execution part of the script
    
    If template is not defined, a default sequence of commands is generated.
        
    """  
    def defaultCommands():
        out = ''
        out += '# Automatically generated by beer.simres\n'
        out += '# Version: {}\n'.format(BC.VERSION)
        out += '# Date: {}\n'.format(BC.DATE)
        fmt = '\n {}\n'
        out += fmt.format(s_source)
        out += fmt.format(s_lrange)
        out += fmt.format(BSIM.setMisalignment(d=misalign))
        out += fmt.format(BSIM.setWaviness(w=waviness))
        out += fmt.format(BSIM.setOverlap(over=overlap))
        out += fmt.format(s_exe)
        return out
    
    s_lrange = BSIM.setWRange(lrange=lrange, underline=True)
    s_source = BSIM.setSource()
    s_exe = BSIM.setMode0()
    for m in modes:
        if isinstance(m, int):
            im = m
        else:
            im = BMOD.getModeIndex(m)
        s_exe += BSIM.scriptDS1(im, ncnt=ncnt, lrange=lrange, exe=True, 
                   plot=['x', 'y', 'kx', 'ky', 'lam',  't'], upstream=_UPSTREAM)
    
    try:
        lines = getTemplate(template)
        out = ''
        for i in range(len(lines)):
            line = lines[i]
            k = line.find('@')
            if (k>=0):
                if (line.find('@')>-1): line = line.replace('@SRC','beer.simres')
                if (line.find('@')>-1): line = line.replace('@DATE',BC.DATE)
                if (line.find('@')>-1): line = line.replace('@VERSION', BC.VERSION)
                if (line.find('@')>-1): line = line.replace('@TEMPLATE', template)
                if (line.find('@')>-1): line = line.replace('@SOURCE', s_source)
                if (line.find('@')>-1): line = line.replace('@WRANGE', s_lrange)
                if (line.find('@')>-1): line = line.replace('@MISALIGN', BSIM.setMisalignment(d=misalign))
                if (line.find('@')>-1): line = line.replace('@WAVINESS', BSIM.setWaviness(w=waviness))
                if (line.find('@')>-1): line = line.replace('@OVERLAP', BSIM.setOverlap(over=overlap))
                if (line.find('@')>-1): line = line.replace('@EXEC', s_exe)
            else:
                line = lines[i]
            out += line
    except:
        out = defaultCommands()
    if file:
        with open(file, 'w') as fo:
            lines = fo.write(out)
        fo.close()
        print('SIMRES script file saved as {}'.format(file))
    return out


def saveScript(mode, ncnt=None, outpath='', file=None):
    """
    Save a SIMRES script for simulation of given reference mode,
    using the function ``scriptAll``. 
    
    Parameters:
    ----------
    mode: int or str or list
        Mode index or ID string as defined in beer.modes. Can also be a list of IDs.
    ncnt: int
        if defined, include command for given final number of counts
    outpath: str
        Output path (incl. trail slash). If not defined, uses _SIMRES_CFG_DIR
    file: string
        Output file name. If empty, the name is generated from 
        the mode ID, for example 'F0.inp' for mode F0. If None, then no script
        is saved.
    
    Returns:
    --------
    
    dict with keys:
    
    modeid: str
        mode id string or  `allmodes` in case mode=list of modes.
    scrname: str
        script file name
    script: str
        script content
    """
    if not outpath:
        outpath = _SIMRES_CFG_DIR
    if not os.path.isdir(outpath):
        raise Exception('Output directory does not exist: {}'.format(outpath))
    
    if isinstance(mode, list):
        modes = mode
        modeid = 'allmodes'
    elif isinstance(mode, int):
        modes = [mode]
        modeid = BMOD.modes[mode]['ID']
    else:
        modes = [mode]
        modeid = mode
    
    if file=='':
        fname = '{}.inp'.format(modeid)
    elif file is None:
        fname = None
    else:
        fname = file
    
    if fname:
        inp = scriptAll(modes=modes, ncnt=ncnt, file=os.path.join(outpath,fname))
    else:
        inp = scriptAll(modes=modes, ncnt=ncnt, file='')
    res = {'modeid': modeid, 'scrname':fname, 'script': inp}
    return res



#%% Configuring SIMRES project before launching simulation

def getOutputFiles(mode='F0', fset = ['x','y','kx','ky','lam','t']):
    """
    Return a list of default output filenames of SIMRES simulation script
    generated by this package.
    
    Parameters:
    -----------
    mode: str
        BEER reference mode id as defined in beer.modes
    fset: list of str
        Set of filename suffixes for files exported during simulation.
    
    Returns:
    --------
    
    A list of filenames constructed as `mode_fset`.dat.
    """
    files = []
    for f in fset:
        files.append('{}_{}.dat'.format(mode,f))
    return files


def getSimresPath():
    """
    Return SIMRES installation path (absolute) as defined in this module.
    
    Use ``setSimresPath`` to change it.
    """
    global _SIMRES_PATH
    return _SIMRES_PATH


def setSimresPath(path=''):
    """
    Set SIMRES installation path (absolute).
    
    If not defined, tries to use default.
    """
    global _SIMRES_PATH
    if path:
        _SIMRES_PATH = os.path.normpath(path)


def getSimresConfig():
    """
    Get SIMRES project configuration as dict.
    
    Change this setting by calling ``setSimresConfig``.
    
    Returns:
    --------
    
    dict with following keys:
    
    WORKPATH: str
        Root project directory with instrument data and output.        
    OUTPATH: str
        output path
    CFGPATH: str
        path to instrument configuration data
    CFGFILE: str
        instrument configuration file in xml format
    PRJFILE: str
        file name of the project definition (xml format)
    JAVA: str
        Command for calling Java (needed to launch simulation)
    """
    global _SIMRES_JAVA,_SIMRES_WORKPATH, _SIMRES_CFG_FILE, _SIMRES_CFG_DIR, _SIMRES_OUT_DIR
    res = {'JAVA': _SIMRES_JAVA,
           'WORKPATH':_SIMRES_WORKPATH,
           'OUTPATH':_SIMRES_OUT_DIR, 
           'CFGPATH':_SIMRES_CFG_DIR, 
           'CFGFILE':_SIMRES_CFG_FILE,
           'PRJFILE':_SIMRES_PRJ_FILE}
    return res


def createWorkspace():
    """
    Check workspace directories and create missing ones.
    Copy resource files to the workspace directory and check the setup 
    (files exist).
    """
    
    # create workspace directories
    config = getSimresConfig()
    dirs = [config['CFGPATH'], config['OUTPATH'], config['WORKPATH']]
    for d in dirs:
        if not os.path.isdir(d):
            try:
                print('Creating directory: {}'.format(d))
                os.makedirs(d)
            except Exception as e:
                print('Failed to create directory: {}'.format(d))
                raise Exception(e)

    # copy resource files to workspace
    copyResources(config['CFGPATH'], 
                  dirs=['tables'], 
                  globs=['*.tab'], 
                  files=['BEER_reference.xml'])


def saveProjectInfo(fname='beer_simres.xml', verbose=True):
    """
    Saves project definiton file with given name.
    
    Uses global variables _SIMRES_CFG_FILE, _SIMRES_CFG_DIR, _SIMRES_OUT_DIR
    
    Parameters:
    -----------
    fname: str
        file name of the saved project definition file.
    verbose: boolean
        if true, print info on project paths
    
    """
    global _SIMRES_PRJ_FILE
    config = getSimresConfig()
    if verbose:
        msg = 'Project setting:\n'
        fmt = '{}: {}\n'
        for key in config:
            msg += fmt.format(key,config[key])
        print(msg)  
    #cfgpath = config['CFGPATH']
    outpath = config['OUTPATH']
    out = '<?xml version="1.0" encoding="UTF-8"?>\n'
    out += '<SIMRES>\n'
    out += '\t<PROJECT system="no" current="yes">\n'
    fmt = '\t\t<{}>{}</{}>\n'
    out += fmt.format('CFGPATH',config['CFGPATH'], 'CFGPATH')
    out += fmt.format('OUTPATH',outpath, 'OUTPATH')
    out += fmt.format('DATPATH',config['CFGPATH'], 'DATPATH')
    out += fmt.format('CFGFILE',config['CFGFILE'], 'CFGFILE')
    out += fmt.format('DESCR','Auto-generated by beer.simres', 'DESCR')
    out += '\t</PROJECT>\n'
    out += '</SIMRES>\n'
    # must be saved in users home ./simres folder
    userpath = os.path.expanduser('~')
    if not os.path.isdir(userpath):
        msg = 'User home directory {} does not exist.\n'.format(userpath)
        raise Exception(msg)
    outdir = os.path.join(userpath,'.simres')
    if not os.path.isdir(outdir):
        msg = 'SIMRES profile directory {} does not exist.'.format(outdir)        
        print(msg+'\nTrying to create one.')
        os.mkdir(outdir)
        if not os.path.isdir(outdir):
            raise Exception(msg)
    outfile = os.path.join(outdir,fname)
    with open(outfile, 'w') as fo:
        fo.write(out)
        fo.close()
        print('Custom project file created in {}'.format(outfile))
    _SIMRES_PRJ_FILE = fname


def setSimresConfig(workpath='', instr='BEER_reference.xml', cfgpath='cfg', 
                    outpath='out', java='java'):
    """
    Set SIMRES project configuration. Create workspace files and directories
    if needed. 
    
    Must be executed before calling run* functions from this module.
    
    Parameters:
    -----------
    workpath: str
        Root project directory with instrument data and output.
    cfgpath: str
        path to instrument configuraiton files, relative to workpath
    outpath: str
        output path for results, relative to workpath
    instr: str
        instrument file name (xml format)
    java: str
        Command for calling Java (needed to launch simulation)
    
    """
    global _SIMRES_JAVA, _SIMRES_WORKPATH, _SIMRES_CFG_FILE, _SIMRES_CFG_DIR, _SIMRES_OUT_DIR
    
    
    if workpath:
        _SIMRES_WORKPATH = os.path.normpath(workpath)
    else:
        userhome = os.path.expanduser('~')
        _SIMRES_WORKPATH = os.path.join(userhome,'beer_optics','simres')
    
    if outpath:
        if os.path.isabs(outpath):  
            _SIMRES_OUT_DIR = os.path.normpath(outpath)
        else:
            s = os.path.join(_SIMRES_WORKPATH,outpath)
            _SIMRES_OUT_DIR = os.path.normpath(s)

    if cfgpath:
        if os.path.isabs(cfgpath):  
            _SIMRES_CFG_DIR = os.path.normpath(cfgpath)
        else:
            s = os.path.join(_SIMRES_WORKPATH,cfgpath)
            _SIMRES_CFG_DIR = os.path.normpath(s)
    if instr:
        _SIMRES_CFG_FILE = instr
    if java:
        _SIMRES_JAVA = java
    # create workspace files and directories
    createWorkspace()
    # save info on SIMRES project to user profile
    saveProjectInfo()


#%% Run simulations

def verifyConfig(verbose=1):
    """
    Verify workspace configuration.
    """
    res = False
    try:
        config = getSimresConfig()
        checkConfig(config)
        if verbose:
            print('\tConfiguration files are saved in: {}'.format(config['CFGPATH']))
            print('\tOutput files are saved in: {}'.format(config['OUTPATH']))
        res = True
    except Exception as e:
        print(e)
    return res


def verifySimres(verbose=1):
    """
    Verify SIMRES.
    """
    res = False
    try:
        # first verify SIMRES installation
        sim = checkSimres()
        if verbose:
            print('\tSIMRES path: {}'.format(sim['GUI']))
            print('\tSIMRES jar: {}'.format(sim['jar']))
        res = True
    except Exception as e:
        print(e)
    return res


def verifyJava(verbose=1):
    """
    Verify that java can be started.
    """
    config = getSimresConfig()
    cmd = [config['JAVA'], '-version']
    out = None
    res = False
    try:
        if verbose:
            print('\tTesting Java ... ',end='')
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                             universal_newlines=True, shell=True, check=True)
        out.check_returncode()
        if verbose:
            print('OK.')
        res = True
    except Exception as e:
        if verbose:
            print('failed.')
        msg = 'Can\'t execute {}.\n {}\n'.format(' '.join(cmd),e)
        if out:
            ires = out.returncode
            msg += 'Return code: {:d}'.format(ires)
        sys.exit(msg)
        traceback.print_exc(file=sys.stdout)
    return res


def runScript(config=None, script='BEER_setup.inp', log='',
              timeout=600, verbose=1):
    """
    Launch SIMRES, execute given script and exit. 
    
    The script is intended for updating components parameters according
    to the beer.gemoetry and beer.components definitions and to save 
    the updated instrument file in config['CFGDIR'].
    
    **NOTE:** This function does not verify SIMRES and workspace configurations.

    Parameters:
    ----------
    config:
        Workspace configuration data as returned by getSimrestConfig.
        If not set, getSimrestConfig is called and config verified.
    script: scr
        Script file name to execute (must exist in config['CFGDIR'])
    log: str
        File name for log files (excl. extension). 
        Leave empty to switch off logging. 
    timeout: int
        Timeout in sec for execution
    verbose: int
        If true, print STDOUT from the simulation.
    
    Returns:
    --------
    Result of subprocess.run
    
    See also:
    --------
    getSimrestConfig, setSimrestConfig, checkConfig

    
    """
    # first get SIMRES installation data
    sim = checkSimres(verify=False)
    
    # verify project setting
    if not config:
        if not verifyConfig(): return
        config = getSimresConfig()
    
    # check that the script exists
    scrfull = os.path.join(config['CFGPATH'],script)
    if not os.path.isfile(scrfull):
        raise Exception('Script {} does not exist.'.format(scrfull))

    # compose command
    cmd = [config['JAVA'], '-jar', sim['jar']]
    # options
    cmd.extend(['-g', sim['GUI']]) # path to GUI directory
    cmd.extend(['-p', config['PRJFILE']]) # project config. file name
    cmd.extend(['-c', config['CFGFILE']]) # instrument config. file name
    cmd.extend(['-s', script]) # script name 
    cmd.extend(['-e', 'SCRIPT']) # command for SIMRES to execute the script and exit
    if log:
        cmd.extend(['-o', log+'.html']) # html output file
        cmd.extend(['-log', log+'.log']) # console output text file
    out = None
    try:
# for Python >= 3.7 :
#        out = subprocess.run(cmd, capture_output=True, text=True, shell=True, check=True)
# for Python < 3.7 :
        print('Command:\n'+' '.join(cmd))
        print('Running ... ',end='')
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                             universal_newlines=True, shell=True, check=True,
                             timeout=timeout)
        out.check_returncode()
        print('done.')
    except Exception as e:
        msgdata = cmd[:3]
        msg = 'Can\'t execute {} {} {}.\n {}\n'.format(*msgdata,e)
        if out:
            ires = out.returncode
            msg += 'Return code: {:d}'.format(ires)
        sys.exit(msg)
        traceback.print_exc(file=sys.stdout)
    if verbose>=0:
        print(out.stdout) 
    return out


def runSimulation(mode, config=None, ncnt=10000, upstream=True, verbose=1,
                 timeout=600, quiet=False):
    """
    Execute SIMRES simulation for the selected BEER mode. 
    
    First creates corresponding input script and then launches 
    SIMRES in command mode. 
    
    **NOTE:** This function does not verify SIMRES and workspace configurations.
    
    Parameters:
    ----------
    mode: int, str or list
        BEER mode index, ID or list of ID's
    config:
        Workspace configuration data as returned by getSimrestConfig.
        If not set, getSimrestConfig is called and config verified.
    ncnt: int
        Number of final counts
    upstream: boolean
        Switch for up-stream tracing mode
    verbose: int
        If true, print STDOUT from the simulation.
    timeout: int
        timeout in sec for execution
    
    See also:
    --------
    getSimrestConfig, setSimrestConfig
    
    """
    global _UPSTREAM
    _UPSTREAM = upstream

    # verify project setting
    if not config:
        if not verifyConfig(verbose=not quiet): return
        config = getSimresConfig()

    # generate input script
    inp = saveScript(mode, ncnt=ncnt, outpath=config['CFGPATH'], file='')
    
    out = None
    out = runScript(config=config, 
                    script=inp['scrname'], 
                    log=inp['modeid'], 
                    timeout=timeout, 
                    verbose=verbose)
    if out:
        print('\nSee results in '+config['OUTPATH'])


def runSetup(verify=True):
    """
    Create input script for setting up BEER instrument configuration,
    launch SIMRES and update the instrument file [BEER_reference.xml]
    according to actual beam geometry definition. 
    
    Assumes that SIMRES configuration has already been defined.
    
    Parameters:
    -----------
    verify: boolean
        if true, verify SIMRES and Java
    
    See setSimresConfig().
    """
    # verify project setting
    if verify:
        if not (verifySimres() and verifyJava()): return
    if not verifyConfig(): return
    config = getSimresConfig()
    # Save script for setting configuration according to the current beam geometry 
    # as defined in beer.geometry and beer.components
    BSIM.createScriptSetup(file = 'BEER_setup.inp', 
                           outpath=config['CFGPATH'], 
                           save=os.path.join(config['CFGPATH'],config['CFGFILE']))
    
    # Run SIMRES to execute BEER_setup.inp
    runScript(script='BEER_setup.inp', log='setup')


def runModes(modes=[], counts=1000, timeout=600, verify=True):
    """
    Run simulations for selected BEER reference modes.
    
    Parameters:
    -----------
    modes: list
        list of mode ID's
    counts: int
        number of final counts
    timeout: int
        timeout in sec for one simulation
    verify: boolean
        if true, verify SIMRES and Java
    
    Example:
    --------
    
    runModes(modes=['F1','PS1','MCA', 'IM0'])
        
    """
    if verify:
        if not (verifySimres() and verifyJava()): return
    if not verifyConfig(): return
    # modes to be simulated in down-stream direction
    downmodes = ['F0', 'F1']
    config = getSimresConfig()
    for m in modes:
        imode = BMOD.getModeIndex(m)
        if (imode>=0):
            up = not (m in downmodes)
            try:
                runSimulation(m, config=config, ncnt=counts, upstream=up, 
                                  timeout=timeout)
            except Exception as e:
                print(e)


#%% Process and plot results

def processResults(results, dataname='_lam.dat', outfile='intensities.dat'):
    """
    Process a set of simulation results from McStas or SIMRES. 
    For each result, find given data file (dataname) and convert it 
    to the Data1D object. Print and (optionally) save the integral intensities 
    for all results as a table.    
    
    All simulations are saved in a single output directory. We assume that
    the file names are constructed as `[basename][suffix]`, where `basename` denotes
    the simulation and `suffix` denotes the type of output (plot). Then you 
    can provide a list of basenames as `results`, whereas `dataname` should be 
    the required suffix.
    
    `Example: results=['FC1', 'PS1', 'MCA'], dataname='_lam.dat'` 
    
    would process files ``FC1_lam.dat``, ``PS1_lam.dat`` and ``MCA_lam.dat`` 
    from the workspace outpuut directory
    
    Parameters:
    -----------
    results: list of str
        list of directories (McStas) or file name bases (SIMRES) to search for
    dataname: str
        file name (McStas) or file name suffix (SIMRES) to search for
    outfile: str
        output file name
        
    Returns:
    --------
    
    Retrieved results as Data1D objects.
        
    """
    config = getSimresConfig()
     # add 2nd frame for DS1 mode to evaluation
    if ('DS1' in results) and (not 'DS1_2' in results):
        results.append('DS1_2')
    datas = mcplot.processResults(results, 
                              dataname=dataname, 
                              parentdir=config['OUTPATH'],
                              outfile=outfile,
                              dformat='simres')
    return datas


def processRun(mode):
    """
    Process a single simulation results produced by SIMRES. 
    Find all specified files in given directory for given mode and convert them 
    to the `Data1D` objects. Return these objects as a list.
    
    The output file names are assumed to conform to this package, that is:
        
        `base_suffix.dat`
    
    where `base` is the mode ID and `suffix` denotes the variable name, 
    for example `FC1_lam.dat` for wavelength distribution, mode=`FC1`.
        
    Parameters:
    -----------
    mode: str
        mode ID, one of those defined in beer.modes
    
    Returns:
    --------
    
    Retrieved results as Data1D objects.
        
    """
    
    config = getSimresConfig()
    datas = mcplot.processRun('', files=getOutputFiles(mode=mode), 
                              parentdir=config['OUTPATH'], 
                              dformat='simres')
    return datas


def plotResults(datas, title='SIMRES', pdf=''):
    """
    Plot results retrieved by processResults(). 
    
    Parameters:
    -----------
    datas: 
        list of Data1D
    title: str
        Title to be shown on graph
    pdf: str
        File name to export (pdf format, without extension).
        Leave empty to suppress file export.
        
    """
    if pdf:
        config = getSimresConfig()
        out = os.path.join(config['OUTPATH'], pdf)
    else:
        out = ''
    mcplot.plotDataSet(datas, title=title, pdf=out)
