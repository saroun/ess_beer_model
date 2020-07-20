# -*- coding: utf-8 -*-
"""
BEER package, test script for simulations with SIMRES.

See https://europeanspallationsource.se/instruments/beer

See https://github.com/saroun/simres

@author: J. Saroun, saroun@ujf.cas.cz
Created on Thu Jun 11 11:10:13 2020
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez

Creates input scripts for setting BEER configuration according to actual 
beam geometry definition in beer.geometry and beer.components modules. 

Creates SIMRES project files and input scripts for BEER reference operation modes.

Runs simulation for these modes using SIMRES (if installed) and plots results.


Usage:
------
- Run this script from command line: 
`python run_simres.py n=[number of neutrons]`

- or from IPyton console:
`%run run_simres.py n=[number of neutrons]`

**NOTE**: 

It is assumed that component sequence corresponding to the instrument definiton
in beer.components is already defined in the SIMRES instrument file 
beer/resources/BEER_reference.xml (defines the same component types and names).
This file is part of the package resources.

"""

#%% Import and define

import sys
import beer.simres as simres
import beer.modes as bmodes


# set defoult counts:
counts = 1000

# Path to java executable
# change to your prefered JRE or JDK java command
JAVA = 'java'

""" Process command arguments 
Accepts n=counts
"""
if len(sys.argv)>1:
    a = sys.argv[1]
    if a.find('=')>0:
        print(sys.argv)
        [pn, pv] = a.split('=')
        if pn=='n':
            counts = int(float(pv))


#%% Set SIMRES configuration

# leave workpath empty to use default: ~/beerpy/simres 
simres.configure(workpath='', java=JAVA)

#%% Create BEER_setup.inp script for updating actual BEER configuration. 
# Set scriptonly=False to also start SIMRES and run the script.

simres.update(scriptonly=False)

#%% Run a single simulation for given BEER mode

"""
data = simres.execute(modes='PS2', n=counts, runsetup=False, plot=True)
"""

#%% Run a sequence of simulations for multiple modes defined in beer.modes

# define modes to run

# get all modes:
modes = bmodes.getModeKeys() 

# or define own list. Call BMOD.listModes() to get a list of defined modes:
#modes = ['F0', 'PS2', 'M1']
 
# execute simulation for these modes:
data = simres.execute(modes=modes, n=counts, runsetup=False, plot=True)


