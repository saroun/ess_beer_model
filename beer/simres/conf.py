# -*- coding: utf-8 -*-
"""
Export of SIMRES configuration scripts.

Usage:
------

`createScriptSetup()` creates SIMRES script for configuring BEER according to 
current beam geometry and component parameyters as defined in beer.geometry 
and beer.components. 

`scriptMode()` returns SIMRES script for setting BEER to given operation mode

Created: October 13, 2018, 2018
@author: J. Saroun, saroun@ujf.cas.cz
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez

update 2019-08-27:
    Adjusted NBOA+BBG according actual drawings
    Adjusted shutter pit , W02-13 to W02-15 according actual drawings.
    
update 2020-03-04:
    Moved to submodule beer and renamed from BEER_simres.py.
    added GE2AS guide segment to match updated beer.components
    
update 2020-05-11: 
    Updated according to the final CAD model submitted to TG3 review.
    Added W02-19 miniguide. Update of distances and gaps measured in CAD. 
    Geometry of the beam and optical surfaces remains unchanged.    

"""

import numpy as np

import os
import beer.geometry as BG
import beer.components as BC
import beer.modes as BMOD
deg = np.pi/180;

# instrument and source component names
_INST = 'INST'
_SOURCE = 'SOURCE'
_seg_exchanger = [367, 250, 250, 250, 250, 200, 200, 100]

key0 = 'GT1'
key1 = 'FC2A'




# %% SIMRES setup for BEER, basic parameters


def sectionHeader(name):
    fmt = '#'+30*'-'+'\n'+'# {}\n'+'#'+30*'-'+'\n'
    return fmt.format(name)


def getPreviousDistance(key0):
    if (key0 is None):
        L0 = 0.
    else:
        L0 = BC.BEER[key0]['start']
        typ = BC.BEER[key0]['type']
        if (typ == 'chopper' or typ == 'slit'):
            L0 += 0.5*BC.BEER[key0]['thickness']
    return L0

def getRelDistance(key0, key1):
    """Calculate SIMRES distance bewteen components.
    
    In the `beer.components` module, the componet distances are measured along x_ISCS axis. 
    In SIMRES, the distance is take along actual incident axis direction. hence 
    we need to make corrections when setting up SIMRES to match 
    the definition in `beer.components` exactly.
    """
    if key0:
        comp0 = BC.BEER[key0]
        r0 = BG.beamAxis(comp0['dist'])
    else:
        r0 = np.zeros(3)
    comp1 = BC.BEER[key1]
    #a1 = BG.beamAngle(comp1['dist'])
    r1 = BG.beamAxis(comp1['dist'])
    #dist = (r1[0]-r0[0])/np.cos(a1)
    dist = (r1[0]-r0[0])
    # fmt = 'angle={:g}, r=['+3*'{:g} '+']'
    # print(key0, fmt.format(a0, *r0))
    # print(key1, fmt.format(a1, *r1))
    # print('distance', r1[0]-r0[0], dist) 
    return dist


def infoSegments(key, seg=500., segm=None, gap=0.2):
    comp = BC.BEER[key]
    x1 = comp['start']
    x2 = comp['end']
    L = x2-x1
    """ If seg is scalar: define equidistant segmentation.
        If seg is a list: use provided segmentation until the guide length.
        Adjust the last segment for required length.
    """
    if (type(seg) == float):
        Lseg = seg
        nseg = int(np.ceil(L/Lseg))
        sg = nseg*[Lseg]
        last = L - sum(sg[:-1])
        sg[nseg-1] = last
    else:
        x = seg[0]
        sg = []
        i = 0
        n = len(seg)
        while (x < L and i < n-1):
            sg.append(seg[i])
            i += 1
            x += seg[i] 
        last = L - sum(sg)
        sg += [last]
    
    nseg = len(sg)
    segments = []
    x = 0.
    for i in range(nseg):
        Lseg = sg[i]
        x += Lseg
        if comp['const']:
            w,h = comp['entry']
        else:
            p = BG.beamSize(x1 + x,coord='ISCS').reshape((6,))
            w = p[4]
            h = p[5]
        z = Lseg
        if (i==0 or i==nseg-1):
            z -= 0.5*gap
        else:
            z -= gap
        if (segm == None):
            m = comp['m']
        else:
            m = segm[i]
        s = [w, h, z] + m
        fmt = 2*'{:.2f} '+'{:.1f} ' + 3*'{:g} '+'{:g}'
        segments.append(fmt.format(* s))
    return segments
    

