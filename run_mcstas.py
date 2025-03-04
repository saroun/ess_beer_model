# -*- coding: utf-8 -*-
r"""BEER package, test script for simulations with McStas.

See https://europeanspallationsource.se/instruments/beer

See http://www.mcstas.org
    
This script allows to:

- Create McStas instrument file from a template, using the beam 
  geometry definition from beer.geometry and beer.components
- Compile the instrument file
- Run BEER simulations for selected pre-defined reference modes

By default, the script assumes McStas 3.x. The environment variable MCSTAS 
with the path to McSTas installation should be defined, e.g.

set MCSTAS=C:\mcstas-3.4


Example
-------
Run as a script:

    # complile and run modes F0 and PS1 for 1e8 neutrons
    python run_mcstas.py modes=F0,PS1 n=1e8
    
    # run all modes without re-compilation
    python run_mcstas.py force=0 modes=all n=1e7
    
    # see help
    python run_mcstas.py -h


@author: J. Saroun, saroun@ujf.cas.cz
Created on Thu Jun 11 11:10:13 2020
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez
"""

import sys
import os
import beer.mcstas as mcstas

# Set MCSTAS variable if not defined by the environment
#os.environ['MCSTAS'] = r'C:\mcstas-3.4'
#os.environ['MCSTAS'] = r'C:\mcstas-2.7.1'

_version=3  # choose mcstas version 2 or 3
_GPU=True  # version 3 with GPU?
_mcpath = os.environ.get('MCSTAS')

if not _mcpath:
    raise Exception('MCSTAS environment variable not defined.') 

if not os.path.isdir(_mcpath):
    raise Exception('MCSTAS path {} does not exist'.format(_mcpath))
    
if os.path.basename(_mcpath) in ['lib','bin']:
    _mcpath = os.path.dirname(_mcpath)

if not os.path.join(_mcpath,'bin'):
    raise Exception('Path {} does not exist'.format(os.path.join(_mcpath,'bin')))

if not os.path.join(_mcpath,'lib'):
    raise Exception('Path {} does not exist'.format(os.path.join(_mcpath,'lib')))


# set default
_options = {}
_options['n'] = 1e6  # number of neutrons generated
_options['modes'] = 'F0'  # mode name, `all`, or a list of modes
_options['plot'] = True   # plot the result
_options['force'] = True  # force creation of instr file and compile
_options['workpath'] = '' # working directory (using home if empty)
_options['outpath'] = 'out' # output directory 

# instrument parameters
_params = {}

_help = {}
_help['n'] = 'number of neutrons generated'
_help['modes'] =  'mode name, `all`, or a list of modes'
_help['plot'] =  'plot the result'
_help['force'] = 'force creation of instr file and compile'
_help['workpath'] = 'working directory (using home if empty)'
_help['outpath'] = 'output directory'

def _prn_help():
    """Print help."""
    out = '{} [options] [parameters]\n'.format(os.path.basename(__file__))
    out += 'Options are defined in the `name=value` format:\n'
    for o in _help:
        out += '{} = {} \t{}\n'.format(o, _options[o], _help[o])
    out += '\nParameters of the instrument can be defined similarly.\n\n'
    out += 'Example:\n'
    out += 'python run_mcstas.py modes=F0,PS1 n=1e8:\n\n'
    out += 'Example without re-compilation:\n'
    out += 'python run_mcstas.py modes=F0,F1 n=1e8, force=0:\n'
    print(out)

def _set_option(name, value):
    global _options
    if name in _options:
        if name=='n':
           value = int(float(value))
        elif name in ['plot','force']:
            value = bool(int(value))
        else:
            value = str(value)
        _options[name] = value
    else:
        _params[name] = value
        
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

def main():
    _proc_args()
    print('Using McStas {} at {}'.format(_version, _mcpath))
    mcstas.configure(version=_version, 
                     workpath=_options['workpath'], 
                     PATH=os.path.join(_mcpath,'bin'), 
                     MCSTAS=os.path.join(_mcpath,'lib'),
                     instname='BEER_reference', 
                     outpath=_options['outpath'])
    # Create instrument
    if _options['force']:
        mcstas.create_instrument(version=_version, GPU=_GPU, 
                                statinfo=False, shielding=False)
    # Compile
    mcstas.compile_instrument(force=_options['force'])
    # Run
    if len(_params)>0:
        print('Instrument parameters:')
        for p in _params:
            print('{} = {}'.format(p, _params[p]))
    mcstas.execute(modes=_options['modes'], n=_options['n'], 
                   plot=_options['plot'], **_params)

if __name__ == "__main__":
    main()
    

    