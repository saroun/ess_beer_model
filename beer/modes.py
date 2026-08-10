# -*- coding: utf-8 -*-
"""
Definition of BEER reference operation modes.

Created on Mon Apr  8 17:27:54 2019
@author: Jan Saroun, saroun@ujf.cas.cz
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez
"""


import numpy as np
import os
import beer.components as BC
from matplotlib import pyplot as plt

deg = np.pi/180;
hovm = 6.62607004/1.6749275
_TPULSE = 1/14/25*1000 # source pulse width in ms
_TSRC = 1/14*1000 # source period in ms

# %% Definition of chopper modes

"""
Reference chopper modes (pulse definition)
"""
# chopper modes for: label, PSC1, PSC2, PSC3, MCA, MCB, MCC

cmodes = 9*[0]
cmodes[0] = ['full pulse', 0,  0, 0, 0, 0, 0 ]
cmodes[1] = ['PSC, high flux', 168,  0, -168, 0, 0, 0 ]
cmodes[2] = ['PSC, medium resolution', 168, -168, 0, 0, 0, 0 ]
cmodes[3] = ['PSC, high resolution', 168, -168, 0, 0, 0, 0 ]
cmodes[4] = ['MC, high flux', 0, 0, 0, 70, 0, 0 ]
cmodes[5] = ['MC, medium resolution', 0, 0, 0, 140, 0, 0 ]
cmodes[6] = ['MC, high resolution', 0, 0, 0, 280, 0, 0 ]
cmodes[7] = ['MC, SANS mode', 0, 0, 0, 0, 0, 70 ]
cmodes[8] = ['MC, AB mode', 0, 0, 0, 140, 280, 0 ]

# initial phases [deg]
cphases = 9*[6*[0]]
cphases[1] = [72, 0, 72, 0, 0, 0]
cphases[2] = [72, 72, 0, 0, 0, 0]
cphases[3] = [72, 72, 0, 0, 0, 0]
cphases[7] = [0, 0, 0, 0, 0, -90]

"""
Reference wavelength frame selection modes
"""
# chopper modes for FC1A, FC1B, FC2A, FC2B
wmodes = 5*[0]
wmodes[0] = ['full beam', 0, 0, 0, 0]
wmodes[1] = ['single frame', 28, 0, 14, 0]
wmodes[2] = ['pulse suppression, double frame', 7, 0, 7, 0]
wmodes[3] = ['alternating frames', 14, 63, 0, 7]
wmodes[4] = ['full beam with FC2A', 0, 0, 14, 0]

# initial phases [deg]
wphases = 5*[4*[0]]
wphases[1] = [6, 0, 0, 0]
wphases[2] = [12, 0, 0, 0]
wphases[3] = [-9, 0, 0, 0]



# %% Definition of BEER reference operation modes
modes = 17*[None]

