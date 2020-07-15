# -*- coding: utf-8 -*-
"""
Definition of BEER reference operation modes.
version: 1.0
Created on Mon Apr  8 17:27:54 2019

@author: Jan Saroun, sarun@ujf.cas.cz
"""


import numpy as np
#import BEERgeometry as BG
#import BEERcomponents as BC
deg = np.pi/180;


# %% Definition of chopper modes


"""
Reference chopper modes (pulse definition)
"""
# chopper modes: label, PSC1, PSC2, PSC3, MCA, MCB, MCC

cmodes = 8*[0]
cmodes[0] = ['full pulse', 0,  0, 0, 0, 0, 0 ]
cmodes[1] = ['PSC, high flux', 168,  0, -168, 0, 0, 0 ]
cmodes[2] = ['PSC, medium resolution', 168, -168, 0, 0, 0, 0 ]
cmodes[3] = ['PSC, high resolution', 168, -168, 0, 0, 0, 0 ]
cmodes[4] = ['MC, high flux', 0, 0, 0, 70, 0, 0 ]
cmodes[5] = ['MC, medium resolution', 0, 0, 0, 140, 0, 0 ]
cmodes[6] = ['MC, high resolution', 0, 0, 0, 280, 0, 0 ]
cmodes[7] = ['MC, SANS mode', 0, 0, 0, 0, 0, 70 ]


"""
Reference wavelength frame selection modes
"""
# label, FC1A, FC1B, FC2A, FC2B
wmodes = 4*[0]
wmodes[0] = ['full beam', 0, 0, 0, 0]
wmodes[1] = ['single frame', 28, 0, 14, 0]
wmodes[2] = ['pulse suppression, double frame', 14, 0, 7, 0]
wmodes[3] = ['alternating frames', 14, 63, 0, 7]

# %% Definition of BEER reference operation modes
modes = 14*[None]

def defMode(ID, slits, foc=True, lam=2.1, cm=[0, 0], PSC2dist=200):
    """
    Return hash map with mode parameters
    
    Arguments
    ---------
    ID: string
        ID string
    slits: list(3)
        [width, height] for the three slits [SL3, SL2, SL1]
    for: boolean
        if the focusing guide on exchanger is on
    lam: float
        center of the wavelength band
    cm: list(2)
        [cmode, wmode] = mode indexes for pulse choppers (PSCx MCx) and wavelength frame choppers (FCx)
    PSC2dist: float
        distance of the PSC2 chopper, can be 200 or 400
    
    """
    res = {'ID':ID[0], 'label':ID[1], 'comment':ID[2] }
    res['SL3'] = slits[0]
    res['SL2'] = slits[1]
    res['SL1'] = slits[2]
    res['GEX1'] = foc
    res['cmode'] = cm[0]
    res['wmode'] = cm[1]
    res['lam0'] = lam
    if (PSC2dist>=200 or PSC2dist<=400):
        res['PSC2dist'] = PSC2dist
    else:
        raise Exception('PSC2 distance can only be between 200 or 400')
    
    return res

# Define operation modes:
i = 0
modes[i] = defMode(
        ID=['F0', 'Maximum intensity, white beam', 'never used in experiment'],
        slits=[[100,100], [0,0], [0,0]], foc=1, lam=2.1, cm=[0, 0]
        )
i += 1
modes[i] = defMode(
        ID=['PS0', 'Maximum intensity,  pulse shaping', 'diffraction, max. slit'],
        slits=[[10,20], [25,0], [0,0]], foc=1, lam=2.1, cm=[1, 1]
        )

i += 1
modes[i] = defMode(
        ID=['PS1', 'High flux, pulse shaping', 'in-situ thermo mechanical experiment'],
        slits=[[5,10], [25,0], [0,0]], foc=1, lam=2.1, cm=[1, 1]
        )

i += 1
modes[i] = defMode(
        ID=['PS2', 'Medium resolution, pulse shaping', 'in-situ thermo mechanical experiment'],
        slits=[[5,10], [23,0], [35,0]], foc=1, lam=2.1, cm=[2, 1], PSC2dist=400
        )

i += 1
modes[i] = defMode(
        ID=['PS3', 'High resolution, pulse shaping', 'in-situ thermo mechanical experiment'],
        slits=[[5,10], [15,0], [20,0]], foc=1, lam=2.1, cm=[3, 1]
        )

i += 1
modes[i] = defMode(
        ID=['M0', 'Maximum intensity,  modulation',	'diffraction, max. slit'],
        slits=[[10,20], [25,0], [0,0]], foc=1, lam=2.1, cm=[4, 1]
        )

i += 1
modes[i] = defMode(
        ID=['M1', 'High flux, modulation',	'strain scanning'],
        slits=[[2,5], [25,0], [0,0]], foc=1, lam=2.1, cm=[4, 1]
        )

i += 1
modes[i] = defMode(
        ID=['M2', 'Medium resolution, modulation',	'strain scanning'],
        slits=[[1,3], [18,0], [35,0]], foc=1, lam=2.1, cm=[5, 1]
        )

i += 1
modes[i] = defMode(
        ID=['M3', 'High resolution, modulation',	'strain scanning'],
        slits=[[1,3], [8,50], [12,0]], foc=0, lam=2.1, cm=[6, 1]
        )

