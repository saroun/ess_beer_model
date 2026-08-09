# -*- coding: utf-8 -*-
"""
Export of McStas configuration file.
Requires template text of the *.instr file.

Created on Sat Jan 12 10:43:23 2019
@author: Jan Saroun, saroun@ujf.cas.cz
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez

update 2020-03-04::
    moved to module beer and renamed from BEER_mcstas.py
    added GE2AS guide segment to match updated beer.components
    Added arguments to parseTemplate: input/output files 
    Changed statinfo variable to fnc argument
    
update 2020-05-11:
    Updated according to the final CAD model submitted to TG3 review.
    Added W02-19 miniguide (GMINI). Update of distances and gaps measured in CAD. 
"""

import os
import numpy as np
from beer.utils import getTemplate
import beer.geometry as BG
import beer.components as BC
import beer.modes as BM
deg = np.pi/180;
indent = '   '

# %% Initialization

# global private variables
_WAV = None # waviness [deg]
_SHIELDING = False # add shielding calculator for required section

# define special types:
TJump = 'TJump'
TMonitor = 'TMonitor'

# define component types:
TArm = 'TArm'
TSlit = 'TSlit'
TCollimator = 'TCollimator'
TGuide = 'TGuide'
TGuideSeg = 'TGuideSeg'
TGuideTA = 'TGuideTA'
TGuideMC = 'TGuideMC'
TGuideEG = 'TGuideEG'
TCDisc = 'TCDisc'
TMDChopper = 'TMDChopper'
# list of component types
CTypes = [TArm, TSlit, TCollimator, TGuide, TGuideSeg, TGuideTA, TGuideMC, 
          TGuideEG, TCDisc, TMDChopper]

# initialize component lists 
listComp = {}
for c in CTypes:
    l = []
    listComp[c] = l
"""
listComp.append(listGuide = [])
listComp.append(listSlit = [])
listComp.append(listArm = [])
listComp.append(listCollimator = [])
listComp.append(listGuideTapering = [])
listComp.append(listGuideMultichannel = [])
listComp.append(listEGuideGravity = [])
listComp.append(listGuideSegmented = [])
listComp.append(listDChopper = [])
listComp.append(listMDChopper = [])
"""

beamline = []
beamMonolith = []
beamBunker = []
beamTransport = []
beamFocusing = []



nBMon = 0 # counter of monitors for statinfo 
nComp = 0 # counter of components for statinfo


# return corresponding McStas component type
def getMcStasComp(comp):
    out = ''
    sfx = ''
    if _SHIELDING:
        sfx = '_shieldinglogger'
    if (comp==TGuide):
        out = 'Guide_gravity'+sfx
    if (comp==TCollimator):
        out = 'Collimator_linear'     
    elif (comp==TGuideSeg):
        out = 'Guide_gravity'+sfx   
    elif (comp==TGuideTA):
        out = 'Guide_tapering'
    elif (comp==TGuideMC):
        out = 'Guide_multichannel'+sfx  
    elif (comp==TGuideEG):
        out = 'Elliptic_guide_gravity'+sfx  
    return out    

# %% Functions for collecting info about components


def infoSegments(key, seg=500., gap=1.0, m=None):
    """ Info about guide segments.
    
    Divides the guide into segments of required length 
    (the last segment is cut in order to match the total length).
    The segments are shortened to allow for specified gaps between the segments.
    
    Arguments:
    ---------
    key: str
        component ID
    seg: float or list
        required segment length(s), mm
    gap: float
        required gap between segments
    m: list 
        m-values for segments, for each give a list [mL, mR, mT, mB]
        Only if seg is a list, must have the same length.
    
    Returns:
    -------
    list of [dist, len, w1, h1, w2, h2, angle] for each segment
        coordinates of each element, relative preceding segment [mm,deg]
    """
    def getMList(comp, seg, m):
        mseg = []
        nr = 0
        if m and isinstance(m,list):
            nr = np.shape(m)[0]
        # m must have the same number of rows as seg.  
        # Otherwise, use m-values from comp for all segments
        if not nr==len(seg):
            mseg = len(seg)*[comp['m']]        
        # number of segments agrees: 
        else:
            msh = np.shape(m)
            # 1-D list, use the same m for all walls
            if len(msh)==1:
                # same m for all walls
                m1 = np.array([m,m,m,m]).T
                mseg = list(m1)
            # 2-D list: 
            elif len(msh)==2:
                if msh[1]==1:
                    # same m for all walls
                    m1 = np.array([m,m,m,m]).T
                    mseg = list(m1) 
                elif msh[1]==2:
                    # same m for left/right and top/bottom
                    m1 = np.array([m[:,0],m[:,0],m[:,1],m[:,1]]).T
                    mseg = list(m1) 
                elif msh[1]==4:
                    # different values for left, right, top, bottom
                    mseg = m
            # something went wrong: use m-values from comp
            if not nr==len(mseg):
                mseg = len(seg)*[comp['m']]
        return mseg
    
    comp = BC.BEER[key]
    zin = comp['start']
    zout = comp['end']
    L = zout-zin
    
    """ Guide segmentation:
        If seg is scalar: define equidistant segmentation.
        If seg is a list: use provided segmentation until the guide length.
        Adjust the last segment for required length.
    """
    if (type(seg) == float or type(seg) == int ):
        Lseg = seg
        nseg = int(np.ceil(L/Lseg))
        sg = nseg*[Lseg]
        last = L - sum(sg[:-1])
        sg[nseg-1] = last
    else:
        d = seg[0]
        sg = []
        i = 0
        n = len(seg)
        while (d < L and i < n-1):
            sg.append(seg[i])
            i += 1
            d += seg[i] 
        last = L - sum(sg)
        sg += [last]
    nseg = len(sg)
    segments = []
    d = 0.
# For each segment, get dist, len, w1, h1, w2, h2, angle, rel. preceding segment
# Units: m, deg 
    # initial dist, w, h, ctr, angle
    zin = comp['start']
    [w, h, x0] = BC.getFace(comp, zin, coord = 'ISCS') 
    z0 = 0.0
    # get entry axis angle, cos and sin
    a0 = BG.beamAngle(zin, coord = 'ISCS')
    mm = 0.001
    # get m-values for segments
    mvals = getMList(comp, sg, m)
    for i in range(nseg):
        # nominal segment length
        Lseg = sg[i]
        # get true entry and exit distances
        z1 = d + 0.5*gap
        z2 = d + Lseg - 0.5*gap
        # true segment length after cutting gaps off
        L = z2 - z1
        # get width, height and ISCS_y of the centre for entry and exit faces
        [w1, h1, x1] = BC.getFace(comp, zin+z1, coord = 'ISCS')
        [w2, h2, x2] = BC.getFace(comp, zin+z2, coord = 'ISCS')
        # get segment angle w.r.t. ISCS_y
        a1 = np.arctan2(x2-x1, L)
        # dist, len, w1, h1, w2, h2, angle, rel. preceding segment
        z = z1 - z0 
        a = a1 - a0
        ah = (x2 + 0.5*w2 - x1 - 0.5*w1)/L
        av = (0.5*h2 - 0.5*h1)/L
        s = [z*mm, L*mm, w1*mm, h1*mm, w2*mm, h2*mm, a/deg, ah/deg, av/deg]
        # add m-values for segments
        s.append(mvals[i])
        segments.append(s)
        z0 = z1
        a0 = a1
        d += Lseg
    return segments
   
    