def defMode(ID, slits, foc=True, lam=2.1, cm=[0, 0], PSC2dist=0, FC1A_dphi=0):
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
        distance of the PSC2 chopper [mm], can be 200 or 400. 
        If zero, the default is 200 mm.
    FC1A_dphi: float
        additional adjustment of FCA1 phase
    
    """
    res = {'ID':ID[0], 'label':ID[1], 'comment':ID[2] }
    res['SL3'] = slits[0]
    res['SL2'] = slits[1]
    res['SL1'] = slits[2]
    res['GEX1'] = foc
    res['cmode'] = cm[0]
    res['wmode'] = cm[1]
    res['lam0'] = lam
    if (FC1A_dphi):
        res['FC1A_phi'] = FC1A_dphi
    if (PSC2dist==200 or PSC2dist==400):
        res['PSC2dist'] = PSC2dist
    
    elif PSC2dist != 0:
        raise Exception('PSC2 distance can only be between 200 or 400')
    
    return res

def getMode(ID):
    """
    Return mode data by ID string, or None if not found.
    """
    out = None
    i = 0
    while i<len(modes):
        mod = modes[i]
        if mod['ID'] == ID:
            out = mod
            break
        i += 1
    return out

def getModeIndex(ID):
    """
    Return mode index by ID string, or -1 if not found.
    """
    out = -1
    i = 0
    while i<len(modes):
        mod = modes[i]
        if mod['ID'] == ID:
            out = i
            break
        i += 1
    return out

def getModeKeys():
    """
    Return mode keys (ID strings).
    """
    out = len(modes)*['']
    for i in range(len(modes)):
        out[i] = modes[i]['ID']
    return out

#%% Define operation modes:
i = 0
modes[i] = defMode(
        ID=['F0', 'Maximum white beam', 'never used in experiment'],
        slits=[[0,0], [0,0], [0,0]], foc=1, lam=2.1, cm=[0, 0]
        )
i += 1
modes[i] = defMode(
        ID=['F1', 'Accident full beam', 'F0 with FC choppers running'],
        slits=[[0,0], [0,0], [0,0]], foc=1, lam=3.1, cm=[0, 4]
        )
i += 1
modes[i] = defMode(
        ID=['F2', 'Maximum reduced experimental beam', 'F1, with diffraction slit on'],
        slits=[[10,20], [0,0], [0,0]], foc=1, lam=3.1, cm=[0, 4]
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
        slits=[[5,10], [20,0], [35,0]], foc=1, lam=2.1, cm=[2, 1], PSC2dist=400
        )

i += 1
modes[i] = defMode(
        ID=['PS3', 'High resolution, pulse shaping', 'in-situ thermo mechanical experiment'],
        slits=[[5,10], [15,0], [20,0]], foc=1, lam=2.1, cm=[3, 1], PSC2dist=200
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
        slits=[[10,10], [15,15], [20,20]], foc=0, lam=6.0, cm=[0, 1], FC1A_dphi=-9.0
        )

i += 1
modes[i] = defMode(
        ID=['DS0', 'diffraction + SANS, modulation', 'in-situ thermomechanical experiment'],
        slits=[[5,10], [25,25], [40,40]], foc=0, lam=4.0, cm=[7, 2]
        )

i += 1
modes[i] = defMode(
        ID=['DS1', 'diffraction + SANS, pulse shaping', 'in-situ thermomechanical experiment'],
        slits=[[5,10], [25,25], [40,40]], foc=0, lam=2.1, cm=[1, 3]
        )

i += 1
modes[i] = defMode(
        ID=['M4', 'High resolution, modulation x 4',	'strain scanning'],
        slits=[[1,3], [8,50], [12,0]], foc=0, lam=2.1, cm=[8, 1]
        )

# %%  Define parsing functions

def getModeStr(m):
    """
    Return one line of a table with the given mode definition.
    """
    fmt = '{}\t'*3 + '{:.1f}\t'*6 + '{}\t' + '{:.2f}\t' + '{:d}\t' + '{:d}\n'
    s = fmt.format(m['ID'], m['label'], m['comment'], 
                   *m['SL3'], *m['SL2'], *m['SL1'], m['GEX1'], m['lam0'],
                     m['cmode'], m['wmode'])
    return s

def getCModeStr(m):
    fmt = '\t' + '{}\t' + '\t' + '{}\t'*5 + '{}\n'
    s = fmt.format(* m)
    return s

def getFModeStr(m):
    fmt = '\t' + '{}\t' + '\t' + '{}\t'*3 + '{}\n'
    s = fmt.format(* m)
    return s
    
def modes2str():
    """
    Returns tab-separated text with summary of mode settings.
    Suitable for copying in an excel table.
    """
    out = ''
    fmt = '{}\t{}' 
    
    out += '# Operation modes\n'
    out += '# '
    # Slit settings etc
    hdr = ['No','ID','description','comment','SL3_w','SL3_h','SL2_w','SL2_h','SL1_w','SL1_h','GEX1on','lambda','cmode','wmode']
    for i in range(len(hdr)):
        out += '{}\t'.format(hdr[i])
    out += '\n'
    for i in range(len(modes)):     
        out += fmt.format(i,getModeStr(modes[i]))
    # cmodes
    out += '\n'     
    out += '# Resolution chopper modes [cmode], frequency in Hz\n'
    out += '# '
    hdr = ['ID', ' ', 'description', ' ', 'PSC1', 'PSC2', 'PSC3', 'MCA', 'MCB', 'MCC']
    for i in range(len(hdr)):
        out += '{}\t'.format(hdr[i])
    out += '\n'    
    for i in range(len(cmodes)):
        out += fmt.format(i,getCModeStr(cmodes[i]))
    # cphases
    out += '\n'     
    out += '# Resolution chopper modes [cphases], angular shift in deg\n'
    out += '# '
    hdr = ['ID', ' ', 'description', ' ', 'PSC1', 'PSC2', 'PSC3', 'MCA', 'MCB', 'MCC']
    for i in range(len(hdr)):
        out += '{}\t'.format(hdr[i])
    out += '\n'
    for i in range(len(cmodes)):
        out += fmt.format(i,getCModeStr([cmodes[i][0]]+cphases[i][:]))
    # wmodes
    out += '\n'
    out += '# Wavelength selection chopper modes [wmode], frequency in Hz\n'  
    out += '# '
    hdr = ['ID', ' ', 'description', ' ', 'FC1A', 'FC1B', 'FC2A', 'FC2B']
    for i in range(len(hdr)):
        out += '{}\t'.format(hdr[i])
    out += '\n'
    for i in range(len(wmodes)):
        out += fmt.format(i,getFModeStr(wmodes[i]))
    # wphases
    out += '\n'
    out += '# Wavelength selection chopper modes [wphases], angular shift in deg\n'  
    out += '# '
    hdr = ['ID', ' ', 'description', ' ', 'FC1A', 'FC1B', 'FC2A', 'FC2B']
    for i in range(len(hdr)):
        out += '{}\t'.format(hdr[i])
    out += '\n'
    for i in range(len(wmodes)):
        out += fmt.format(i,getFModeStr([wmodes[i][0]]+wphases[i][:]))
    return out

def getSlitStr(ID, dim=0):
    inf = [80, 80]
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

def getCModesFrq(cmode):
    """
    Returns frequencies from cmodes for given index as string
    """
    cm = cmodes[cmode]
    val = cm[1:]
    n = len(val)
    fmt = '{:.1f}, '*(n-1)+'{:.1f}'
    out = fmt.format(*val)
    return out

def getWModesFrq(wmode):
    """
    Returns frequencies from wmodes for given index as string
    """
    wm = wmodes[wmode]
    val = wm[1:]
    n = len(val)
    fmt = '{:.1f}, '*(n-1)+'{:.1f}'
    out = fmt.format(*val)
    return out

def getCModesPhi(cmode):
    """
    Returns phases from cphases for given index as string
    """
    cm = cphases[cmode]
    val = cm
    n = len(val)
    fmt = '{:.1f}, '*(n-1)+'{:.1f}'
    out = fmt.format(*val)
    return out

def getWModesPhi(wmode):
    """
    Returns phases from wphases for given index as string
    """
    wm = wphases[wmode]
    val = wm
    n = len(val)
    fmt = '{:.1f}, '*(n-1)+'{:.1f}'
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
        if 'PSC2dist' in m:
            val[i] = m['PSC2dist']
        else:
            val[i] = 200.0
    out = fmt.format(*val)
    return out

def getLambdaStr():
    n = len(modes)
    fmt = '{:g}, '*(n-1)+'{:g}'
    val = np.zeros(n)
    for i in range(len(modes)):
        m = modes[i]
        val[i] = m['lam0']
    out = fmt.format(*val)
    return out

def getFC1APhiStr():
    n = len(modes)
    fmt = '{:g}, '*(n-1)+'{:g}'
    val = np.zeros(n)
    for i in range(len(modes)):
        m = modes[i]
        if 'FC1A_phi' in m:
            val[i] = float(m['FC1A_phi'])
        else:
            val[i] = 0.0
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


#%% Chopper phases

def setPhase(F, dist, lam=2.1):
    """ Set phase and frequency for a chopper """
    v = hovm/lam # m/ms
    tof = dist/v # ms
    F['tof'] = tof # ms 

def setPhase2(F1, F2, lam=2.1):
    """
    Set phase and frequency for a pair of pulse shaping choppers
    """
    dist = 0.5*(F1['dist']+F2['dist'])
    setPhase(F1, dist, lam=lam)
    setPhase(F2, dist, lam=lam)

#%% Chopper settings

def chopper(ID, frq=None, phase=0):
    """
    Get chopper settings as a hash map. Optionally set frquency and phase.
    
    Arguments:
    ----------
    ID: string
        ID string in BEER hash table from beer.components
    frq: float
        frequency in Hz
    phase: float
        phase misfit in deg. Moves chopper CCW by given angle. 
    
    Return:
    ------
    Hash map with values:
        id: string
            chopper ID
        dist: float
            distance [m]
        win: list of float
            window widths [fraction of period]
        ctr: list of float
            window centers [fraction of period], counter-clockwise            
        frq: float
            frequency [Hz]
        phi: float
            phase shift, measured as counter-clockwise rotation angle 
            [fraction of period]
        
    """
    if ID in BC.BEER:
        c = {'id':ID, 'dist':BC.BEER[ID]['dist']/1000}
        c['win'] = list(np.divide(BC.BEER[ID]['win'],360.0))
        c['ctr'] = list(np.divide(BC.BEER[ID]['wctr'],360.0))
        c['phi'] = phase/360
        if (frq is not None):
            c['frq'] = frq
        else:
            c['frq'] = float(BC.BEER[ID]['fmax'])
    else:
        c = None
    return c


def chopperset(imode=0):
    """
    Return a set of choppers for given reference mode.
    """
    ids = ['PSC1', 'PSC2', 'PSC3', 'MCA', 'MCB', 'MCC', 'FC1A', 'FC1B', 'FC2A',
           'FC2B']
    mod = modes[imode]
    cmode = mod['cmode']
    wmode = mod['wmode']
    cm = cmodes[cmode]
    wm = wmodes[wmode]
    cp = cphases[cmode]
    wp = wphases[wmode]    
    choppers = []
    frc = cm[1:] # frequencies
    frc.extend(wm[1:])
    phi = cp.copy() # phases
    phi.extend(wp) 
    for i in range(len(frc)):
        f = frc[i]
        if f:
            c = chopper(ids[i], frq=f, phase=phi[i])
            if c:
                # adjust phase shift for FC1A
                if ('FC1A_phi' in mod) and (c['id']=='FC1A'):
                    c['phi'] += mod['FC1A_phi']/360
                # adjust PSC2 chopper distance for given mode
                if ('PSC2dist' in mod) and (c['id']=='PSC2'):
                    c['dist'] = 0.001*(BC.BEER['PSC1']['dist'] + mod['PSC2dist'])
                choppers.append(c)      
    
    return choppers


#%% Chopper adjustment
            
def adjChoppers(choppers, lam=2.1, verbose=0):
    """
    Adjust chopper phases for given wavelength.
    """
    msg = ''
    if len(choppers)==0:
        return
    PS = []
    for c in choppers:
        if c['id'].startswith('PSC'):
            PS.append(c)
    # double PSC chopper mode:
    if (len(PS)==2):
        setPhase2(PS[0], PS[1], lam=lam)
    for c in choppers:
        if not ((c in PS) and (len(PS)==2)):
            setPhase(c, c['dist'], lam=lam)
    for c in choppers:
        fmt = '{}: dist={:g}, frq={:g}, phi={:g}, phase={:g}\n'
        phase = c['tof']*c['frq']/1000 - c['phi']
        msg += fmt.format(c['id'], c['dist'],c['frq'], c['phi'], phase)
    if verbose:
        print(msg)
    return msg


def getChopperFrames(F, jf=0, wrange = [0.1, 20.0], verbose=0):
    """
    Calculate wavelength intervals passed by the chopper, 
    for a ray started at t=0 and for the source pulse No. jf.
    
    Arguments:
    ---------
    F: chopper
        chopper data 
    jf: int
        source pulse number
    wrange: list(2)
        wavelength range
    verbose: int
        set True for additional output
    
    Return:
    -------
    A hash map:

    id: string
        chopper ID
    dist: float
        chopper distance
    npls: int
        source pulse index
    wav: list
        A list of wavelength intervals with period index [[l1,l2, k], [l1,l2, k], ...]
    """
    # frequency in 1/ms
    f = F['frq']/1000
    # conversion time -> wavelength
    t2lam = hovm/F['dist']
    # source period
    ws = jf*_TSRC*t2lam
    # chopper period
    wp = t2lam/abs(f)
    # window centres
    wc = ((np.array(F['ctr']) - F['phi'])/f + F['tof'])*t2lam - ws
    # window widths
    ww = np.array(F['win'])*t2lam/abs(f)
    # determine minimum and maximum chopper period to be considered
    sg = [-1, 1]
    klim = [0, 0]
    for i in range(2):
        wav0 = min(wc - sg[i]*0.5*ww)
        wav = wav0
        k = 0
        while (sg[i]*wav < sg[i]*wrange[i]):
            k = k + sg[i]
            wav = wav0 + k*wp
        klim[i] = k
    
    # construct list of wavelength intervals
    wavs = []
    for k in range(klim[0], klim[1]):
        for j in range(len(wc)):
            w0 = wc[j] + k*wp
            r = [w0 - 0.5*ww[j], w0 + 0.5*ww[j]]
            r1 = [max(wrange[0],r[0]), min(wrange[1],r[1]), k]
            if (r1[1]>r1[0]):
                wavs.append(r1)
    if verbose:
        print('Chopper timing, {}:'.format(F['id']))
        for r in wavs:
            print('{:d}: {:.2f} .. {:.2f}'.format(r[2], r[0], r[1]))
    res = {'id':F['id'], 'dist':F['dist'], 'npls':jf, 'wav':wavs }
    return res
    
#%% Chopper transmission calculations

def getChoppersSpc(choppers, t, w, Ldet=160, t0=0, npls=0, wrange = [0.1, 20.0], verbose=0):
    """
    Calculate choppers spectra for given start time t0
    """
    # collect chopper opening intervals on time and wavelength scales
    frames = [0]*len(choppers)
    for i in range(len(frames)):
        frames[i] = getChopperFrames(choppers[i], jf=npls, wrange = wrange, verbose=verbose)    
    # initiate wavelength and time bins
    nt = len(t)
    nl = len(w)
    dt = (t[nt-1]-t[1])/nt
    dlam = (w[nl-1]-w[1])/nl
    wbins = np.ones(nl)
    tbins = np.ones(nt)
    for i in range(len(frames)):
    #for i in [3]:    
        fr = frames[i]
        dist = fr['dist']
        if (dist<Ldet):
            wavs = fr['wav']
            tshift = t0 + npls*_TSRC  # shift by t0 + source pulse time
            wshift = -t0*hovm/dist # time shift converted to wavelength 
            pw = np.zeros(len(w))
            pt = np.zeros(len(t))
            for j in range(len(wavs)):
                # wavelength range
                wr = np.add(wavs[j][:2],wshift) 
                # time range, account for source pulse index
                tr = np.multiply(Ldet/hovm,wr) + tshift
                # get corresponding index range on wavelength bins
                k1 = int(max(0,round((wr[0]-w[0])/dlam)))
                k2 = int(min(nl-1,round((wr[1]-w[0])/dlam)))
                # set coresponding range of wavelength bins
                if (k2>=k1):
                    pw[k1:k2+1] = 1
                # get corresponding index range on time bins
                k1 = int(max(0,round((tr[0]-t[0])/dt)))
                k2 = int(min(nt-1,round((tr[1]-t[0])/dt)))
                # set coresponding range of time bins
                if (k2>=k1):
                    pt[k1:k2+1] = 1
            wbins = wbins*pw
            tbins = tbins*pt
            if verbose:
                plt.plot(t,pt,label=fr['id'])
    if verbose:        
        plt.ylim(0,1.1)
        plt.legend()
        plt.xlabel('time [ms]')
        plt.show()
    return [wbins, tbins]
    

def getIntegralSpectra(choppers, t, w, Ldet=160, t0=[0,1], npls=0, wrange=[0.1, 20.0]):
    pls = np.array(t0)
    ntp = pls.shape[0]
    if (len(pls.shape)==1):
        tt = pls
        p = np.ones(ntp)
    else:
        tt = pls[:,0]
        p = pls[:,1]
    zn = sum(p)
    p = p/zn
    wbins = np.zeros(len(w))
    tbins = np.zeros(len(t)) 
    for i in range(len(tt)):
        [wb, tb] = getChoppersSpc(choppers, t, w, Ldet=Ldet, t0=tt[i], npls=npls, wrange=wrange)
        wbins = wbins + p[i]*wb
        tbins = tbins + p[i]*tb
    return [wbins, tbins]


def T(F, t):
    dphi =  (t-F['tof'])*F['frq']*1e-3 + F['phi']
    ddphi = dphi - round(dphi)
    dw = ddphi/F['win']*360
    if (abs(dw) < 0.5):
        res = 1.0
    else:
        res = 0.0
    return res

def pulseFnc(t, wt=2.86, tau=0.4):
    """
    Pulse shape function
    """
    if (t<0.0):
        p = 0.0
    elif (t<wt):
        p = 1 - np.exp(-t/tau)
    else:
        p = np.exp(-(t-wt)/tau)
    return p
         

def genPulse(dt=0.1, verbose=0, tail=1):
    """
    Calculate pulse profile time [ms], weight
    """
    n = int((tail+1)*_TPULSE/dt)+1
    src_delay = 0.6*_TPULSE
    tp = np.linspace(-src_delay, n*dt-src_delay, num=n)
    yp = np.zeros(len(tp))
    for i in range(len(tp)):
        yp[i] = pulseFnc(tp[i]+src_delay, wt=_TPULSE)  
    pulse = np.array([tp,yp]).T
    if verbose:
        plt.plot(tp, yp,'-r')
        plt.ylim(0)
        plt.show()
    return pulse

#%% Top level output functions

def plotChoppersSpec(ax, x, y, pulses, imode, xval='time', title = ''):
    """
    Plot calculated intensities transmitted through choppers on given axis.
    """
    MEDIUM_SIZE = 10
    BIGGER_SIZE = 12    
    colors=['blue', 'black', 'red', 'green', 'purple', 'royalblue']
    sbls = ['--', '-', '--', '-', '--', '-']
    cpls = [-1, 0, 1, 2, 3, 4]
    npls = len(pulses)
    if (xval=='frame'):
        xx = x/_TSRC
    else:
        xx = x
    for i in range(npls):
        ip = pulses[i]
        if (ip in cpls):
            c = colors[cpls[i+1]]
            s = sbls[cpls[i+1]]
        else:
            c = 'darkgray'
            s = ':'
        lbl = 'pulse={:d}'.format(ip)
        ax.plot(xx,y[i], s, color=c, label=lbl)
    ax.set_ylim(0) 
    if (xval=='time'):
        ax.set_xlabel('time [ms]')
    elif (xval=='frame'):
        ax.set_xlabel('source periods', fontsize=BIGGER_SIZE)
    else:
        ax.set_xlabel('wavelength [A]', fontsize=BIGGER_SIZE)
    ax.set_ylabel('intensity', fontsize=12)
    ax.minorticks_on()
    ax.tick_params(axis='both', labelsize=MEDIUM_SIZE)

    ax.grid(True, which='major', axis='x')

    if title:
        ax.set_title(title)
    if (xval=='frame'):
        mod = modes[imode]
        wavelength = mod['lam0']
        if (wavelength>3):
            loc = 'upper left'
        else:
            loc = 'upper right'
    else:
        loc = 'upper right'
    ax.legend(framealpha=1.0, loc=loc, fontsize=MEDIUM_SIZE)


def listModes():
    """
    Print a short table with the list of defined modes.
    """
    out = '# Operation modes\n'
    # Slit settings etc
    hdr = ['No','ID','description','comment']
    for i in range(len(hdr)):
        out += '{}\t'.format(hdr[i])
    out += '\n'
    for i in range(len(modes)): 
        m = modes[i]
        fmt = '{}\t'*3 + '{}\n'
        out += fmt.format(i, m['ID'], m['label'], m['comment'])
    print(out)
    
    
def reportModes(file = 'BEER_modes.txt'):
    """
    Export tables with modes settings as a tab separated text.
    """
    if file:
        with open(file, 'w') as f: 
            f.write(modes2str())
            f.close()
            print('BEER modes reported in {}'.format(file))


def reportChoppers(imode=1, wrange=[0.5, 20, 0.05], trange=[0, 400, 0.02],
                   pulses=[0], wavelength=0, pdf=''):
    """ Report on chopper settings for selected reference mode. Prints parameters
    of active choppers and plot ToF and wavelength transmissivity distributions 
    at the detector. Actual source spectrum is not considered, assumes 
    uniform spectrum. 
    
    Arguments:
    ----------
    imode: int
        reference mode index
    wrange: list(3)
        wavelength range: [min, max, step]
    trange: list(3)
        time range: [min, max, step]
    pulses: list of int
        pulse indices to include    
    wavelength: float
        wavelength [A] used to adjust choppers. If zero, the wavelength defined
        for given reference mode is used. 
    pdf: str
        if defined, figure is saved under this filename in PDF format
    """  
    mod = modes[imode]
    cmode = mod['cmode']
    wmode = mod['wmode']
    if (not wavelength):
        wavelength = mod['lam0']
    
    msg = ''
    msg += '\nReference mode [{:d}], {}\n'.format(imode,mod['ID'])
    msg += '{}, {}, {}\n'.format(mod['label'],cmodes[cmode][0],wmodes[wmode][0])
    msg += 'Chopper settings (cmode={:d}, wmode={:d}, lambda={:g}):\n'.format(cmode,wmode,wavelength)
    # set choppers according to required operation mode
    cs = chopperset(imode=imode)
    msg += adjChoppers(cs, lam=wavelength, verbose=0)
    # define time bins [ms]
    nt = int((trange[1]-trange[0])/trange[2])
    t = np.linspace(trange[0]+0.5*trange[2], trange[0]+(nt-0.5)*trange[2], num=nt)
    # define wavelength bins
    nl = int((wrange[1]-wrange[0])/wrange[2])
    w = np.linspace(wrange[0]+0.5*wrange[2], wrange[0]+(nl-0.5)*wrange[2], num=nl)
    # generate pulse profile
    pls = genPulse(dt=trange[2], verbose=0)

    npls = len(pulses)
    wbins = npls*[0]
    tbins = npls*[0]
    for i in range(npls):
        n = pulses[i]
        [wbins[i], tbins[i]] = getIntegralSpectra(cs, t, w, Ldet=160, t0=pls, npls=n, wrange=wrange)
   
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(8,6))
    #ax = axs[0]

    # plot t-bins
    title = 'Mode({:d}) {}, {}, {}'.format(imode, mod['ID'], cmodes[cmode][0],wmodes[wmode][0])
    plotChoppersSpec(axs[0], t, tbins, pulses, imode, xval='frame')
    # plot w-bins
    plotChoppersSpec(axs[1], w, wbins, pulses, imode, xval='wavelength')
    fig.suptitle(title)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    # fig.tight_layout()
    print(msg)
    if pdf:
        pname = os.path.normpath(pdf)
        if not pname.endswith('.pdf'): pname += '.pdf'
        plt.savefig(pname, bbox_inches='tight')
        print('Plot saved as '+pname)
    plt.show()
    return msg