def infoTilt(key):
    comp = BC.BEER[key]       
    [w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(comp, coord = 'ISCS')    
    length = comp['end']-comp['start']
    angle = np.arctan2(ctr2-ctr1, length)
    info = {}
    info['shift'] = '{:.2f}'.format(ctr1)
    info['angle'] = '{:.4f}'.format(angle/deg)
    return info
        
def infoGUIDE(key, key0=None):
    comp = BC.BEER[key]       
    data = BC.getComponentData(comp, coord = 'ISCS')
    ID = data['name']
    #L = comp['start'] - L0
    #L0 = getPreviousDistance(key0)
    L = getRelDistance(key0, key)
    rho = [0., 0.]
    RH = comp['RH']
    RV = comp['RV']
    if (RH != 0):
        rho[0] =  1e-3/RH
    if (RV != 0):
        rho[1] =  1e-3/RV
    info = {}
    info['ID'] = ID
    info['DIST'] = '{:.2f}'.format(L)
    info['SIZE'] = [data['w1'], data['h1'], data['length']]
    info['EXIT'] = [data['w2'], data['h2']]
    info['M'] = [data['mL'], data['mR'], data['mT'], data['mB']]
    if (rho[0] != 0. or rho[1] != 0.):
        info['RHO'] = '{:g} {:g}'.format(*rho)
    return info

def infoSGUIDE(key, seg = 500., segm = None, gap = 0.2):
    sgm = infoSegments(key, seg=seg, segm=segm, gap=gap)
    info = {}
    info['sgm'] = sgm
    return info


#-----------------------------------------
# Functions generating configuration strings:
#-----------------------------------------

def cfgGuideBasic(info):
    ID = info['ID']
    dist='SET {} DIST {}\n'
    size='SET {} SIZE {} {} {}\n'
    ex='SET {} EXIT {} {}\n'
    out ='# '+info['ID']+'\n'
    out += dist.format(ID, info['DIST'])
    out += size.format(ID, *info['SIZE'])
    out += ex.format(ID, *info['EXIT'])
    if ('shift' in info):
        out += 'SET {} STA(1) {}\n'.format(ID, info['shift'])
    if ('angle' in info):
        out += 'SET {} GON(1) {}\n'.format(ID, info['angle'])
    return out
    

def cfgSGUIDE(key, seg = 500., segm = None,  key0=None, isTilted=False):
    info = infoGUIDE(key, key0=key0)
    info.update(infoSGUIDE(key, seg = seg, segm=segm))
    if (isTilted):
        info.update(infoTilt(key))
    ID = info['ID']
    out = cfgGuideBasic(info)
    if ('RHO') in info:
        out += 'SET {} RHO {}\n'.format(ID, info['RHO'])
    sgm = info['sgm']
    nseg = len(sgm)
    # pass NSEG as negative number and call XML to recreate the segments structure
    out += 'SET {} NSEG {}\n'.format(ID, -nseg)
    out += 'XML {}\n'.format(ID)
    # set segments data
    fmt = 'SET {} SEG({}) {}\n'
    for i in range(nseg):
        out += fmt.format(ID, i+1, sgm[i]) 
    out += 'XML {}\n'.format(ID)
    return out   

def switchExchanger(on=True):
    ID = 'GEX1'
    if on:
        info = infoSGUIDE(ID, seg = _seg_exchanger)
    else:
        info = infoSGUIDE('GEX2', seg = _seg_exchanger)
    sgm = info['sgm']
    nseg = len(sgm)
    # set segments data
    fmt = 'SET {} SEG({}) {}\n'
    out = '# Switch exchanger\n'
    for i in range(nseg):
        out += fmt.format(ID, i+1, sgm[i]) 
    out += 'XML {}\n'.format(ID)
    return out
        
    
    

def cfgGUIDE(key, key0=None, isTilted=False):
    info = infoGUIDE(key, key0=key0)
    if (isTilted):
        info.update(infoTilt(key))
    ID = info['ID']
    mval = 'SET {} M {} {}\n'
    out = cfgGuideBasic(info)
    out += mval.format(ID, info['M'][0], info['M'][2])    
    out += 'XML {}\n'.format(ID)
    return out

def cfgDist(key, key0=None):
    comp = BC.BEER[key]       
    ID = comp['key']
    #L0 = getPreviousDistance(key0)
    #L = comp['start'] - L0
    L = getRelDistance(key0, key)
#    if (comp['type'] == 'chopper' or comp['type'] == 'slit'):
#        L += 0.5*comp['thickness']
    dist='SET {} DIST {:.1f}\n'
    out ='# '+ID+'\n'
    out += dist.format(ID, L)
    out += 'XML {}\n'.format(ID)
    return out


def cfgChopperTiming(key, phase=0):
    """Generate chopper timing string.
    
    The format is ``ctr1:win1:ctr2:win2:...``
    
    ctr = window center
    
    win = window width
    
    as a fraction of period.
    
    Parameters
    ----------
    key: str
        chopper ID
    phase: float
        additional angular shift, usually taken from beer.modes 
    """
    comp = BC.BEER[key]
    wins = comp['win']
    wctr = comp['wctr']
    wmin = min(wins)
    tt = ''
    for i in range(len(wins)):
        if (i>0):
            tt += ':'
        tt += '{:g}:{:g}'.format((phase+wctr[i])/360, wins[i]/wmin )    
    return tt

def cfgChopper(key, key0=None):
    comp = BC.BEER[key]
    if not comp or not comp['type'] == 'chopper':
        raise Exception('Wrong component type for cfgChopper')
    ID = comp['key']
#    L0 = getPreviousDistance(key0)
#    L = comp['start'] - L0 + 0.5*comp['thickness']   
    L = getRelDistance(key0, key)
    wins = comp['win']
    # minimum window width
    wmin = min(wins) 
    # get timing string
    tt = cfgChopperTiming(key)
    out ='# '+ID+'\n'
    out += 'SET {} DIST {:.1f}\n'.format(ID, L)
    out += 'SET {} SIZE(3) 20\n'.format(ID) 
    out += 'SET {} NWIN {:d}\n'.format(ID,len(wins))
    out += 'SET {} WIN {:.5g}\n'.format(ID, wmin/360)
    out += 'SET {} TIMING {}\n'.format(ID, tt)
    out += 'XML {}\n'.format(ID)
    return out


def cfgMonolithSection():
    out = sectionHeader('Monolith section')
    seg = 4*[250.] + 5*[500.]
    #seg = 8*[125.] + 10*[250.]
    #seg = 4*[1000.] 
    out += cfgSGUIDE('NBOA', seg = seg, key0=None, isTilted=True)
    out += cfgGUIDE('BBG', key0='NBOA', isTilted=True)
    out += '\n'
    return out

def cfgChopperSection():
    out = sectionHeader('Chopper section')
    out += cfgDist('GSW', key0='BBG')
    out += cfgGUIDE('GCA1', key0='GSW')
    out += cfgChopper('PSC1', key0='GCA1' )
    out += cfgGUIDE('GCA2', key0='PSC1' )
    out += cfgChopper('PSC2', key0='GCA2' )
    out += cfgGUIDE('GCB', key0='PSC2' )
    out += cfgChopper('PSC3', key0='GCB' )
    out += cfgGUIDE('GCC', key0='PSC3' )
    out += cfgChopper('FC1A', key0='GCC' )
    out += cfgChopper('FC1B', key0='FC1A' )
    out += cfgGUIDE('GCE', key0='FC1B' )
    out += cfgChopper('MCA', key0='GCE' )
    out += cfgChopper('MCB', key0='MCA' )
    out += cfgGUIDE('GCF', key0='MCB' )
    out += cfgChopper('MCC', key0='GCF' )
    out += cfgGUIDE('GCG', key0='MCC' )
    out += '\n'
    return out

def cfgBunkerSection():
    out = sectionHeader('Bunker section')
    # out += cfgSGUIDE('GE1', seg = 500., key0='GCG')
    out += cfgSGUIDE('GE1A', seg = 500., key0='GCG')
    out += cfgSGUIDE('GE1B', seg = 500., key0='GE1A')
    out += cfgSGUIDE('GN1', seg = 500., key0='GE1B')
    out += cfgSGUIDE('GN2', seg = 500., key0='GN1')
    out += cfgGUIDE('GSH2', key0='GN2')
    out += '\n'
    return out

def cfgTransportSection():
    out = sectionHeader('Transport section')
    out += cfgGUIDE('GE2AS', key0='GSH2' )
    out += cfgSGUIDE('GE2A', seg = 1000., key0='GE2AS')
    out += cfgSGUIDE('GE2B', seg = 1000., key0='GE2A')
    out += cfgSGUIDE('GT1', seg = 2000., key0='GE2B')
    out += cfgChopper('FC2A', key0='GT1' )
    out += cfgChopper('FC2B', key0='FC2A' )
    out += cfgSGUIDE('GT2', seg = 2000., key0='FC2B')
    out += '\n'
    return out

def cfgFocusingSection():
    out = sectionHeader('Focusing section')
    out += cfgSGUIDE('GF1', seg = 500., key0='GT2')
    out += cfgDist('SL1', key0='GF1')
    seg = 6*[500.]
    m = BC.BEER['GF2']['m']
    segm = 5*[m] + 1*[[0., 0., m[2], m[3]]]
    out += cfgSGUIDE('GF2', seg = seg, segm = segm, key0='SL1')
    out += cfgDist('SL2', key0='GF2')
    out += cfgGUIDE('GMINI', key0='SL2')
    out += cfgSGUIDE('GEX1', seg = _seg_exchanger, key0='GMINI')
    out += cfgDist('SL3', key0='GEX1')
    out += '\n'
    return out


def createScriptSetup(file = 'BEER_setup.inp', outpath='', save=''):
    """Create input script for SIMRES.
    
    Sets basic setup parameters for BEER components as defined in 
    beer.geometry and beer.components modules.
    
    Arguments
    ---------
    file: str
        Output file name
    outpath: str
        Output directory for the generated script file (include trailing /)
    save: str
        Optional instrument file name to save at the end of script
    """
    if file:
        outfile = os.path.normpath(os.path.join(outpath,file))
        out = cfgMonolithSection()
        out += cfgChopperSection()
        out += cfgBunkerSection()
        out += cfgTransportSection()
        out += cfgFocusingSection()
        
        if save:
            # we must use absolute path from the SIMRES script, 
            # otherwise output goes to output directory
            if not os.path.isabs(save):
                save = os.path.abspath(save)            
            out += 'cmd SAVE FILE {}\n'.format(save)
            out += 'do SAVE\n'
        with open(outfile, 'w') as f: 
            f.write(out)
            f.close()
            print('SIMRES setup script saved as {}'.format(outfile))


# %% SIMRES configuration scripts for reference modes settings

def setHeader(comment, underline=True):
    """Print header to a command block."""
    out = '\n# {}\n'.format(comment)
    if underline:
        out += '#' + 70*'-' +'\n'
    return out
    
def setSource(thermal='ESS2016_W2_thermal', cold='ESS2016_W2_cold', 
              comment='Set source tables', short=True):
    """Define source.
    
    Set either thermal or cold to None or empty string in order to define
    mono-spectral source.
        
    Arguments
    ---------
    thermal: str
        thermal moderator table name without extension
    cold: str
        cold moderator table name without extension
    short: boolean
        If true, the pulse width is limited to 5 ms. Otherwise it is 10 ms.
        
    """
    ID = _SOURCE
    if short:
        sfx = '_5ms.tab'
        delay = 5/2-1.6
    else:
        sfx = '.tab'
        delay = 10/2-1.6
    out = setHeader(comment)
    out += 'set {} FLUXTAB '.format(ID)
    if thermal:
        out += thermal+sfx
        if cold:
            out += ':'
    if cold:
        out += cold+sfx
    out += '\nset {} OVERLAP 0\n'.format(ID)
    out += 'set {} DELAY {:g}\n'.format(ID, delay)
    out += 'XML {}\n'.format(ID)
    return out

def setWRange(lrange=[0.2, 10.2], comment='Set wavelength range', underline=False):
    """Set wavelength range."""
    lam0 = 0.5*(lrange[0] + lrange[1])
    dlam = (lrange[1] - lrange[0])/lam0
    if comment:
        cm = ', {:g} .. {:g}'.format(* lrange)
        out = setHeader(comment+cm, underline=underline)
    else:
        out = '\n'
    out += 'set {} LAMBDA {:g}\n'.format(_INST,lam0)
    out += 'set {} LAMW {:.5f}\n'.format(_SOURCE, dlam)
    out += 'XML UPDATE\n'
    return out

def setMisalignment(d=0.02, guides=[]):
    """
    Set misalignment to all guides.
    
    Argument:
    ------
    d: float
        misalignment in mm
    guides: list
        list of guides id to be set. If empty, set all choppers of BEER
    """
    out = setHeader('Set misalignment {} mm'.format(d))
    if len(guides)==0:
        lst = BC.BEER.keys()
    else:
        lst = guides
    for key in lst:
        comp = BC.BEER[key]
        if comp['type'] == 'optics':
            if isinstance(d, list):
                out += 'SET {} MISALIGN {:g} {:g}\n'.format(key, *d)
            else:
                out += 'SET {} MISALIGN {:g} {:g}\n'.format(key, d, d)
    return out

def setWaviness(w=0.2, guides=[]):
    """
    Set guide waviness for all guides.
    
    Argument:
    ------
    w: float
        waviness (RMS) in mrad
    guides: list
        list of guides id to be set. If empty, set all choppers of BEER        
    """
    out = setHeader('Set waviness {:g} mrad'.format(w))
    if len(guides)==0:
        lst = BC.BEER.keys()
    else:
        lst = guides
    for key in lst:
        comp = BC.BEER[key]
        if comp['type'] == 'optics':
            out += 'SET {} WAV {:g}\n'.format(key, w)
    return out

def setOverlap(over=False, choppers=[]):
    """
    Set chopper overlap for all choppers.
    
    Argument:
    ------
    over: boolean
        overlapping flag for all choppers
    choppers: list
        list of choppers id to be set. If empty, set all choppers of BEER
    """
    if over:
        iov = 1
        msg = 'To check for frame overlaps, set choppers like this:\n'
    else:
        iov = 0
        msg = 'To ignore  frame overlaps and speed up simulation, set choppers like this:\n'
    ovstr = ['off', 'on']
    
    out = setHeader('Set chopper overlapping {}'.format(ovstr[iov]))
    out += '# '+msg
    if len(choppers)==0:
        lst = BC.BEER.keys()
    else:
        lst = choppers
    for key in lst:
        comp = BC.BEER[key]
        if comp['type'] == 'chopper':
            out += 'SET {} OVERLAP {:d}\n'.format(key, iov)
    return out

def setCollimator(w=1.0, ID='RAD'):
    """Sett radial collimator for given gauge width.
    
    Only defined are [0.5, 1, 2, 3, 4] mm
    """
    wset = [0.5, 1, 2, 3, 4]
    wnames = ['RAD05', 'RAD1', 'RAD2', 'RAD3' 'RAD4']
    out = ''
    if w in wset:
        ic = wset.index(w)
        col = BC.RADC[wnames[ic]]        
        out += setHeader('Set radial collimator width {:g} mm'.format(w))
        out += 'SET {} SIZE {:g}  {:g} {:g}\n'.format(ID, * col['entry'], col['length'])
        out += 'SET {} EXIT {:g}  {:g}\n'.format(ID, * col['exit'])
        out += 'SET {} DIST {:g}\n'.format(ID, col['dist'])
        out += 'XML {}\n'.format(ID)
        out += 'SET DET DIST {:g}\n'.format(2000 - col['dist'])
        out += 'XML DET\n'
    return out


def setChopperOff(ID):
    """Stop given chopper in open position."""
    out = ''
    comp = BC.BEER[ID]
    if comp and comp['type']=='chopper':
        out += setHeader('{} off'.format(ID), underline=False)
        out += 'set {} FRQ 0\n'.format(ID)
        out += 'set {} TIMING {}\n'.format(ID, cfgChopperTiming(ID, phase=0))
        out += 'set {} T0 0\n'.format(ID)
        out += 'set {} LOCKT0 0\n'.format(ID)
        out += 'set {} ADJ 1\n'.format(ID)
        out += 'XML {}\n'.format(ID)
    return out

def setSlit(ID, size=[5, 10]):
    out =  'set {} SIZE(1) {:g}\n'.format(ID,size[0])
    out += 'set {} SIZE(2) {:g}\n'.format(ID,size[1])
    out += 'XML {}\n'.format(ID)
    return out
    
def setSlits(imode):
    """Set slits for given BEEER mode."""
    out = setHeader('Setting slits for mode={:d}'.format(imode), underline=False)
    slits = ['SL1', 'SL2', 'SL3']
    for s in slits:
        sz = BMOD.modes[imode][s]
        if sz[0]==0:
            sz[0]=100
        if sz[1]==0:
            sz[1]=100
        out += setSlit(s, size=sz)
    #gex = '# # # #'.replace('#', str(BMOD.modes[imode]['GEX1']))
    #out += 'set GEX1 ACTIVE {}\n'.format(gex)
    #out += 'XML GEX1\n'
    return out

def setExchanger(imode):
    """Switch Exchanger on or off."""
    gex = BMOD.modes[imode]['GEX1']
    if not gex:
        out = setHeader('Setting exchanger as collimator')
        out += switchExchanger(on=False)
    else:
        out = setHeader('Setting exchanger as focusing guide')
        out += switchExchanger(on=True)
    return out
        


def setMode0():
    """Set mode F0 with all choppers stopped.
    
    This should be the initial state for switching to any other mode.
    """
    out = setHeader('Stop resolution choppers', underline=False)
    cchoppers = ['PSC1','PSC2', 'PSC3', 'MCA', 'MCB', 'MCC']
    wchoppers = ['FC1A','FC1B', 'FC2A', 'FC2B']
    for key in cchoppers:
        out += setChopperOff(key)
    out += setHeader('Stop wavelength selection choppers', underline=False)
    for key in wchoppers:
        out += setChopperOff(key)
    out += setSlits(0)
    out += setExchanger(0)
    return out


def adjChopper(chopper, isPSC=False, isMC=False, overlap=False):
    """Script for adjustment of given chopper.
    
    Parameters
    ----------
    chopper: 
        chopper data in the format returned by beer.modes.chopper
    isPSC: boolean
        true of it is one of a pair of pulse shaping choppers in blind mode.
    isMC: boolean
        tru if it is a modulation chopper
    overlap: boolean
        switch chopper frame overlap on/off
    """
    ID = chopper['id']
    timing = cfgChopperTiming(ID, phase=chopper['phi']*360)
    out = setHeader('{} on'.format(ID), underline=False)
    out += 'set {} FRQ {:g}\n'.format(ID,chopper['frq'])
    out += 'set {} TIMING {}\n'.format(ID,timing)
    if isPSC:
        out += 'set {} T0 1\n'.format(ID)
        out += 'set {} LOCKT0 1\n'.format(ID)
    elif isMC:
        out += 'set {} T0 1\n'.format(ID)
        out += 'set {} LOCKT0 0\n'.format(ID)
    # always set overlap for MC choppers
    if (isMC or overlap):
        out += 'set {} OVERLAP 1\n'.format(ID)
    out += 'XML {}\n'.format(ID)
    return out
    
    
def adjAllChoppers(imode):
    """Script section for adjustment of all choppers for given BEER mode."""
    pchoppers = ['PSC1','PSC2', 'PSC3']
    mchoppers = ['MCA', 'MCB', 'MCC']    
   # wchoppers = ['FC1A','FC1B', 'FC2A', 'FC2B']
    out = ''
    m = BMOD.modes[imode]    
    cs = BMOD.chopperset(imode=imode)
    BMOD.adjChoppers(cs, lam=m['lam0'], verbose=0)
    for c in cs:
        isPSC = c['id'] in pchoppers
        isMC =  c['id'] in mchoppers
        isFC = not (isPSC or isMC)
        if isFC:
            over = (imode<3)
        elif isMC:
            over = True
        else:
            over = False
        out += adjChopper(c, isPSC=isPSC, isMC=isMC, overlap=over)
    return out

def setChopperAdj(imode, value):
    """Set ADJ flag (auto adjust) for all choppers running for given mode."""
    sv = ['off', 'on']
    if value:
        v = 1
    else:
        v = 0
    out = ''
    cs = BMOD.chopperset(imode=imode)
    if len(cs)>0:
        out += '\n# Set auto-adjust {}\n'.format(sv[v])
        for c in cs:
            out += 'set {} ADJ {:d} \n'.format(c['id'],v)
            out += 'XML {} \n'.format(c['id'])
    return out
 
def adjWavelength(imode, lrange=[0.2, 10.2]):
    """Set wavelength and adjust chopper phases."""
    m = BMOD.modes[imode] 
    lam = m['lam0']
    lmax = lrange[1]
    dlam = (lmax-lam)*2
    lmin = lam - 0.5*dlam   
    out = ''
    out += setHeader('Adjust choppers for wavelength {:g}'.format(lam), 
                     underline=False)
    out += adjAllChoppers(imode)
#    out += '\n# set wavelength for alignment \n'
#    out += 'set {} LAMBDA {:g}\n'.format(_INST,lam)
    out += setChopperAdj(imode, 1)
    out += setWRange(lrange=[lmin, lmax], comment='')
    #out += '\nXML UPDATE\n'
    return out 

def setPSCdist(imode):
    """Generate SIMRES script for seting PSC2 distance.

    Set the PSC2 chopper distance required for given mode.  
    
    Assumes no guides attached to the movable chopper. 
    
    """
    m = BMOD.modes[imode]
    
    out = ''
    if 'PSC2dist' in m:        
        # required PSC2-PSC1 distance
        PSC2dist = m['PSC2dist']        
        # absolute distance of GCB is constant  
        GCBstart = BC.BEER['GCB']['start']    
        # relative distance of GCA2 from PSC1 is constant
        GCA2_PSC1 = BC.BEER['GCA2']['start'] - BC.BEER['PSC1']['dist'] 
        
        
        # new relative distance of PSC2 from GCA2
        PSC2_GCA2 = PSC2dist - GCA2_PSC1
        # new rel. distance of GCB from PSC2
        GCBdist = GCBstart - BC.BEER['PSC1']['dist'] - PSC2dist
        
        fmt = 'set {} dist {:g}\nXML {}\n'
        out += '\n'
        key = BC.BEER['PSC2']['key']
        out += fmt.format(key,PSC2_GCA2, key)
        key = BC.BEER['GCB']['key']
        out += fmt.format(key,GCBdist, key)
    return out
        


def scriptPlot(imode, what='lam', lrange=[0.2, 10.2], nx=100, suffix=''):
    """Create script section for plotting and saving graphs.
    
    Parametes:
    ----------
    imode: int
        BEER reference mode index (defined in beer.modes)
    what: str
        One of ['x', 'y', 'kx', 'ky', 'lam']
        Defines which kind of plot to save (corresponds to the x-coordinate 
        from BEAM1D SIMRES command), e.g. 'lam' stands for wavelength, 'kx' is
        horizontal divergence (kx/k).
    lrange: list(2) of float
        wavelength range
    nx: int
        number of bins
    suffix: str
        suffix to be added to mode ID when constructing output file
    """
    x = ['x', 'y', 'kx', 'ky', 'lam', 't']
    xval = [0, 1, 3, 4, 8, 6]
    out = '\n'
    m = BMOD.modes[imode]
    comment = 'mode {}{}'.format(m['ID'],suffix)
    ix = x.index(what)
    xv = xval[ix]
    out += 'cmd BEAM1D X {:d}\n'.format(xv)
    if lrange:
        x0 = 0.5*(lrange[0]+lrange[1])
        dx = lrange[1] - lrange[0]
        out += 'cmd BEAM1D X0 {:g}\n'.format(x0)
        out += 'cmd BEAM1D DX {:g}\n'.format(dx)
        out += 'cmd BEAM1D XAUTO 0\n'
    else:
        out += 'cmd BEAM1D XAUTO 1\n'
    out += 'cmd BEAM1D NP {:d}\n'.format(nx)
    out += 'cmd BEAM1D COM {}\n'.format(comment)
    out += 'do BEAM1D\n'
    out += 'cmd GRSAVE FILE {}{}_{}.dat\n'.format(m['ID'],  suffix, what)
    out += 'cmd GRSAVE OVER no\n'
    out += 'do GRSAVE\n'
    
    return out

    
def scriptMode(imode, ncnt=10000, lrange=[0.2, 10.2], exe=True, 
               plot=['x', 'y', 'kx', 'ky', 'lam', 't'],
               upstream=True):
    """Return script for setting and execution of given BEER mode.
    
    Arguments:
    ---------
    imode: it
        BEER mode index as defined in beer.modes
    ncnt: int
        number of final counts
    lrange: list(2)
        wavelength range [A]
    exe: boolen
        if true, add simulation execution
    plot: list
        a list of strings indicating output data files: 
        variable names from BEAM1D command and suffixes to output file names.
    upstream: boolean
        If false, switch for down-stream tracing
    """
    m = BMOD.modes[imode]
    cm = m['cmode']
    wm = m['wmode']
    out = '\n#' + 70*'-'
    hdr = '{:d}, {}, {}, {}, {}'.format(imode, m['ID'], m['label'], 
           BMOD.cmodes[cm][0], BMOD.wmodes[wm][0] )
    out += setHeader(hdr, underline=True)
    if (imode>0):
        out += adjWavelength(imode, lrange=lrange )
        out += setPSCdist(imode)
        out += setSlits(imode)
        out += setExchanger(imode)
    else:
        out += setMode0()
    if exe:
        if upstream:
            out += '\nset TR DIR 1\n'
        else:
            out += '\nset TR DIR 0\n'
        if ncnt:
            out += '\nset TR CNT {:g}\n'.format(ncnt)
        out += '\nDO MC\n'
    if plot:
        for p in plot:
            if p=='lam':
                out += scriptPlot(imode, what=p, lrange=lrange)
            else:
                out += scriptPlot(imode, what=p, lrange=None)
    return out

    
def scriptDS1(imode, ncnt=10000, lrange=[0.2, 10.2], exe=True, 
               plot=['x', 'y', 'kx', 'ky', 'lam', 't'],
               upstream=True):
    """Call scriptMode().
    
    If imode corresponds to the 'DS1' mode 
    (pulse suppression with alternate frames), then include 2nd simulations 
    for cold wavelength frame.
    
    Return script for setting and execution of given BEER mode.
    
    Arguments:
    ---------
    imode: it
        BEER mode index as defined in beer.modes
    ncnt: int
        number of final counts
    lrange: list(2)
        wavelength range [A]
    exe: boolen
        if true, add simulation execution
    plot: list
        a list of strings indicating output data files: 
        variable names from BEAM1D command and suffixes to output file names.
    upstream: boolean
        If false, switch for down-stream tracing
    """
    m = BMOD.modes[imode]
    out = scriptMode(imode, ncnt=ncnt, lrange=lrange, exe=exe, plot=plot,
               upstream=upstream)
    if not m['ID']=='DS1':
        return out
    
    out += '\n#' + 70*'-'   
    out += setHeader('2nd frame', underline=True)
    
    # Lock all chopper phases
    
    out += setChopperAdj(imode, 0)
    
    # set phase of FC1A 
    out += setHeader('adjust FC1A for the middle of the frames and lock phase', 
                     underline=False)

    lam1 = m['lam0']
    Ldet = BC.sample_dist + 2000
    # one period in terms of wavelength:
    dlam = BMOD.hovm/14/Ldet*1e6
    # set wavelength for the middle of the range and lock phase
    out += 'set INST LAMBDA {:g}\n'.format(lam1+dlam)
    out += 'set FC1A ADJ 1\n'
    out += 'XML FC1A\n'
    out += 'set FC1A ADJ 0\n'

    # shift phase of FC1B and FC2B by 0.5 period
    out += setHeader('shift phase of FC1B and FC2B by 0.5 period', 
                     underline=False)
    out += 'set FC1B TIMING 0.5:1\n'
    out += 'XML FC1B\n'
    out += 'set FC2B TIMING 0.5:1\n'
    out += 'XML FC2B\n'
    
    # let frame overlap for PSC and FC2
    out += setHeader('let frame overlap for PSC and FC2', 
                     underline=False)
    cs = BMOD.chopperset(imode=imode)
    cset = []
    for c in cs:
        if not c['id'].startswith('FC1'):
            cset.append(c['id'])
    out += setOverlap(over=True, choppers=cset)
    
    # switch to the other frame
    out += setHeader('switch to the other frame', 
                     underline=False)
    lam2 = lam1+2*dlam
    lmax = lrange[1]
    dl = (lmax-lam2)*2
    lmin = lam2 - 0.5*dl  
    out += setWRange(lrange=[lmin, lmax], comment='')
    
    if exe:
        out += '\nDO MC\n'
    if plot:
        for p in plot:
            if p=='lam':
                out += scriptPlot(imode, what=p, lrange=lrange, suffix='_2')
            else:
                out += scriptPlot(imode, what=p, lrange=None, suffix='_2')
    return out