def infoTilt(key):
    """Get shift and angle for excentric straight guides"""
    comp = BC.BEER[key]       
    [w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(comp, coord = 'ISCS')    
    length = comp['end']-comp['start']
    angle = np.arctan2(ctr2-ctr1, length)
    info = {}
    mm = 0.001
    info['shift'] = '{:.5f}'.format(ctr1*mm)
    info['angle'] = '{:.5f}'.format(angle/deg)
    info['span'] = [comp['start']*mm,comp['end']*mm]
    return info

def infoPos(key, middle=False):
    """Get shift and angle for components centered on beam axis  """
    comp = BC.BEER[key]       
    info = {}
    mm = 0.001
    angle = BG.beamAngle(comp['start'], coord = 'ISCS')
    if (middle):
        axis = BG.beamAxis(0.5*(comp['start']+comp['end']), coord = 'ISCS')
    else:
        axis = BG.beamAxis(comp['start'], coord = 'ISCS')
    info['shift'] = '{:.5f}'.format(axis[1]*mm)
    info['angle'] = '{:.5f}'.format(angle/deg)
    info['span'] = [comp['start']*mm,comp['end']*mm]
    return info

def infoMonitor(key, mtype='single', nowritefile=None):
    """Create info with properties of given component: Monitor.
    
    Parameters
    ----------
    key: str
        Component ID after which the monitor is placed
    mtype: str
        Monitor type: single (default) or spectrum
    nowritefile : str
        Add nowritefile argument if defined.
    Return
    ------
        Hash map with items for export to McStas files (e.g. parameter values 
        formatted as strings)
        
    """
    comp = BC.BEER[key]
    info = {}
    #mm = 0.001
    if comp['type'] == 'monitor':
        info['ID'] = '{}'.format(key)
    else:
        info['ID'] = 'mon{}'.format(key)
    info['desc'] = ''
    info['w'] = '{:.4f}'.format(0.1)
    info['h'] = '{:.4f}'.format(0.1)
    info['type'] = mtype
    if nowritefile is not None:
        info['nowritefile'] = '{}'.format(nowritefile)    
    mm = 0.001
    # The monitor is defined as a component
    if comp['type'] == 'monitor':
        dist = 0.5*(comp['start']+comp['end'])
    # monitor is placed after the component
    else:    
        dist = comp['end'] + 1
    angle = BG.beamAngle(dist, coord = 'ISCS')
    axis = BG.beamAxis(dist, coord = 'ISCS')
    info['dist'] = '{:.4f}'.format(dist*mm)
    info['shift'] = '{:.5f}'.format(axis[1]*mm)
    info['angle'] = '{:.5f}'.format(angle/deg)
    info['start'] = dist
    info['span'] = [dist*mm,dist*mm]
    return info

def infoJump(target, when='', desc='jump to'):
    """
    Information for a JUMP command.
    
    Arguments:
    ---------
    target: string
        component name to jump to - must be an Arm
    condition: string
        condition string to be placed after WHEN
    desc: string
        description to be placed as a code comment
    """
    info = {}
    info['ID'] = 'JUMP' # obligatory, but not used for JUMP
    info['target'] = target
    info['when'] = when
    info['desc'] = desc
    return info

def infoArm(key, dist):
    """
    Collect information on beam axis position at given distance.
    
    Arguments:
    ---------
    key: string
        component name
    dist: float
        distance, mm measured as ISCS_x coordinate
    
    Returns:
    -------
    pos: float(3)
        position in ISCS, m
    rot: float(3)
        rotation w.r.t. ISCS in deg
    """
    info = {}
    mm = 0.001
    info['ID'] = key
    info['desc'] = ''
    angle = BG.beamAngle(dist, coord = 'ISCS')
    axis = BG.beamAxis(dist, coord = 'ISCS')
    info['dist'] = '{:.4f}'.format(dist*mm)
    info['shift'] = '{:.5f}'.format(axis[1]*mm)
    info['angle'] = '{:.5f}'.format(angle/deg)
    info['start'] = dist
    info['span'] = [dist*mm,dist*mm]
    return info

def infoSlit(key):
    """
    Create info with properties of given component: Guide.
    
    Arguments:
    ----------
    
    key: str
        component ID
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
        
    """
    comp = BC.BEER[key]
    [w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(comp, coord = 'ISCS')
    info = {}
    mm = 0.001
    info['ID'] = key
    info['desc'] = comp['desc']
    info['dist'] = '{:.4f}'.format(comp['dist']*mm)
    info['w'] = '{:.4f}'.format(0.5*(w1+w2)*mm)
    info['h'] = '{:.4f}'.format(0.5*(h1+h2)*mm)
    info.update(infoPos(key, middle=True))
    return info

def infoGuide(key):
    """
    Create info with properties of given component: Guide.
    
    Arguments:
    ----------
    
    key: str
        component ID
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
        
    """
    global _WAV
    comp = BC.BEER[key]
    [w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(comp, coord = 'ISCS')
    info = {}
    mm = 0.001
    info['ID'] = key
    info['desc'] = comp['desc']
    info['dist'] = '{:.4f}'.format(comp['start']*mm)
    info['start'] = '{:.4f}'.format(comp['start']*mm)
    info['end'] = '{:.4f}'.format(comp['end']*mm)
    info['L'] = '{:.4f}'.format(((comp['end']-comp['start'])*mm))
    info['w1'] = '{:.5f}'.format(w1*mm)
    info['w2'] = '{:.5f}'.format(w2*mm)
    info['h1'] = '{:.5f}'.format(h1*mm)
    info['h2'] = '{:.5f}'.format(h2*mm)
    # note: Guide_gravity has only two m values for horizontal and vertical directions: 
    info['mL'] = '{:g}'.format(comp['m'][0])
    info['mR'] = '{:g}'.format(comp['m'][1])
    info['mT'] = '{:g}'.format(comp['m'][2])
    info['mB'] = '{:g}'.format(comp['m'][3])
    if (_WAV is not None):
        info['wav'] = '{:.5f}'.format(_WAV)
    #length = comp['end']-comp['start']
    #angle = np.arctan2(ctr2-ctr1, length)
    info.update(infoPos(key))
    return info

def infoCollimator(key):
    """
    Create info with properties of given component: Guide.
    
    Arguments:
    ----------
    
    key: str
        component ID
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
        
    """
    comp = BC.BEER[key]
    [w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(comp, coord = 'ISCS')
    info = {}
    mm = 0.001
    info['ID'] = key
    info['desc'] = comp['desc']
    info['dist'] = '{:.4f}'.format(comp['start']*mm)
    info['start'] = '{:.4f}'.format(comp['start']*mm)
    info['end'] = '{:.4f}'.format(comp['end']*mm)
    info['L'] = '{:.4f}'.format(((comp['end']-comp['start'])*mm))
    info['w1'] = '{:.5f}'.format(w1*mm)
    info['w2'] = '{:.5f}'.format(w2*mm)
    info['h1'] = '{:.5f}'.format(h1*mm)
    info['h2'] = '{:.5f}'.format(h2*mm)
    info.update(infoPos(key))
    return info 

def infoGuideSegmented(key, **kwargs):
    """
    Create info with properties of a segmented guide.
    This guide is written in a McStas instrument code as an Arm, which defines
    entry coordinates, followed by a sequence of Guide_gravity components for each segment,
    which are positioned relative to the Arm. 
    
    Arguments:
    ----------
    
    key: str
        component ID
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
        
    """
    global _WAV
    comp = BC.BEER[key]
    RH = comp['RH']*1000 # km to m
    # get basic info from Guide
    info = infoGuide(key)
    # add additional info
    info['RH'] = '{:g}'.format(RH)
    if (_WAV is not None):
        info['wav'] = '{:.5f}'.format(_WAV)
    info['segm'] = infoSegments(key, **kwargs)
    return info

def infoGuideTapering(key, nseg=1, isTilted=False, ellH='', ellV=''):
    """
    Create info with properties of given component: Guide_tapering.
    
    Arguments:
    ----------
    
    key: str
        component ID
    nseg: int
        number of segments
    isTilted: boolean
        if tilted: add shift and angle properties
    ellH: str
        name of a horizontal ellipse
    ellV: str
        name of a vertical ellipse
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
        
    """
    comp = BC.BEER[key]
    # get basic info from Guide
    info = infoGuide(key)
    if (isTilted):
        info.update(infoTilt(key))
    # add additional info
    info['mx'] = '{:g}'.format(comp['m'][0])
    info['my'] = '{:g}'.format(comp['m'][2])
    info['nseg'] = '{:g}'.format(nseg)
    if (ellH and ellV):
        raise Exception('{}: Cannot define both horizontal and vertical ellipses.'.format(key))
    if (ellH):
        info['ell'] = {'file':'prof_{}.txt'.format(key), 'ID':ellH, 'dir':0}
    if (ellV):
        info['ell'] = {'file':'prof_{}.txt'.format(key), 'ID':ellV, 'dir':1}
    return info

def infoGuideMultichannel(key):
    """
    Create info with properties of given component: Guide_multichannel.
    
    Arguments:
    ----------
    
    key: str
        component ID
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
        
    """
    comp = BC.BEER[key]
    # get basic info from Guide
    info = infoGuide(key)
    # add additional info
    info['mx'] = '{:g}'.format(comp['m'][0])
    info['my'] = '{:g}'.format(comp['m'][2])
    info['nseg'] = '{:g}'.format(comp['nlam'])
    dist = comp['dist']
    angle = comp['angle'] + BG.beamAngle(dist, coord = 'ISCS')
    axis = BG.beamAxis(dist, coord = 'ISCS')
    length = comp['end']-comp['start']
    shift = -0.5*length*np.tan(angle*deg) + axis[1]
    info['angle'] = '{:.5f}'.format(angle)
    info['shift'] = '{:.5f}'.format(shift*0.001)
    info['dlam'] = '{:.7f}'.format(comp['dlam']*0.001)
    return info


def infoEGuideGravity(key, ell='', fdir=0):
    """
    Create info with properties of given component: Elliptic_guide_gravity.
    
    Arguments:
    ----------
    
    key: str
        component ID
    ell: str
        name of a horizontal ellipse
    fdir: int
        focusing direction if ell is defined: (0) horizontal, (1) vertical
    nseg: int
        requested number of segments
    gapseg: float
        requested gap between segments, mm
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
        
    """
    comp = BC.BEER[key]
    RH = comp['RH']*1000 # km to m
    # get basic info from Guide
    info = infoGuide(key)
    # add additional info
    info['RH'] = '{:g}'.format(RH)
    # no focusing by default
    info['linh'] = '{:g}'.format(1e5)
    info['linw'] = '{:g}'.format(1e5)
    info['louth'] = '{:g}'.format(1e5)
    info['loutw'] = '{:g}'.format(1e5)
    if (ell):
        info['ell'] = {'ID':ell, 'dir':fdir}
    return info

#def infoDChopper(key, win=144, nwin=1):
def infoDChopper(key):    
    """
    Create info with properties of given component: DiscChopper.
    
    Arguments:
    ----------
    
    key: str
        component ID
    win: float
        window width [deg]
    nwin: int
        number of windows
    flip: float
        for flip<>0, the chopper is rotated by flip*180 deg around y axis
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
    """
    comp = BC.BEER[key]
    win = comp['win'][0]
    nwin = len(comp['win'])
    info = {}
    info['ID'] = key
    info['desc'] = comp['desc']
    info['dist'] = '{:.4f}'.format(comp['dist']*0.001)
    info['win'] = '{:.4f}'.format(win)
    info['ns'] = '{:g}'.format(nwin)
    info.update(infoPos(key, middle=True))
    return info


#def infoMDChopper(key, wins, ctrs, nwin=1):
def infoMDChopper(key):
    """
    Create info with properties of given component: DiscChopper.
    
    Arguments:
    ----------
    
    key: str
        component ID
    wins: float array
        window widths [deg],
    ctrs: float array
        window centeres [deg], 
    nwin: int
        number of windows
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
    """
    comp = BC.BEER[key]
    wins = comp['win']
    ctrs = comp['wctr']
    nwin = len(comp['win'])
    info = {}
    info['ID'] = key
    info['desc'] = comp['desc']
    info['dist'] = '{:.4f}'.format(comp['dist']*0.001)
    fmt = (nwin-1)*'{:g};'+'{:g}'
    info['wins'] = fmt.format(* wins)
    info['ctrs'] = fmt.format(* ctrs)
    info['ns'] = '{:g}'.format(nwin)
    info.update(infoPos(key, middle=True))    
    return info


#%% Functions for adding components to beamline

def addJump(beam, target, when='', desc=''):
    """
    Add a JUMP command to TRACE section.
    
    Arguments:
    ---------
    beam: 
        beam list to be added to
    target: str
        name of the target component.
    when: str
        contition expression
    desc: str
        description to be used in code comment\
        
    NOTE: by McStas rules, JUMP can only navigate between Arm components.
    """
    item = {'info': infoJump(target, when=when, desc=desc), 'type':TJump}
    beam.append(item)
    beamline.append(item)
    
def addMonitor(beam, key, **kwargs):
    """
    Add monitor.
    
    Arguments:
    ----------
    beam: 
        beam list to be added to
    key: string
        The name of the component after which the montor is placed.    
        The monitor ID gets a prefix 'mon', so that its name becomes monkey :-)
    mtype: str
        Monitor type. Recognized types are 'single' or 'spectrum'
    """
    global nBMon,nComp
    item = {'info': infoMonitor(key, **kwargs), 'type':TMonitor}
    d = [item['info']['span'][1]]
    stat = {'icomp': nComp, 'dist': d, 'nmon':nBMon, 'nseg': 1}
    item['statinfo'] = stat
    nBMon += 1
    nComp += 1
    beam.append(item)
    item['idx'] = nComp
    beamline.append(item)   
    

def addComponent(typ, beam, key, **kwargs):
    """
    Call this function to add a component on beamline.
    It dispatches calls to individual components add functions and collects
    necessary information.
    """
    global nBMon, nComp, listComp
        
    def addToList(item):
        """
        Add a component to the global list listComp.
        """
        global listComp
        if item['type'] in listComp:
            listComp[item['type']].append(item)
     
    def dataArm(beam, key, dist=0.0):
        item = {'info': infoArm(key, dist), 'type':TArm}
        return item
        
    def dataSlit(beam, key):
        item = {'info': infoSlit(key), 'type':TSlit}
        return item
    
    def dataGuide(beam, key, **kwargs):
        item = {'info': infoGuide(key, **kwargs), 'type':TGuide}
        return item
    
    def dataCollimator(beam, key, **kwargs):
        item = {'info': infoCollimator(key, **kwargs), 'type':TCollimator}
        return item
    
    def dataGuideTapering(beam, key, **kwargs):
        item = {'info': infoGuideTapering(key, **kwargs), 'type':TGuideTA}
        return item
    
    def dataGuideMultichannel(beam, key, **kwargs):
        item = {'info': infoGuideMultichannel(key, **kwargs), 'type':TGuideMC}
        return item
    
    def dataEGuideGravity(beam, key, when='', **kwargs):
        item = {'info': infoEGuideGravity(key, **kwargs), 'type':TGuideEG}
        if (when):
            item['info']['when'] = when 
        return item
        
    def dataDChopper(beam, key, **kwargs):
        item = {'info': infoDChopper(key, **kwargs), 'type':TCDisc}
        return item
        
    def dataMDChopper(beam, key, **kwargs):
        item = {'info': infoMDChopper(key, **kwargs), 'type':TMDChopper}
        return item  
    
    def dataMonitor(beam, key, **kwargs):
        item = {'info': infoMonitor(key, **kwargs), 'type':TMonitor}
        return item 
    
    item = None
    if (typ==TSlit):
        item = dataSlit(beam, key)
    elif (typ==TArm):
        item = dataArm(beam, key, **kwargs)
    elif (typ==TCollimator):
        item = dataCollimator(beam, key, **kwargs)        
    elif (typ==TGuide):
        item = dataGuide(beam, key, **kwargs)
    elif (typ==TGuideTA):
        item = dataGuideTapering(beam, key, **kwargs)
    elif (typ==TGuideMC):
        item = dataGuideMultichannel(beam, key, **kwargs)
    elif (typ==TGuideEG):
        item = dataEGuideGravity(beam, key, **kwargs)
    elif (typ==TCDisc):
        item = dataDChopper(beam, key, **kwargs)
    elif (typ==TMDChopper):
        item = dataMDChopper(beam, key, **kwargs)
    elif (typ==TGuideSeg):
        # for segmented guide, add an inital arm automatically
        # guide segments start relative to it 
        comp = BC.BEER[key]
        dist = comp['dist']
        ID = 'Arm'+key
        a = dataArm(beam, ID, dist=dist)
        d = [a['info']['span'][1]]
        stat = {'icomp': nComp, 'dist': d, 'nmon':nBMon, 'nseg': 1}
        a['statinfo'] = stat
        addToList(a)
        nBMon += 1
        nComp += 1
        beam.append(a)
        a['idx'] = nComp
        beamline.append(a)
        item = {'info': infoGuideSegmented(key, **kwargs), 'type':TGuideSeg, 'relto':ID}
    elif (typ==TMonitor):
        item = dataMonitor(beam, key, **kwargs)
    if (item is None):
        raise Exception('cannot add unknown component type: {}\n'.format(typ))
    else:
        addToList(item)
    
    # define statinfo: data for counting statistics
    if (typ==TGuideSeg):
        sgm = item['info']['segm']
        nseg = len(sgm)
        d = nseg*[0.0]
        z = item['info']['span'][0]
        for i in range(nseg):
            z += sgm[i][0] 
            d[i] = z + sgm[i][1]

    else:
        d = [item['info']['span'][1]]
        nseg = 1
    stat = {'icomp': nComp, 'dist': d, 'nmon':nBMon, 'nseg': nseg}
    item['statinfo'] = stat
    nBMon += nseg
    nComp += 1
    beam.append(item)
    item['idx'] = nComp
    beamline.append(item)


#%% Code generators for the INITIALIZE part 

def cfgComponent(comp, indent='    '):
    """
    In the INITIALIZE section, writes code for setting component parameters.
    """
    def cfgSlit(info, indent):
        ID = info['ID']
        out = ''
        # define guide parameters
        fmt = indent+'{}.{}={};\n'
        varkeys = ['dist','w', 'h', 'shift', 'angle']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])
        return out
    
    def cfgArm(info, indent):
        ID = info['ID']
        out = ''
        # define guide parameters
        fmt = indent+'{}.{}={};\n'
        varkeys = ['dist', 'shift', 'angle']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])
        return out
    
    def cfgGuideBasic(info, indent):
        ID = info['ID']
        out = ''
        # define guide parameters
        fmt = indent+'{}.{}={};\n'
        varkeys = ['dist','L', 'w1', 'w2', 'h1', 'h2', 'shift', 'angle']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format( ID, p, info[p])
        return out
    
    def cfgGuide(info, indent):
        ID = info['ID']
        out = cfgGuideBasic(info, indent)
        # define guide parameters
        fmt = indent+'{}.{}={};\n'
        varkeys = ['mL', 'mR', 'mT', 'mB', 'wav']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])
        return out 
    
    def cfgGuideSegmented(info, indent):
        ID = info['ID']
        out = cfgGuideBasic(info, indent)
        # define guide parameters
        fmt = indent+'{}.{}={};\n'
        varkeys = ['mL', 'mR', 'mT', 'mB', 'RH', 'wav']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])
        return out 
    
    def cfgGuideTapering(info, indent):
        ID = info['ID']
        # get basics from Guide
        out = cfgGuideBasic(info, indent)
        # define additional parameters
        fmt = indent+'{}.{}={};\n'
        varkeys = ['mx', 'my', 'nseg']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])
        # define elliptic profile
        if ('ell' in info.keys()):
            ell = info['ell']
            out += indent+'MPI_MASTER(\n'
            fmt = '{}writeTaperingFile("{}", {}, {:d}, {}, &{});\n'
            out += fmt.format(indent, ell['file'], ell['ID'], ell['dir'], info['start'], ID)
            out += indent+');\n'
            fmt = r'{}if (verbose) printf("%s: shift=%g [mm], angle = %g [deg]\n","{}",{}.shift*1000,{}.angle);'
            out += fmt.format(indent, ID, ID, ID) +'\n'
        return out
    
    def cfgGuideMultichannel(info, indent):
        ID = info['ID']
        # get basics from Guide
        out = cfgGuideBasic(info, indent)
        # define additional parameters
        fmt = indent+'{}.{}={};\n'
        varkeys = ['mx', 'my', 'nseg', 'dlam']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])
        return out
    
    def cfgEGuideGravity(info, indent):
        ID = info['ID']
        # default chopper data 
        fmt = '{}setEGuideDefault(&{});\n'
        out = fmt.format(indent, ID)
        # get basics from Guide
        out += cfgGuideBasic(info, indent)
        # define additional parameters
        fmt = indent+'{}.{}={};\n'
        varkeys = ['mL', 'mR', 'mT', 'mB', 'RH']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format( ID, p, info[p])
        # define ellipse
        if ('ell' in info.keys()):
            ell = info['ell']
            fmt = indent+'defEllipse({}, {:d}, {}, {}, &{});\n'
            out += fmt.format( ell['ID'], ell['dir'], info['start'], info['end'], ID)
        else:
            fmt = indent+'defEllipse(NULL, 0, {}, {}, &{});\n'
            out += fmt.format( info['start'], info['end'], ID)
        return out
    
    def cfgDChopper(info, indent):
        ID = info['ID']
        # default chopper data 
        fmt = '{}setCDiscDefault(&{});\n'
        out = fmt.format(indent, ID)
        # define additional parameters
        fmt = indent+'{}.{}={};\n'
        # out += indent+'strcpy({}.id, "{}");\n'.format(ID, ID)
        varkeys = ['dist', 'win', 'ns', 'shift', 'angle']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])
        return out
    
    def cfgMDChopper(info, indent):
        ID = info['ID']
        # default chopper data 
        fmt = '{}setMDChopperDefault(&{});\n'
        out = fmt.format(indent, ID)
        # define additional parameters
        fmt = indent+'{}.{}={};\n'
        # out += indent+'strcpy({}.id, "{}");\n'.format(ID, ID)
        varkeys = ['dist', 'ns']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])
        varkeys = ['wins', 'ctrs']
        fmt = indent+'strcpy({}.{},"{}");\n'
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])
        fmt = indent+'{}.{}={};\n'        
        varkeys = ['shift', 'angle']
        for p in varkeys:
            if (p in info.keys()):
                out += fmt.format(ID, p, info[p])        
        return out
    
    
    
    
    typ = comp['type']
    info = comp['info']
    out = ''
    if (typ==TSlit):
        out += cfgSlit(info, indent)
    elif (typ==TArm):
        out += cfgArm(info, indent)
    elif (typ==TGuide):
        out += cfgGuide(info, indent)
    elif (typ==TCollimator):
        out += cfgGuideBasic(info, indent)
    elif (typ==TGuideSeg):
        out += cfgGuideSegmented(info, indent)
    elif (typ==TGuideTA):
        out += cfgGuideTapering(info, indent)
    elif (typ==TGuideMC):
        out += cfgGuideMultichannel(info, indent)
    elif (typ==TGuideEG):
        out += cfgEGuideGravity(info, indent)
    elif (typ==TCDisc):
        out += cfgDChopper(info, indent)
    elif (typ==TMDChopper):
        out += cfgMDChopper(info, indent)        
    return out