i += 1
modes[i] = defMode(
        ID=['IM0', 'White beam',	'imaging'],
        slits=[[0,0], [25,25], [10,10]], foc=0, lam=3.0, cm=[0, 1]
        )

i += 1
modes[i] = defMode(
        ID=['IM1', 'High flux, pulse shaping',	'imaging, Bragg edge'],
        slits=[[0,0], [25,25], [10,10]], foc=0, lam=3.5, cm=[1, 1]
        )

i += 1
modes[i] = defMode(
        ID=['SANS', 'White beam',	'SANS'],
        slits=[[10,10], [15,15], [20,20]], foc=0, lam=6.0, cm=[0, 1]
        )

i += 1
modes[i] = defMode(
        ID=['DS0', 'diffraction + SANS, modulation', 'in-situ thermomechanical experiment'],
        slits=[[5,10], [25,25], [40,40]], foc=0, lam=3.5, cm=[7, 2]
        )

i += 1
modes[i] = defMode(
        ID=['DS1', 'diffraction + SANS, pulse shaping', 'in-situ thermomechanical experiment'],
        slits=[[5,10], [25,25], [40,40]], foc=0, lam=2.1, cm=[1, 3]
        )

# %% 


def getModeStr(m):
    fmt = '{}\t'*3 + '{:.1f}\t'*6 + '{}\t' + '{:.2f}\t' + '{:d}\t' + '{:d}\n'
    s = fmt.format(m['ID'], m['label'], m['comment'], 
                   *m['SL3'], *m['SL2'], *m['SL1'], m['GEX1'], m['lam0'],
                     m['cmode'], m['wmode'])
    return s

def getCModeStr(m):
    fmt = '{}\t'*6 + '{}\n'
    s = fmt.format(* m)
    return s

def getFModeStr(m):
    fmt = '{}\t'*4 + '{}\n'
    s = fmt.format(* m)
    return s

def modes2str():
    out = ''
    fmt = '{}\t{}'    
    out += '# Operation modes\n'
    for i in range(len(modes)):
        out += fmt.format(i,getModeStr(modes[i]))
    out += '# Chopper modes (pulse definition)\n'
    for i in range(len(cmodes)):
        out += fmt.format(i,getCModeStr(cmodes[i]))
    out += '# Wavelength frame selection modes\n'        
    for i in range(len(wmodes)):
        out += fmt.format(i,getFModeStr(wmodes[i]))
    return out

def getSlitStr(ID, dim=0):
    inf = [40, 80]
    n = len(modes)
    fmt = '{:.1f}, '*(n-1)+'{:.1f}'
    val = np.zeros(n)
    for i in range(len(modes)):
        m = modes[i]
        val[i] = m[ID][dim]
        if (val[i]<=0):
            val[i] = inf[dim]
    out = fmt.format(*val)
    return out

def getChopperStr(ID):
    cnames = ['label', 'PSC1','PSC2','PSC3','MCA','MCB', 'MCC']
    n = len(modes)
    idx = cnames.index(ID)
    fmt = '{:.1f}, '*(n-1)+'{:.1f}'
    val = np.zeros(n)
    for i in range(len(modes)):
        m = modes[i]
        cm = cmodes[m['cmode']]
        if (cm != 0):
            val[i] = cm[idx]
        else:
            val[i] = 0   
    out = fmt.format(*val)
    return out

def getFChopperStr(ID):
    cnames = ['label', 'FC1A','FC1B','FC2A','FC2B']
    n = len(modes)
    idx = cnames.index(ID)
    fmt = '{:.1f}, '*(n-1)+'{:.1f}'
    val = np.zeros(n)
    for i in range(len(modes)):
        m = modes[i]
        cm = wmodes[m['wmode']]
        if (cm != 0):
            val[i] = cm[idx]
        else:
            val[i] = 0   
    out = fmt.format(*val)
    return out

def getGEXStr():
    n = len(modes)
    fmt = '{:g}, '*(n-1)+'{:g}'
    val = np.zeros(n)
    for i in range(len(modes)):
        m = modes[i]
        val[i] = m['GEX1']
    out = fmt.format(*val)
    return out

def getPSC2distStr():
    n = len(modes)
    fmt = '{:g}, '*(n-1)+'{:g}'
    val = np.zeros(n)
    for i in range(len(modes)):
        m = modes[i]
        val[i] = m['PSC2dist']
    out = fmt.format(*val)
    return out

def getCmodesStr():
    n = len(modes)
    fmt = '{:g}, '*(n-1)+'{:g}'
    val = np.zeros(n)
    for i in range(len(modes)):
        m = modes[i]
        val[i] = m['cmode']
    out = fmt.format(*val)
    return out

def getWmodesStr():
    n = len(modes)
    fmt = '{:g}, '*(n-1)+'{:g}'
    val = np.zeros(n)
    for i in range(len(modes)):
        m = modes[i]
        val[i] = m['wmode']
    out = fmt.format(*val)
    return out

# %%
#
with open('BEER_modes.txt', 'w') as f: 
    f.write(modes2str())




# %%
        

