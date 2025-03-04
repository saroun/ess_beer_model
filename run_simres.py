# -*- coding: utf-8 -*-
"""BEER package, test script for simulations with SIMRES.

See https://europeanspallationsource.se/instruments/beer

See https://github.com/saroun/simres

This script allows to run BEER simulations with SIMRES for selected 
pre-defined reference modes.

Requires that the environment variable JRE is defined. It has to be full
path to the Java RE interpreter. 

By default, the script assumes that SIMRES is installed in default directory.
If not, modify the _simresdir variable below. 


Example
-------
Run as a script:

    # update setup and run modes F0 and PS1 for 1e4 final neutrons
    python run_simres.py runetup=1 modes=F0,PS1 n=1e4 
    
    # run all modes 
    python run_simres.py modes=all n=1e4
    
    # see help
    python run_simres.py -h

**NOTE**

It is assumed that the component sequence corresponding to the instrument 
definiton in beer.components is already defined in the SIMRES instrument file 
beer/resources/BEER_reference.xml (defines the same component types and names).
This file is part of the package resources.

@author: J. Saroun, saroun@ujf.cas.cz
Created on Thu Jun 11 11:10:13 2020
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez
"""

#%% Import and define

import sys, os
import beer.simres as simres
import beer.modes as bmodes

# set path to SIMRES installation if not in the default location
# Linux: /opt.simres
# Windows: %programfiles%/Restrax/Simres
_simresdir = ''

# Set path to JRE interpreter if not defined by the system
# os.environ['JRE'] = r'C:\Program Files\Java\jdk-13.0.1\bin\java.exe'
_java = os.environ.get('JRE')

if not _java:
    msg = 'JRE environment variable not defined.'
    msg += ' Set JRE path for the Java interpreter.'
    raise Exception(msg) 
    
if not os.path.isfile(_java):
    raise Exception('JRE executable {} does not exist'.format(_java))

# set default
_options = {}
_options['n'] = 1e4            # number of final neutrons
_options['modes'] = 'F0'       # mode name, `all`, or a list of modes
_options['plot'] = True        # plot the result
_options['workpath'] = ''      # working directory (using home if empty)
_options['runsetup'] = False   # create and run input script for updating BEER setup

_help = {}
_help['n'] = 'number of final neutrons'
_help['modes'] = 'mode name, `all`, or a list of modes'
_help['plot'] =  'plot the result'
_help['workpath'] = 'working directory (using home if empty)'
_help['runsetup'] = 'run input script for updating BEER setup'

def _prn_help():
    """Print help."""
    out = '{} [options] \n'.format(os.path.basename(__file__))
    out += 'Options are defined in the `name=value` format:\n'
    for o in _help:
        out += '{} = {} \t{}\n'.format(o, _options[o], _help[o])
    out += '\nExample:\n'
    out += 'python run_simres.py modes=F0,PS1 n=1e4\n'
    print(out)


def _set_option(name, value):
    global _options
    if name in _options:
        if name=='n':
           value = int(float(value))
        elif name in ['plot','runsetup']:
            value = bool(int(value))
        else:
            value = str(value)
        _options[name] = value
        
def _proc_args():
    for a in sys.argv[1:]:
        if a.strip() in ['-h', '--help', '?']:
            _prn_help()
            exit()
        elif a.find('=')>0:
            [pn, pv] = a.split('=')
            pn = pn.strip()
            pv = pv.strip()
            _set_option(pn, pv)
            
# set default counts:

# Path to java executable
# change to your prefered JRE or JDK java command
#JAVA = 'java'
#JAVA = r"C:\Program Files\Java\jre1.8.0_231\bin\java.exe"

def main():
    _proc_args()
    simres.configure(workpath=_options['workpath'], 
                     simresdir=_simresdir,
                     java=_java)
    simres.update(scriptonly=not _options['runsetup'])
    # execute simulation for these modes:
    simres.execute(modes=_options['modes'],
                   n=_options['n'], 
                   runsetup=_options['runsetup'], 
                   plot=_options['plot'])


if __name__ == "__main__":
    main()
    