#%% Code generators for the TRACE part 

def extStatistics(stat, iseg=0):
    icomp = stat['icomp']
    nseg = stat['nseg']
    nmon = stat['nmon']
    out = 'EXTEND\n%{\n'
    out += '{}beam_sum[{:d}] += p;\n'.format(indent,nmon+iseg)
    if (nseg==1 or iseg==nseg-1):
        out += '{}stats[{:d}].sum += p;\n'.format(indent,icomp)
        out += '{}if (p>0) stats[{:d}].cnt++;\n'.format(indent,icomp)
    out += '%}\n'
    return out

def compPosition(ID,relto='ISCS'):
    fmt = 'AT ({}.shift, 0, {}.dist) RELATIVE {}\n'
    out = fmt.format(ID, ID, relto)
    fmt = 'ROTATED (0, {}.angle, 0) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    return out

def compPositionDispl(ID,relto='ISCS'):
    fmt = 'AT ({}.shift + misfit_h*randnorm(), misfit_v*randnorm(), {}.dist) RELATIVE {}\n'
    out = fmt.format(ID, ID, relto)
    fmt = 'ROTATED (0, {}.angle, 0) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    return out

def compMonitor(info, relto='ISCS'):
    """
     Place simple monitor after given component
    """
    tab = '\t'
    ID = info['ID']
    fmt = 'COMPONENT @C = '
    if (info['type']=='spectrum'):
        fmt += 'L_monitor(filename="@C.dat", nL=100, Lmin=0.2, Lmax=10.2,\n'
    else:
        fmt += 'Monitor('
    fmt += 'xwidth={}, yheight={}, restore_neutron=1'
    if 'nowritefile' in info:
        fmt += ', nowritefile={})\n'.format(info['nowritefile'])
    else:
        fmt += ')\n'
    out = fmt.replace('@C',ID).format(info['w'],info['h'])
    fmt = 'AT ({}, 0, {}) RELATIVE {}\n'
    out += fmt.format(info['shift'], info['dist'], relto)
    fmt = 'ROTATED (0, {}, 0) RELATIVE {}\n'
    out += fmt.format(info['angle'], relto)
    return out

def compArm(info, relto='ISCS'):
    ID = info['ID']
    fmt = 'COMPONENT @C = Arm()\n'
    out = fmt.replace('@C',ID)
    out += compPosition(ID,relto=relto)
    return out

def compJump(info):
    if ('when' in info):
        out = 'JUMP {} WHEN ({})\n'.format(info['target'], info['when'])
    else:
        out = 'JUMP {}\n'.format(info['target'])   
    return out

def compSlit(info, relto='ISCS'):
    ID = info['ID']
    fmt = 'COMPONENT c@C = Slit(xwidth = @C.w, yheight = @C.h)\n'
    out = fmt.replace('@C',ID)
    out += compPosition(ID,relto=relto)
    return out

def compCollimator(info, relto='ISCS'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c{} = {}(\n'.format(ID,getMcStasComp(TCollimator))
    fmt = 'length = @C.L, xwidth = @C.w1, yheight = @C.h1\n'
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    out += compPosition(ID,relto=relto)
    return out
      
def compGuide(info, relto='ISCS'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c{} = {}(\n'.format(ID,getMcStasComp(TGuide))
    fmt = 'l = @C.L, w1 = @C.w1, h1 = @C.h1, w2 = @C.w2, h2 = @C.h2,\n'
    out += tab+fmt.replace('@C',ID)
    if ('wav' in info.keys()):
        fmt = 'R0 = R_0, alpha = m_alpha, Qc = m_Qc, W = m_W, wavy = @C.wav,\n'
    else:
        fmt = 'R0 = R_0, alpha = m_alpha, Qc = m_Qc, W = m_W,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'mleft = @C.mL, mright = @C.mR, mtop = @C.mT, mbottom = @C.mB\n'.replace('@C',ID)
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    out += compPositionDispl(ID,relto=relto)
    return out

        
def compDChopper(info, relto='ISCS'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c@C = DiskChopper(\n'.replace('@C',ID)
    fmt = 'theta_0 = @C.win, radius = @C.R, yheight = @C.h, nu = @C.nu,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'nslit = @C.ns, delay = @C.delay\n'
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    fmt = 'AT ({}.shift, 0, {}.dist) RELATIVE {}\n'
    out += fmt.format(ID, ID, relto)
    fmt = 'ROTATED (0, {}.angle + {}.flip*180, 0) RELATIVE {}\n'
    out += fmt.format(ID, ID, relto)
    
    return out

def compMDChopper(info, relto='ISCS'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c@C = MultiDiskChopper(\n'.replace('@C',ID)
    fmt = 'radius = @C.R, delta_y = 0.5*@C.h - @C.R, nu = -@C.nu,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'nslits = @C.ns, delay = @C.delay, abs_out=0,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'slit_width = @C.wins, slit_center = @C.ctrs\n'
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    out += compPosition(ID,relto=relto)
    return out
    
def compGuideTapering(info, relto='ISCS'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c{} = {}(\n'.format(ID,getMcStasComp(TGuideTA))
    # shape given in file
    if ('ell') in info:
        fname = info['ell']['file']
        fmt = tab+'option = "file={}",\n'
        out += fmt.format(fname)
        fmt = tab+'l = @C.L, w1=0, h1=0, linw=0, loutw=0, linh=0, louth=0,\n'
        out += fmt.replace('@C',ID)
    # shape given by parameters
    else:
        fmt = tab+'l = @C.L, w1 = @C.w1, h1 = @C.h1, linw = @C.linw, loutw = @C.loutw, linh = @C.linh, louth = @C.louth,\n'
        out += fmt.replace('@C',ID)
    fmt = tab+'R0 = R_0, alphax = m_alpha, alphay = m_alpha, Qcx = m_Qc, Qcy = m_Qc, W = m_W,\n'
    out += fmt.replace('@C',ID)
    fmt = tab+'mx = @C.mx, my = @C.my, segno = @C.nseg\n'
    out += fmt.replace('@C',ID)    
    out += ')\n'
    out += compPosition(ID,relto=relto)
    return out
  
def compGuideMultichannel(info, relto='ISCS'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c@C = Guide_multichannel(\n'.replace('@C',ID)
    fmt = 'l = @C.L,w1 = @C.w1, h1 = @C.h1, w2 = @C.w2, h2 = @C.h2, \n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'R0 = R_0, alphax = m_alpha, alphay = m_alpha, Qcx = m_Qc, Qcy = m_Qc, W = m_W, dlam = @C.dlam,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'mx = @C.mx, my = @C.my, nslit = @C.nseg+1, mater = "Si"\n'
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    out += compPosition(ID,relto=relto)
    return out

def compEGuideGravity(info, relto='ISCS'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c{} = {}(\n'.format(ID,getMcStasComp(TGuideEG))
    fmt = 'l = @C.L, xwidth = @C.w1, yheight = @C.h1,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'majorAxisxw=@C.ah, minorAxisxw=@C.bh, majorAxisyh=@C.av, minorAxisyh=@C.bv,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'majorAxisoffsetxw=@C.ctr, majorAxisoffsetyh=@C.ctr,\n'
    out += tab+fmt.replace('@C',ID)
    # fmt = 'linxw = @C.linw, loutxw = @C.loutw, linyh = @C.linh, loutyh = @C.louth, curvature = @C.RH,\n'
    #out += tab+fmt.replace('@C',ID)
    fmt = 'mleft = @C.mL, mright = @C.mR, mtop = @C.mT,  mbottom = @C.mB,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'R0 = R_0, Qc = m_Qc, alpha = m_alpha, W = m_W\n'
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    if ('when' in info.keys()):
        out += 'WHEN ({} = 1) '.format(info['when'])
    out += compPosition(ID,relto=relto)
    return out


def compGuideSegment(info, iseg, seginfo):
    ID = info['ID']
    IDseg = '{}_{}'.format(ID,iseg)
    [dist, L, w1, h1, w2, h2, angle, ah, av, m4]  = seginfo[iseg] # rel. preceding segment [m, deg]
    tab = '\t'
    out = 'COMPONENT c{} = {}(\n'.format(IDseg,getMcStasComp(TGuide))
    fmt = 'l = {:.5g}, w1 = {:.5g}, h1 = {:.5g}, w2 = {:.5g}, h2 = {:.5g},\n'
    out += tab+fmt.format(L, w1, h1, w2, h2 )
    if ('wav' in info.keys()):
        fmt = 'R0 = R_0, alpha = m_alpha, Qc = m_Qc, W = m_W, wavy = @C.wav,\n'
    else:
        fmt = 'R0 = R_0, alpha = m_alpha, Qc = m_Qc, W = m_W,\n'
    out += tab+fmt.replace('@C',ID)
    
    #fmt = 'mleft = @C.mL, mright = @C.mR, mtop = @C.mT, mbottom = @C.mB\n'
    #out += tab+fmt.replace('@C',ID)
    # use seginfo
    fmt = 'mleft = {}, mright = {}, mtop = {}, mbottom = {}\n'
    out += tab+fmt.format(*m4)
    out += ')\n'
    #fmt = 'AT (0, 0, {:.5g}) RELATIVE PREVIOUS\n'
    #out += fmt.format(dist)
    fmt = 'AT (misfit_h*randnorm(), misfit_v*randnorm(), {:.5g}) RELATIVE PREVIOUS\n'
    out += fmt.format(dist)
    
# TODO add misalignment variable    
    fmt = 'ROTATED (0, {:.5g}, 0) RELATIVE PREVIOUS\n'
    out += fmt.format(angle)
    return out

def compGuideSegmented(info, stat, relto='ISCS', statinfo = False):
    if ('segm') not in info.keys():
        out = compEGuideGravity(info, relto=relto)
        return out
    segm = info['segm']
    nseg = len(segm)
    out = '\n'
    for i in range(nseg):
        out += compGuideSegment(info, i, segm)
        if statinfo:
            out += extStatistics(stat, iseg=i) 
    return out



def traceComponent(comp, statinfo, relto='ISCS'):
    typ = comp['type']
    info = comp['info']
    out = ''
    if (typ==TSlit):
        out += compSlit(info, relto=relto)
    elif (typ==TArm):
        out += compArm(info, relto=relto)
    elif (typ==TJump):
        out += compJump(info)        
    elif (typ==TMonitor):
        out += compMonitor(info, relto=relto)    
    elif (typ==TGuide):
        out += compGuide(info, relto=relto)
    elif (typ==TCollimator):
        out += compCollimator(info, relto=relto)        
    elif (typ==TGuideSeg):
        out += compGuideSegmented(info, comp['statinfo'], relto=relto, statinfo=statinfo)
    elif (typ==TGuideTA):
        out += compGuideTapering(info, relto=relto)
    elif (typ==TGuideMC):
        out += compGuideMultichannel(info, relto=relto)
    elif (typ==TGuideEG):
        out += compEGuideGravity(info, relto=relto)
    elif (typ==TCDisc):
        out += compDChopper(info, relto=relto)
    elif (typ==TMDChopper):
        out += compMDChopper(info, relto=relto) 
    
    # NOTE: compGuideSegmented implements its own statistics trace extension 
    if statinfo and (typ != TGuideSeg) and ('statinfo' in comp): 
            out += extStatistics(comp['statinfo']) 
    return out


# %% Define BEER instrument components
    
def defineInstrument(guide_monitors=False):
    global nBMon,nComp
    global beamMonolith, beamBunker, beamTransport, beamFocusing, beamline
    global listComp
    global _SHIELDING
    nBMon = 0
    nComp = 0
    beamline.clear()
    beamMonolith.clear()
    beamBunker.clear()
    beamTransport.clear()
    beamFocusing.clear()
    for c in listComp:
        listComp[c].clear()


    # Add Monolith section    
    addComponent(TGuideTA, beamMonolith,'NBOA', nseg=7, isTilted=True, ellV='ellV1')
    addMonitor(beamMonolith,'NBOA', mtype='spectrum', nowritefile='!monoutputs')
    addComponent(TGuideTA, beamMonolith,'BBG', nseg=1, isTilted=True, ellV='ellV1')
    
    if guide_monitors:
        addMonitor(beamMonolith,'BBG')
    
    # Add Bunker section
    addComponent(TGuideMC, beamBunker,'GSW')
    addComponent(TMonitor, beamBunker,'BM1', mtype='spectrum')
    #addMonitor(beamBunker,'GSW')
    addComponent(TGuide, beamBunker,'GCA1')
    addComponent(TCDisc, beamBunker, 'PSC1')
    addComponent(TGuide, beamBunker,'GCA2')
    #addComponent(TGuide, beamBunker,'GCA3')
    addComponent(TCDisc, beamBunker, 'PSC2')
    #addComponent(TGuide, beamBunker,'GCA4')
    addComponent(TGuide, beamBunker,'GCB') 
    addComponent(TCDisc, beamBunker, 'PSC3')         
    addComponent(TGuide, beamBunker,'GCC')
    addComponent(TCDisc, beamBunker, 'FC1A')      
    addComponent(TCDisc, beamBunker, 'FC1B') 
    addComponent(TGuide, beamBunker,'GCE')
    if guide_monitors:
        addMonitor(beamBunker,'GCE')
    addComponent(TCDisc, beamBunker, 'MCA')      
    addComponent(TCDisc, beamBunker, 'MCB')    
    addComponent(TGuide, beamBunker,'GCF')
    if guide_monitors:
        addMonitor(beamBunker,'GCF')
    addComponent(TMDChopper, beamBunker, 'MCC')
    addComponent(TGuide, beamBunker,'GCG')
    if guide_monitors:
        addMonitor(beamBunker,'GCG')   
    #addComponent(TGuideSeg, beamBunker, 'GE1', seg=500, gap=1)
    addComponent(TGuideSeg, beamBunker, 'GE1A', seg=500, gap=1)
    addComponent(TMonitor, beamBunker,'BM2', mtype='spectrum')
    addComponent(TGuideSeg, beamBunker, 'GE1B', seg=500, gap=1)
    addComponent(TGuideSeg, beamBunker, 'GN1', seg=500, gap=1)
    addComponent(TGuideSeg, beamBunker, 'GN2', seg=500, gap=1)
    addMonitor(beamBunker,'GN2', mtype='spectrum', nowritefile='!monoutputs')
    
    
    # Add Transport section
    # add axis at the shielding section start
    if _SHIELDING:
        addComponent(TArm, beamTransport, 'Arm1', dist=BC.BEER['GSH2']['start']-0.0001)

    addComponent(TGuide, beamTransport,'GSH2')
    if guide_monitors:
        addMonitor(beamTransport,'GSH2')
    addComponent(TGuide, beamTransport,'GE2AS')
    
    #addEGuideGravity(beamTransport, 'GE2A', ell='ellH1', fdir=0)
    #addEGuideGravity(beamTransport, 'GE2B', ell='ellH1', fdir=0)
    addComponent(TGuideSeg, beamTransport, 'GE2A', seg=500, gap=1)
    addComponent(TGuideSeg, beamTransport, 'GE2B', seg=1000, gap=1)
    if guide_monitors:
        addMonitor(beamTransport,'GE2B')
    #addEGuideGravity(beamTransport, 'GT1')
    addComponent(TGuideSeg, beamTransport, 'GT1', seg=2000, gap=1)
    addMonitor(beamTransport,'GT1', mtype='spectrum', nowritefile='!monoutputs')
    # addComponent(TCDisc, beamTransport, 'FC2A', win=180, nwin=1)      
    # addComponent(TCDisc, beamTransport, 'FC2B', win=90, nwin=1) 
    addComponent(TCDisc, beamTransport, 'FC2A')      
    addComponent(TCDisc, beamTransport, 'FC2B')     
    #addEGuideGravity(beamTransport, 'GT2')
    addComponent(TGuideSeg, beamTransport, 'GT2', seg=2000, gap=1)
    if guide_monitors:
        addMonitor(beamTransport,'GT2')
    
    # Add Focusing section
    #addEGuideGravity(beamFocusing, 'GF1', ell='ellV2', fdir=1)
    addComponent(TGuideSeg, beamFocusing, 'GF1', seg=1000, gap=1)
    if guide_monitors:
        addMonitor(beamFocusing,'GF1')
    addComponent(TSlit, beamFocusing, 'SL1')
    #addEGuideGravity(beamFocusing, 'GF2', ell='ellV2', fdir=1)

    # special setting for FC2: set the last ~0.5m segment blind on left/right
    seg = 6*[500.]
    m = BC.BEER['GF2']['m']
    mseg = 6*[m]
    mseg[5] = [0.0, 0.0, m[2], m[3]]
    addComponent(TGuideSeg, beamFocusing, 'GF2', seg=seg, m = mseg, gap=1)
    if guide_monitors:
        addMonitor(beamFocusing,'GF2')
    addComponent(TSlit, beamFocusing, 'SL2')
    
    addComponent(TGuide, beamFocusing,'GMINI')
    if guide_monitors:
        addMonitor(beamFocusing,'GMINI')

    #addComponent(TGuideSeg, beamFocusing, 'GEX1', seg=150, gap=1)
    
    # Start of the guide exchanger
    addComponent(TArm, beamFocusing, 'ArmGEXstart', dist=BC.BEER['GEX1']['start'])
    
    # Jump to GEX1 (ArmGEX1 is created automatically for TGuideSeg)
    addJump(beamFocusing, 'ArmGEX1', when='GF3On==1', desc='Jump to GEX1')
    
    # Add GEX2 - flight tube
    addComponent(TCollimator, beamFocusing,'GEX2')
    
    # Add Arm at the end of the collimator to allow the following JUMP
    addComponent(TArm, beamFocusing, 'ArmGEX2', dist=BC.BEER['GEX1']['end'])
    
    # Jump to the end of exchanger 
    addJump(beamFocusing, 'ArmGEXend', when='GF3On==0', desc='Jump to the end of exchanger')
        
    addComponent(TGuideSeg, beamFocusing, 'GEX1', seg=[367, 250, 250, 250, 250, 200, 200, 100], gap=1)
    
    # Add Arm at the end of the exchanger
    addComponent(TArm, beamFocusing, 'ArmGEXend', dist=BC.BEER['GEX1']['end'])
    
    # monitor at the end of exchanger
    if guide_monitors:
        addMonitor(beamFocusing,'GEX1')
    
    # input slit
    addComponent(TSlit, beamFocusing, 'SL3')
    
    # Arm at the sample axis. Name it Sample_axis, other components may rely on it
    addComponent(TArm, beamFocusing, 'Sample_axis', dist=BC.sample_dist)
    
    # add axis at the shielding section end
    if (_SHIELDING):
        addComponent(TArm, beamFocusing, 'Arm2',  dist=BC.sample_dist+0.0001)    

# %% INITIALIZE section: setting of component parametes 


def cfgBeam(beamsection, comment, statinfo):
    """Adds a component in the INITIALIZE section """
    
    # ignored items:
    skipitem = [TJump]    
    out = '\n/*'+50*'-'+'\n'
    out += '{}\n'.format(comment)
    out += 50*'-'+'*/\n'
    for comp in beamsection:
        typ = comp['type']
        if not typ in skipitem:
            if (typ == TMonitor):
                info = comp['info']
                i = comp['idx']
                ID = info['ID']
                out += '\n'
                out += '/* Monitor: {} */\n'.format(ID)
                out += indent + 'addComponent("{}", {:d});\n'.format(ID, i)
            else:
                info = comp['info']
                out += '\n'
                out += '/* {}: {}*/\n'.format(info['ID'], info['desc'])
                out += cfgComponent(comp, indent)
                i = comp['idx']
                ID = info['ID']
                out += indent + '{}.idx = {:d};\n'.format(ID, i)
                out += indent + 'addComponent("{}", {:d});\n'.format(ID, i)
            if statinfo and 'statinfo' in comp:
                out += '\n'
                fmt = 'addBeamSegment({:g});\n'
                stat = comp['statinfo']
                d = stat['dist']
                # print('cfgBeam: {}, {}\n'.format(info['ID'],d))
                for j in range(len(d)):
                    out += fmt.format(d[j])
                out += '\n'
    return out

def reportBeam(beam, comment, indent):
    """Adds a component in the reporting section of INITIALIZE """
    # ignored items:
    skipitem = [TJump, TMonitor] 
    fmt = '\n'+indent+'/* {}*/\n'
    out = fmt.format(comment)
    fmt = indent+'report{}("{}", {});\n'
    for comp in beam:
        typ = comp['type']
        if not typ in skipitem:
            ID = comp['info']['ID']
            out += fmt.format(comp['type'],ID,ID)
    out +='\n'
    return out


def declaretype(listC):
    """Declares variables from the list  """
    out = ''
    n = len(listC)
    if (n>0):
        typ = listC[0]['type']
        out += '{}{}  '.format(indent,typ)
        for i in range(n):
            ID = listC[i]['info']['ID']
            out += ID
            if i<n-1: out+=','
    out += ';\n'
    return out        

        
def traceBeam(beam, comment, statinfo):
    """ Writes TRACE code for given beam section """
    out = '\n/*'+50*'-'+'\n'
    out += '{}\n'.format(comment)
    out += 50*'-'+'*/\n'
    for comp in beam:
        # print(comp['info']['ID'])
        info =  comp['info'] 
        out += '\n'
        out += '/* {}: {}*/\n'.format(info['ID'], info['desc'])
        out += traceComponent(comp, statinfo, relto='ISCS')
    return out

   
# %% Parsing function, generates strings for @VAR replacements

def ellipses(indent):
    mm = 0.001
    fmt = indent+'double {}[] = @1{:.4f}, {:.3f}, {:.3f}@2;  // {}\n'
    e = BG.E1
    out = fmt.format('ellV1',e['b']*mm, e['a']*mm, e['c']*mm, 'vertical expansion')
    e = BG.E2
    out += fmt.format('ellH1',e['b']*mm, e['a']*mm, e['c']*mm, 'horizontal expansion')
    e = BG.E3
    out += fmt.format('ellV2',e['b']*mm ,e['a']*mm , e['c']*mm, 'vertical focusing (defined from the sample)')
    out = out.replace('@1','{')
    out = out.replace('@2','}')
    return out

def initPrimary(statinfo):
    out = cfgBeam(beamMonolith, 'Monolith section', statinfo)
    out += cfgBeam(beamBunker, 'Bunker section', statinfo)
    out += cfgBeam(beamTransport, 'Transport section', statinfo)
    out += cfgBeam(beamFocusing, 'Focusing section', statinfo)

    return out

def cmodesFrq(indent):
    out = '\n// Define frequencies for resolution choppers \n'
    nx = len(BM.cmodes)
    ny = len(BM.cmodes[0])-1
    out += indent+'double cmode_f[{:d}][{:d}] = '.format(nx,ny)+'{\n'
    for i in range(nx):
        out += indent+'{'+BM.getCModesFrq(i)+ '}' 
        if (i==nx-1):
            out += '\n'
        else:
            out += ',\n'
    out += indent+'};\n'
    return out

def wmodesFrq(indent):
    out = '\n// Define frequencies for wavelength definition  choppers \n'
    nx = len(BM.wmodes)
    ny = len(BM.wmodes[0])-1
    out += indent+'double wmode_f[{:d}][{:d}] = '.format(nx,ny)+'{\n'
    for i in range(nx):
        out += indent+'{'+BM.getWModesFrq(i)+ '}' 
        if (i==nx-1):
            out += '\n'
        else:
            out += ',\n' 
    out += indent+'};\n'
    return out

def cmodesPhi(indent):
    out = '\n// Define phase shifts for resolution choppers \n'
    nx = len(BM.cmodes)
    ny = len(BM.cphases[0])
    out += indent+'double cmode_phi[{:d}][{:d}] = '.format(nx,ny)+'{\n'
    for i in range(nx):
        out += indent+'{'+BM.getCModesPhi(i)+ '}' 
        if (i==nx-1):
            out += '\n'
        else:
            out += ',\n' 
    out += indent+'};\n'
    return out

def wmodesPhi(indent):
    out = '\n// Define phase shifts for wavelength definition choppers \n'
    nx = len(BM.wmodes)
    ny = len(BM.wphases[0])
    out += indent+'double wmode_phi[{:d}][{:d}] = '.format(nx,ny)+'{\n'
    for i in range(nx):
        out += indent+'{'+BM.getWModesPhi(i)+ '}' 
        if (i==nx-1):
            out += '\n'
        else:
            out += ',\n' 
    out += indent+'};\n'
    return out


def modesFChoppers(indent):
    out = '\n// Define frequencies for frame selection choppers \n'
    out += indent+'double mod_FC1A_nu[] = {'+BM.getFChopperStr('FC1A') + '};\n' 
    out += indent+'double mod_FC1B_nu[] = {'+BM.getFChopperStr('FC1B') + '};\n'
    out += indent+'double mod_FC2A_nu[] = {'+BM.getFChopperStr('FC2A') + '};\n'
    out += indent+'double mod_FC2B_nu[] = {'+BM.getFChopperStr('FC2B') + '};\n'
    return out


def modesSlits(indent):
    out = '\n// Define slit dimensions [mm]  \n'
    out += indent+'double mod_S1_w[] = {'+BM.getSlitStr('SL1',0) + '};\n' 
    out += indent+'double mod_S2_w[] = {'+BM.getSlitStr('SL2',0) + '};\n' 
    out += indent+'double mod_S3_w[] = {'+BM.getSlitStr('SL3',0) + '};\n' 
    out += indent+'double mod_S1_h[] = {'+BM.getSlitStr('SL1',1) + '};\n' 
    out += indent+'double mod_S2_h[] = {'+BM.getSlitStr('SL2',1) + '};\n' 
    out += indent+'double mod_S3_h[] = {'+BM.getSlitStr('SL3',1) + '};\n'
    return out

def modesGEX1(indent):
    out = '\n// Define focusing guide setting [on/off]  \n'
    out += indent+'int mod_GF3[] = {'+BM.getGEXStr() + '};\n' 
    return out

def modesPSC2dist(indent):
    out = '\n// Define distance of the PSC2 chopper  \n'
    out += indent+'double mod_PSC2dist[] = {'+BM.getPSC2distStr() + '};\n' 
    return out

def modesLambda(indent):
    out = '\n// Define wavelength [A] for each mode  \n'
    out += indent+'double mod_lambda[] = {'+BM.getLambdaStr() + '};\n' 
    return out

def modesFC1A(indent):
    out = '\n// Define additional FC1A phase shift [deg] for each mode  \n'
    out += indent+'double mod_FC1A_dphi[] = {'+BM.getFC1APhiStr() + '};\n' 
    return out

def modes(indent):
    out = _modes_legend()
    out += modesSlits(indent)
    out += cmodesFrq(indent)
    out += wmodesFrq(indent)
    out += cmodesPhi(indent)
    out += wmodesPhi(indent)
    out += modesPSC2dist(indent)
    out += modesGEX1(indent)
    out += modesLambda(indent)
    out += modesFC1A(indent)
    out += '\n// Chopper modes  \n'
    out += indent+'int mod_cmodes[] = {'+BM.getCmodesStr() + '};\n'
    out += indent+'int mod_wmodes[] = {'+BM.getWmodesStr() + '};\n'
    return out
    return out

def _modes_legend():
    """Comment before the mode setting code."""
    out = '\n/*'+50*'-'+'\n'
    out += 'Define reference operation modes \n'
    out += 50*'-'+'\n'
    for i in range(len(BM.modes)):
        m = BM.modes[i]
        out += '{}\t{}\t{}, {}\n'.format(i, m['ID'], m['label'], m['comment'])
    out += 50*'-'+'*/\n'
    return out

def _modes_descr():
    """Text in the instrument description: list of modes."""
    out = ''
    for i in range(len(BM.modes)):
        m = BM.modes[i]
        out += '* {}\t{}\t{}, {}\n'.format(i, m['ID'], m['label'], m['comment'])
    return out

def _init_reports():
    out = reportBeam(beamMonolith, 'Monolith section', indent+indent)
    out += reportBeam(beamBunker, 'Bunker section', indent+indent)
    out += reportBeam(beamTransport, 'Transport section', indent+indent)
    out += reportBeam(beamFocusing, 'Focusing section', indent+indent)
    return out

def _declare_primary():  
    global listComp
    out = "\n/* Component declarations */\n"
    for l in listComp:
        out += declaretype(listComp[l])
    out += '\n'
    return out

def _trace_primary(statinfo):
    out = traceBeam(beamMonolith, 'Monolith section', statinfo)
    out += traceBeam(beamBunker, 'Bunker section', statinfo)
    if _SHIELDING:
        out += '@SHIELDING_START\n'
    out += traceBeam(beamTransport, 'Transport section', statinfo)        
    out += traceBeam(beamFocusing, 'Focusing section', statinfo)
    if _SHIELDING:
        out += '@SHIELDING_STOP\n'
    return out

def get_instr_file(instname='BEER_reference', template='BEER_reference_v3_GPU',
                 inpath=None, statinfo=False, shielding=False, **options):
    """Create McStas instrument file, using provided template.
    
    Parameters
    ----------
    instname : str
        Instrument name, should be equal to the name of the template file 
        without '.instr.template' extension. The output file name will then be 
        instname+'.instr'
    template : str
        Template name without '.instr.template' extension.
    inpath : str
        Input directory for the template file.
        If not defined, search for templates in package resources.
    statinfo : boolean
        If true, the simulation will produce tracing statistics
    shielding : boolean
        If true, the instrument file will include shielding logger
    options : dict
        Options passed to :func:`defineInstrument`.
    
    Returns
    -------
    Content of the instrument file as a string. 
    
    """
    global _SHIELDING
    _SHIELDING = shielding
    defineInstrument(**options)
    template_name = template+'.instr.template'
    out = ''
    declare = _declare_primary()
    init = initPrimary(statinfo)
    trace = _trace_primary(statinfo)
    ell = ellipses(indent)
    rep = _init_reports()
    mymodes = modes(indent)
    lines = getTemplate(template=template+'.instr', inpath=inpath)
    for i in range(len(lines)):
        line = lines[i]
        k = line.find('@')
        if (k>=0):
            line = line.replace('@DECLARE_PRIMARY', declare)
            if (line.find('@')>-1): line = line.replace('@MODESDESCR', _modes_descr())
            if (line.find('@')>-1): line = line.replace('@INIT_PRIMARY', init)
            if (line.find('@')>-1): line = line.replace('@MODES', mymodes)
            # if (line.find('@')>-1): line = line.replace('@TRACE_PRIMARY', trace)
            if (line.find('@')>-1): line = line.replace('@ELLIPSES', ell)
            if (line.find('@')>-1): line = line.replace('@REPORT', rep)
            if (line.find('@')>-1): line = line.replace('@VERSION', BC.VERSION)
            if (line.find('@')>-1): line = line.replace('@DATE', BC.DATE)
            if (line.find('@')>-1): line = line.replace('@TEMPLATE', template_name)
            if (line.find('@')>-1): line = line.replace('@SOURCE', 'beer.mcstas')
            if (line.find('@')>-1): line = line.replace('@NAME', instname)
            if (line.find('@')>-1): line = line.replace('@MAXCOMP', str(nComp))
            if (line.find('@')>-1): line = line.replace('@MAXMON', str(nBMon))
            if (line.find('@')>-1): line = line.replace('@MAXMODE', str(len(BM.modes)-1))
            if (line.find('@')>-1): 
                if statinfo:
                    line = line.replace('@STATINFO', 'printStat();\n')
                else:
                    line = line.replace('@STATINFO','')
                    
            # unknown @, let it be
            if (line.find('@')>-1): line = lines[i]
        else:
            line = lines[i]
        out += line
    out = out.replace('@TRACE_PRIMARY', trace)
    if _SHIELDING: 
        out = add_shielding_calculator(out)
    else:
        if (out.find('@SHIELDING_CALC')>-1):
            out = out.replace('@SHIELDING_CALC', '')
        if (out.find('@SHIELDING_ITER')>-1):
            out = out.replace('@SHIELDING_ITER', '')
    return out
 

def parseTemplate(instname='BEER_reference', template='BEER_reference_v2', 
                  outpath='', **options):
    """Create McStas instrument file, using provided template.
            
    Parameters
    ----------
    instname : str
        Instrument name  without '.instr' extension.
    template : str
        Template name without the '.instr.template' extension.
    outpath : str
        Output directory for the generated McStas instrument file.
        
    options : dict
        Other parameters passed do :func:`get_instr_file`
    """
    out = get_instr_file(instname=instname, template=template, **options)
    outfile = os.path.join(outpath,instname+'.instr')
    with open(outfile, 'w') as fo:
        fo.write(out)
        fo.close()
    print('BEER McStas instrument file saved as {}'.format(outfile))
 

def add_shielding_calculator(inputtxt, zmin=28, zmax=158, bins=130):
    global _SHIELDING
    out = ''
    line = inputtxt
    if (line.find('@SHIELDING_START')>-1): 
        if _SHIELDING:
            out = '\n'
            out += '/'+7*'*'+'  Start shielding logger. '++7*'*'+'/\n'
            out += 'COMPONENT log_P_start=Shielding_logger()\n'
            out += 'AT (0,0,0) RELATIVE PREVIOUS\n'
            out += 'EXTEND\n%{\n'
            out += '#ifdef scatter_logger_stop\n'
            out += '#undef scatter_logger_stop\n'
            out += '#undef scatter_logger_stop\n'
            out += '#endif\n'
            out += '#define scatter_logger_stop log_P_start\n'
            out += '%}\n\n'
            out += '\n'
            line = line.replace('@SHIELDING_START', out)
        else:
            line = line.replace('@SHIELDING_START', '')
    if (line.find('@SHIELDING_STOP')>-1): 
        if _SHIELDING:
            out = '\n\n'
            out = '/'+7*'*'+'  Stop shielding logger. '++7*'*'+'/\n'
            out += 'COMPONENT log_P_stop=Shielding_logger_stop(logger=log_P_start)\n'
            out += 'AT (0,0,0) RELATIVE PREVIOUS\n'  
            line = line.replace('@SHIELDING_STOP', out)
        else:
            line = line.replace('@SHIELDING_STOP', '')
    if (line.find('@SHIELDING_ITER')>-1):
        if _SHIELDING:
            arm = 'Arm1'
            lines = getTemplate(template='ShieldingIterator')
            out = '\n'
            for ln in lines:
                out += ln
            out += '\n'
            while (out.find('@ZMIN')>-1): out = out.replace('@ZMIN', '{:g}'.format(zmin))
            while (out.find('@ZMAX')>-1): out = out.replace('@ZMAX', '{:g}'.format(zmax))
            while (out.find('@ZBINS')>-1): out = out.replace('@ZBINS', '{:g}'.format(bins))
            while (out.find('@SH_START_ELEMENT')>-1): 
                out = out.replace('@SH_START_ELEMENT', arm)
            line = line.replace('@SHIELDING_ITER', out)
        else:
            line = line.replace('@SHIELDING_ITER', '')
    if (line.find('@SHIELDING_CALC')>-1):
        if _SHIELDING:
            lines = getTemplate(template='ShieldingCalculator')
            out = '\n'
            for ln in lines:
                out += ln
            out += '\n'
            line = line.replace('@SHIELDING_CALC', out)
        else:
            line = line.replace('@SHIELDING_CALC', '')
    return line



    