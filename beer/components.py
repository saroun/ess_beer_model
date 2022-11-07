# -*- coding: utf-8 -*-
"""
Module with definitions of BEER guide system sections and tools for 
exporting tables and graphical output of schematics.

Created on Wed Jul  4 11:17:33 2018
@author: J. Saroun, saroun@ujf.cas.cz
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez

update 2019-08-27: revision 1.5
    Adjusted NBOA+BBG according actual drawings
    Adjusted shutter pit , W02-13 to W02-15 according actual drawings.
    
update 2020-03-04: revision 1.51
    Moved to submodule and renamed from BEERcomponents.py.
    Updated doc texts 
    
update 2020-05-18: revision 1.6
    Updated according to the final CAD model submitted to TG3 review.
    Added W02-19 miniguide (GMINI). Update of distances and gaps measured in CAD.
    Fixed sizes for GEX2 and SL3.
    Added doc strings.
    Added definitions for radial collimators.
    Reduced windows for FC2A and FC2B to 175 and 85 deg, respectively
update 2022-10-14: revision 1.7
    Updated PSC1-PSC2 sector according to the design (no movable guides)
    Bug fix - remove smoothness of guides TG1, TG2 
"""

import beer.geometry as B
import datetime
import numpy as np
VERSION = '1.7'
DATE = datetime.datetime.now().strftime("%B %d, %Y, %H:%M:%S")

#%% Define global data

# list of BER components
BEER = {}

# table header id strings
_hdr = ['ID', 'start', 'end', 'length', 'type', 'name', 'w1', 'w2', 'h1', 'h2', 
       'ctr1', 'ctr2', 'mL', 'mR', 'mT', 'mB', 'geomH', 'geomV', 'mater', 'comment']

# basic distances
sample_dist=158000


# BEER collimators
RADC = {}


# %% Functions describing component tyes

def collimator(dist=310, length=350, angle=30, height=1000, nslit=160, dlam=0.1):    
    """
    Defines a radial collimator.
    
    Arguments:
    ---------
    dist: float
        distance from the sample axis
    length: float
        length [mm]
    angle: float
        span horizontal angle [deg]
    height: float
        detector height in mm, assumed distance 2000 mm
    nslit: int
        number of slits (1 + lamellae) 
    dlam: float
        lamella thickness [mm]
    
    """
    deg = 180/np.pi
    def w(d):
        return d*angle/deg
    def h(d):
        return 20 + height*d/2000
    wentry = [w(dist), h(dist)]
    wexit = [w(dist+length), h(dist+length)]
    el = {}
    el['dist'] = dist
    el['angle'] = angle
    el['length'] = length
    el['entry'] = wentry
    el['exit'] = wexit
    el['nslit'] = nslit
    el['dlam'] = dlam
    return el
    
def guide(num, start, end, desc, m=[4., 4., 4., 4.], gh = None, gv=None, 
          RH=0., RV=0., const=False, substr='NBK-7', wentry=None, wexit=None):
    """
    Defines parameters for a neutron guide.
    
    Arguments:
    ----------
    num: int or string
        Component ID. An integer is parsed to string as 'W02-{:d}'. 
    start: float
        entry distance
    end: float
        exit distance
    desc: str
        description
    m: array(4)
        m-values for left, right, top, bottom
    gh: optional
        horizontal ellipse parameters in format 'E2 = {'a':a, 'b':b, 'c':b} '
        where a=major semiaxis, b=minor semiaxis, c = distance of the centre.
    gv: optional
        like gh, but for vertical profile. 
    RH: float
        if != 0, horizontal bending radius
    RV: float
        if != 0, vertical bending radius
    const: boolean
        if true, constant cross-section
    substr: str
        string identifying substrate material
    wentry: optional
        [width, height] for the entry window. If not defined, the size is 
        determined from the calculated beam profile in beer.geometry.
    wexit: optional
        [width, height] for the exit window.  If not defined, the size is 
        determined from the calculated beam profile in beer.geometry.

    """

    el = {}
    el['id'] = 'W02-{}'.format(num)
    el['dist'] = start
    el['start'] = start
    el['end'] = end
    el['desc'] = desc
    el['type'] = 'optics'
    el['thickness']=end-start
    el['m']=m
    el['gh']=gh
    el['gv']=gv
    el['RH']=RH
    el['RV']=RV
    el['const'] = const
    el['substr'] = substr
    if (wentry is not None):
        el['entry'] = wentry
    if (wexit is not None):
        el['exit'] = wexit        
    return el
  
def chopper(name, distance, desc, status=True, thickness=10, fmax=168, win=144, wctr=[0]):
    """
    Defines parameters for a chopper.
    
    Arguments:
    ----------
    name: str
        component ID
    distance: float
        distance to the centre
    desc: str
        description text
    status: boolean
        if false, 'UPGRADE' flag is added to the comment (not part of basic scope)
    thickness: float
        disc thickness
    fmax: float
        Maximum frequency [Hz]
    win: float or str
        window size in [deg], or any other description of windows (used in comments)
    wctr: list
        window centres in deg
    
    """
    def win2list(w):
        out = []
        if isinstance(w,str):
            sp = w.split('+')
            for i in range (len(sp)):
                s = sp[i].strip()
                sx = s.strip().split('x')
                if len(sx)==2:
                    out += int(sx[0])*[float(sx[1])]
                elif len(sx)==1:
                    out += [float(sx[0])]
                else:
                    raise Exception('wrong parameter format, chopper.win="{}" '.format(w))
        elif isinstance(w,int) or isinstance(w,float):
            out += [w]
        return out

    el = {}
    el['id'] = name
    el['dist'] = distance
    el['start'] = distance-0.5*thickness
    el['end'] = distance+0.5*thickness
    el['desc'] = desc
    el['type'] = 'chopper'
    el['thickness']=thickness
    el['rad'] = 350.0 # disc radius
    el['fmax'] = fmax
    el['win'] = win2list(win)
    el['winstr'] = str(win)
    el['wctr'] = wctr
    el['status'] = status # false if not included in the TG2 scope setting
    return el
    
def slit(name, distance, desc, thickness=20, size=None):
    """
    Defines parameters of a slit.
    
    Arguments:
    ---------
    name: str
        component ID
    distance: float
        distance to the centre
    desc: str
        description text
    thickness: float
        thickness  
    size: optional
        [width, height]. If not defined, the size is calculated by beam.geometry.
    """
    el = {}
    el['id'] = name
    el['dist'] = distance
    el['start'] = distance-0.5*thickness
    el['end'] = distance+0.5*thickness
    el['desc'] = desc
    el['type'] = 'slit'
    el['thickness']=thickness
    if (size is not None):
        el['size'] = size
    return el
 
def window(name, distance, thickness=0.5):
    """
    Defines parameters of an Al window.
    
    Arguments:
    ---------
    name: str
        component ID
    distance: float
        distance to the centre
    thickness: float
        thickness  
    """
    el={}
    el['id']=name
    el['dist'] = distance
    el['start']=distance
    el['end'] = distance+thickness
    el['desc']=' '
    el['type']='window'
    el['thickness']=thickness
    return el

def switch(num, distance, thickness=15, m=[3., 3., 0., 0.], 
           size=[22.5, 65.], nlam=149, dlam=0.15, angle=-0.57):
    """Define parameters for a bi-spectral switch.
    
    Parameters
    ----------
    num : int or string
        Component ID. An integer is parsed to string as 'W02-{:d}'. 
    distance : float
        entry distance
    thickness : float
        thickness (length)
    m : array(4)
        m-values for left, right, top, bottom
    size : float(2)
        [width, height]
    nlam : int
        Number of blades.
    dlam : float
        Blade thickness in mm.
    angle : float
        Rotation angle in deg.
        
    """    
    el={}
    el['id'] = 'W02-{}'.format(num)
    el['dist'] = distance
    el['start']=distance
    el['end'] = distance+thickness
    el['type']='optics'
    el['thickness']=thickness
    el['m']=m
    el['RH']=0.
    el['RV']=0.
    el['const'] = True
    prof = [0.5*size[0], -0.5*size[0], 0.5*size[1], -0.5*size[1], size[0], size[1]]
    el['prof'] = prof
    el['substr'] = 'Si'
    el['dlam'] = dlam
    el['nlam'] = nlam
    el['angle'] = angle
    el['desc']='bi-spectral switch, adjustable angle, movable on/off the beam'
    el['gv']=' '
    el['gh']='stack of {:g} um Si wafers, angle={:g}o rel. to ISCS_x axis'.format(dlam*1000, angle)
    
    return el

def getEllStr(E):
    """Ellipse parameters"""
    fmt = 'a:{:g}, b:{:g}, ctr:{:g}'
    out = fmt.format(E['a'], E['b'], E['c'])
    return out

def getChopperGuide(num, start, end):
    """
    Special descriptor for short guides in chopper section
    """
    stre = 'flat expanding, on ellipse '+getEllStr(B.E1)
    g = guide(num, start, end,'chopper guide element', 
              m=[4., 4., 3., 3.], gv=stre, substr='Cu')
    return g


   
# %% Define BEER components 

def defineComponents():
    """
    Main procedure, where the global variable BEER is defined.
    It contains the sequence of all BEER optical components.
    """

    global RADC, BEER, sample_dist
    # standard gaps:
    w = 0.5 # Al window thickness
    g = 1 # std. gap between major guide sections (no windows)
    go = 1.5 # gap between Al window and optics
    gw = w + go
    gc = 50 # gap between chopper discs
    gcg = 25 # chopper center to guide in common housing
    #gsh = 20 # air gap between shutter and guide window
    #gsh = 5 # air gap between shutter and guide window
    #gsl = 30 # gap for a slit
    
    # radial collimaors
    RADC['RAD05'] = collimator(dist=100)
    RADC['RAD1'] = collimator(dist=160)
    RADC['RAD2'] = collimator(dist=310)
    RADC['RAD3'] = collimator(dist=400)
    RADC['RAD4'] = collimator(dist=490)
    
    # Start - end of NBOA 
    nboa_start = 2030.5
    nboa_end = 5390.5
    
    # NBPI window, 1 mm
    nbpi_start = 5396.00
    
    # BBG window 1, 0.5 mm	
    bbg_win1 = 5407.80
    
    # Start of BBG 
    bbg_start = 5410.80 
    
    # End of BBG 
    bbg_end = 5893.80
    
    # BBG window 2, 0.5 mm
    bbg_win2 = 5896.30
    
    # NBPI
    BEER['W0'] = window('W0', nboa_start - 5, thickness=1.5)
    BEER['NBOA'] = guide(1, nboa_start, nboa_end, 'monolith insert optics', 
        m=[2.5, 2.5, 4., 4.], gv=B.E1,substr='Cu')
    BEER['W1'] = window('W1', nbpi_start, thickness=1.0)
    
    # BBG
    BEER['W2'] = window('W2', bbg_win1, thickness=0.5)
    BEER['BBG'] =  guide(2,  bbg_start, bbg_end, 'bridge beam guide',
        m=[2.5, 2.5, 4., 4.], gv='flat expanding, on ellipse '+getEllStr(B.E1), 
        substr='Cu')
    BEER['W3'] = window('W3', bbg_win2, thickness=0.5)
        
    # bi-Switch window, 0.5 mm
    bsw_win = 5911.30
    BEER['W4'] = window('W4', bsw_win)
    # bi-spectral switch, assumed to be inside the 1st guide and chopper housing
    BEER['GSW'] =  switch(3, 5931.80, m=[3., 3., 0., 0.])
        
    # start of the chopper section
    PSC1_dist = 6450
    PSC2_dist = 6850
    PSC2_width = 62 # width of the PSC2 housing 
    dist12 = 210
    #PSC1_width = 200 # width of the PSC1 housing
    GCA2_len=PSC2_dist-PSC1_dist-0.5*PSC2_width-dist12-go-w-gcg
    # format chopper guide section: 
    BEER['GCA1'] =  getChopperGuide('4-01',BEER['GSW']['end']+20, PSC1_dist-gcg)
    BEER['PSC1'] = chopper('PSC1',PSC1_dist, desc='pulse shaping')
    BEER['GCA2'] =  getChopperGuide('4-02', PSC1_dist+gcg, PSC1_dist+gcg+GCA2_len)
    BEER['W5'] = window('W5', BEER['GCA2']['end']+go)
    BEER['W6'] = window('W6', BEER['W5']['end'] + dist12)
#    BEER['GCA3'] =  getChopperGuide('4-03', BEER['W6']['end']+go, PSC2_dist-gcg)
    BEER['PSC2'] = chopper('PSC2',PSC2_dist, desc='pulse shaping, variable distance 6650 to 6850')
#    BEER['GCA4'] =  getChopperGuide('4-04', PSC2_dist+0.5*PSC2_widthgcg, PSC2_dist+0.5*PSC2_width-gw)
    BEER['W7'] = window('W7', PSC2_dist + 0.5*PSC2_width-w)
    
    PSC3_dist = 7375
    FC1_dist = 8300
    MCA_dist = 9300
    MCB_dist = 9350
    MCC_dist = 9875
    BEER['W8'] = window('W8', BEER['W7']['end']+10)
    BEER['GCB'] =  getChopperGuide(5, BEER['W8']['end']+go, PSC3_dist-gcg)
    BEER['PSC3'] = chopper('PSC3',PSC3_dist, 'pulse shaping', status=False)
    BEER['GCC'] =  getChopperGuide(6, PSC3_dist+gcg, FC1_dist-0.5*gc-gcg)
    BEER['FC1A'] = chopper('FC1A',FC1_dist-0.5*gc, fmax=28, win=72, desc='WFD')
    BEER['FC1B'] = chopper('FC1B',FC1_dist+0.5*gc, fmax=70, win=180, desc='WFD', status=False)
    BEER['GCE'] =  getChopperGuide(7, FC1_dist+0.5*gc+gcg, MCA_dist-gcg)
    wctr = []
    for i in range(8):
        wctr.append(i*360/8)
    BEER['MCA'] =  chopper('MCA',MCA_dist, fmax=280, win='8 x 5', wctr=wctr, desc='modulation')
    wctr = []
    for i in range(16):
        wctr.append(i*360/16)
    BEER['MCB'] =  chopper('MCB',MCB_dist, fmax=280, win='16 x 5', wctr=wctr, desc='modulation', status=False)
    BEER['GCF'] =  getChopperGuide(8, MCB_dist+gcg, MCC_dist-gcg)
    wctr = [0]
    for i in range(7):
        wctr.append(90+(i+1)*180/8)
    BEER['MCC'] =  chopper('MCC',MCC_dist, fmax=280, win='180 + 7 x 5', wctr=wctr, desc='modulation', status=False)
    BEER['GCG'] =  getChopperGuide(9, MCC_dist+gcg, B.curve1_begin-gw-10-gw)
    BEER['W9'] = window('W9', B.curve1_begin-gw-10-w)
    # end of the chopper section    
    
    # bunker wall throughput:
    wall_in=24500.0 # start of the bunker wall insert optics
    wall_out=27998.0  # end of the bunker wall insert optics
    
    # Start of the curved guide, vertical elliptic expansion
    BEER['W10'] = window('W10', B.curve1_begin-gw)
    BEER['GE1'] =  guide(10, B.curve1_begin, B.E1['c']-g, 
        'NOTE: bent & vertically expanding !', m=[3., 2.5, 3., 3.], 
        RH=1e-6/B.curve1, gv=B.E1, substr='Cu')
    # Curved guide, parallel, inside bunker
    BEER['GN1'] =  guide(11, B.E1['c'], wall_in-g,' ', 
        m=[3., 2.5, 2., 2.], RH=1e-6/B.curve1, substr='Cu')
    # Curved guide, parallel,  bunker wall insert
    BEER['GN2'] =  guide(12, wall_in, wall_out, 
        'bunker wall insert', m=[3., 2.5, 2., 2.], RH=1e-6/B.curve1, substr='Cu')
    BEER['W11'] = window('W11', wall_out+go)
    
    # shutter guide 
    shutter_start = 28005.00 # with housing
    shutter_end = shutter_start + 610 # with housing
    BEER['W12'] = window('W12', shutter_start)
    # optics starts after 0.5 mm Al window, 3 mm gap and 5 mm B4C mask
    # ends with a 2.5 mm gap and 0.5 mm Al window
    BEER['GSH2'] =  guide(13, shutter_start + 5 + 3 + w, shutter_end - 2.5, 
        'shutter insert', m=[2.5, 2.5, 2., 2.], substr='Cu')
    BEER['W13'] = window('W13', shutter_end - w)
    
    # Shutter wall insert
    shutter_insert_window = 28620.0 
    shutter_insert_start = 28628.0 # update ver. 1.6
    shutter_insert_end = 31357.9 # update ver. 1.6
    # start of the next guide after shutter insert:
    shutter_wall_end = 31360 # update ver. 1.6
    
    # 0.5 mm Al window + 2.5 mm gap + 5 mm B4C mask at the entry
    BEER['W14'] = window('W14', shutter_insert_window)
    # update ver. 1.5, adding straight element
    BEER['GE2AS'] =  guide(14, shutter_insert_start , B.E2_start-g, 
        'shutter pit insert, parallel', m=[2.5, 2.5, 2., 2.], substr='Cu')
    BEER['GE2A'] =  guide(14, B.E2_start , shutter_insert_end, 
        'shutter pit insert, elliptic', m=[2.5, 2.5, 2., 2.], gh=B.E2, substr='Cu')
    BEER['GE2B'] =  guide(15, shutter_wall_end, B.curve2_begin-2.3, 
        ' ', m=[2.5, 2.5, 2., 2.], gh=B.E2)
    
    # Transport guide
    FC2_dist = 80000
    BEER['GT1'] =  guide(16, B.curve2_begin+1.3, FC2_dist-0.5*gc-gcg, 
        'transport guide before chopper', m=[2.0, 2.5, 2., 2.], RH=1e-6/B.curve2)
    BEER['FC2A'] = chopper('FC2A',FC2_dist-0.5*gc, fmax=14, win=175, 
        desc='wavelength frame definition')
    BEER['FC2B'] = chopper('FC2B',FC2_dist+0.5*gc, fmax=14, win=85, 
        desc='wavelength frame definition', status=False)
    # added 5 mm B4C mask
    BEER['GT2'] =  guide(17, FC2_dist+0.5*gc+gcg+5, 144498.15, 
        'transport guide after chopper', m=[2.0, 2.5, 2., 2.], RH=1e-6/B.curve2)
    
    # Focusing guide
    slit1_dist=152000
    slit2_dist=155000
    BEER['GF1'] =  guide(18, 144500.0, 151979.94, 
        ' ', m=[2.5, 2.5, 3., 3.], gv=B.E3)
    BEER['SL1'] =  slit('SL1', slit1_dist, 'Adjustable diaphragm')
      
    BEER['GF2'] =  guide(19, 152024.95, 154979.95,     
        'L/R mirror only 0 .. 2500 mm, then absorbing', m=[2.5, 2.5, 4., 4.], gv=B.E3)
    
    # cave wall insert start 154056 mm
    
    BEER['SL2'] =  slit('SL2', slit2_dist, 'Adjustable diaphragm')
    
    # update ver. 1.6, adding mini guide after SL2
    BEER['GMINI'] =  guide('19M', 155024.9 , 155117.9, 'mini guide at SL2', m=[0, 0, 5., 5.])
    BEER['W15'] = window('W15', 155120-w)
    
    # Guide exchanger with focusing guide and collimator
    BEER['W16'] = window('W16', 155125.5)
    BEER['GEX1'] =  guide('20-01', 155133.0, 157000.0, 
        'Focusing guide on exchanger', m=[0., 0., 5., 5.], gv=B.E3)
    BEER['GEX2'] =  guide('20-02', 155133.001, 157000.0, 
        'Collimator on exchanger', m=[0., 0., 0., 0.], const = True, wentry=[40., 50.])
    BEER['W17'] = window('W17', BEER['GEX2']['end'] + go)
    
    # Input slit
    
    BEER['SL3'] =  slit('SL3', sample_dist-50, 
        'Sample input slit, adjustable distance and size',
        size=[10., 20.])
       
    # store key as the component property:
    for key in BEER:
        BEER[key]['key'] = key


# %% Various utility functions

def sortedKeys():
    """Get keys for components sorted by distance
    """
    d = {}
    for key in BEER:
        d[key] = BEER[key]['start']
    keys = sorted(d, key=lambda k: d[k])
    return keys

def createRec(dist, ctype):
    """Create empty record for a component as a hash map.
    Aruments:
    --------
    dist: float
        distance
    ctype: str
        component type
    """
    global _hdr
    rec = {}
    for key in _hdr:
        rec[key]=' '
    rec['start'] = '{:.1f}'.format(dist)
    rec['type'] = ctype
    return rec


def getGeomStr(g=None, R=0., w1=2., w2=2.):
    out = []
    if g==None:
        if (R==0.):
            out.append('straight')
        else:
            out.append('curved, R={:.3f} km'.format(R))
        if (w2 > w1):
            out.append('expanding')
        elif (w2 < w1):
            out.append('convergent')
        else:
            out.append('parallel')
    elif (type(g) == str):
        out.append(g)
    else:
         # g assumed to be ellipse parameters
        gstr = getEllStr(g)
        out.append('ellipse({})'.format(gstr))
        if (R!=0.):
            out.append('curved, R={:.3f} km'.format(R))
        if (w2 > w1):
            out.append('expanding')
        elif (w2 < w1):
            out.append('convergent')         
    # convert to string
    nr = len(out)
    fmt = '{}'     
    fmt += (nr-1)*', {}'
    return fmt.format(* out)
"""    
def getEntryExit_old(comp, coord = 'ISCS'):
    dist =  comp['start']
    end = comp['end']
    if ('const' in comp):
        const = comp['const']
    else:
        const = False
    if ('prof' in comp):
        prof1 = comp['prof']
        ax1 = B.beamAxis(dist, coord = coord)
        ax2 = B.beamAxis(end, coord = coord)
        w1 = prof1[4]
        h1 = prof1[5]
        w2 = w1
        h2 = h1     
        ctr1 = 0.5*(prof1[0]+prof1[1]) + ax1[1]
        ctr2 = 0.5*(prof1[0]+prof1[1]) + ax2[1]
    else:
        prof1 = B.beamSize(dist,coord=coord).reshape(6,)
        prof2 = B.beamSize(end,coord=coord).reshape(6,)
        w1 = prof1[4]
        h1 = prof1[5]
        if (const):
            w2 = w1
            h2 = h1
        else:
            w2 = prof2[4]
            h2 = prof2[5]        
        ctr1 = 0.5*(prof1[0]+prof1[1])
        ctr2 = 0.5*(prof2[0]+prof2[1]) 
    return [w1, h1, w2, h2, ctr1, ctr2]
"""

def getFace(comp, dist, coord = 'ISCS'):
    """
      Return width, height and component center position in given coordinates.
    """
    if ('prof' in comp):
        prof1 = comp['prof']
        ax1 = B.beamAxis(dist, coord = coord)
        w1 = prof1[4]
        h1 = prof1[5]    
        ctr1 = 0.5*(prof1[0]+prof1[1]) + ax1[1]
    else:
        prof1 = B.beamSize(dist,coord=coord).reshape(6,)
        w1 = prof1[4]
        h1 = prof1[5]       
        ctr1 = 0.5*(prof1[0]+prof1[1])
    return [w1, h1, ctr1]

def getEntryExit(comp, coord = 'ISCS'):
    dist =  comp['start']
    end = comp['end']
    [w1, h1, ctr1] = getFace(comp, dist, coord = coord)
    if ('entry' in comp):
        [w1, h1] = comp['entry']
    [w2, h2, ctr2] = getFace(comp, end, coord = coord)
    if ('exit' in comp):
        [w2, h2] = comp['exit']
    if ('const' in comp):
        if comp['const']:
            w2 = w1
            h2 = h1
    return [w1, h1, w2, h2, ctr1, ctr2]


#%% Construction of records with components parameters stored as strings

def getGuideData(comp, coord = 'ISCS'):
    """Return hash map with strings for component row cells
    """
    dist =  comp['start']
    end = comp['end']
    L = end - dist    
    m = comp['m']
    gh = comp['gh']
    gv = comp['gv']
    RH = comp['RH']
    RV = comp['RV']       
    [w1, h1, w2, h2, ctr1, ctr2] = getEntryExit(comp, coord = coord)
    
    rec = createRec(dist, comp['type'])
    rec['ID'] = comp['id']
    rec['end'] = '{:.1f}'.format(end)
    rec['length'] = '{:.1f}'.format(L)
    rec['name'] = comp['key']
    rec['w1'] = '{:.2f}'.format(w1)
    rec['w2'] = '{:.2f}'.format(w2)
    rec['h1'] = '{:.2f}'.format(h1)
    rec['h2'] = '{:.2f}'.format(h2)
    rec['ctr1'] = '{:.2f}'.format(ctr1)
    rec['ctr2'] = '{:.2f}'.format(ctr2)
    rec['geomH'] = getGeomStr(g = gh, R=RH, w1 = w1, w2 = w2)
    rec['geomV'] = getGeomStr(g = gv, R=RV, w1 = h1, w2 = h2)
    rec['mL'] = '{:g}'.format(m[0])
    rec['mR'] = '{:g}'.format(m[1])
    rec['mT'] = '{:g}'.format(m[2])
    rec['mB'] = '{:g}'.format(m[3])
    rec['mater'] = '{}'.format(comp['substr'])
    rec['comment'] = comp['desc']
    
    return rec

def getChopperData(comp, coord = 'ISCS'):
    """Return hash map with strings for component row cells
    """
    dist =  comp['start']
    end = comp['end']
    L = comp['thickness']   
    """
    prof1 = B.beamSize(dist,coord=coord).reshape(6,)
    prof2 = B.beamSize(dist+L,coord=coord).reshape(6,)
    w1 = prof1[4]
    w2 = prof2[4]
    h1 = prof1[5]
    h2 = prof2[5]
    c1 = 0.5*(prof1[0]+prof1[1])
    c2 = 0.5*(prof2[0]+prof2[1]) 
    """
    [w1, h1, w2, h2, c1, c2] = getEntryExit(comp, coord = coord)
    
    
    ctr1 = 0.5*(c1+c2)
    w1 = 0.5*(w1+w2)
    h1 = 0.5*(h1+h2)   
    com = ''
    if (not comp['status']):
        com += 'UPGRADE, '
    com += comp['desc']
    com += ', fmax={} Hz, win={} deg'.format(comp['fmax'], comp['winstr'])
    
    rec = createRec(dist, comp['type'])
    rec['ID'] = comp['id']
    rec['end'] = '{:.1f}'.format(end)
    rec['length'] = '{:.1f}'.format(L)
    rec['name'] = comp['key']
    rec['w1'] = '{:.2f}'.format(w1)
    rec['h1'] = '{:.2f}'.format(h1)
    rec['ctr1'] = '{:.2f}'.format(ctr1)
    rec['comment'] = com
    return rec

def getSlitData(comp, coord = 'ISCS'):
    """Return hash map with strings for component row cells
    """
    dist =  comp['start']
    end = comp['end']
    L = comp['thickness']
    
    prof1 = B.beamSize(dist,coord=coord).reshape(6,)
    prof2 = B.beamSize(dist+L,coord=coord).reshape(6,)
    w1 = prof1[4]
    w2 = prof2[4]
    h1 = prof1[5]
    h2 = prof2[5]
    c1 = 0.5*(prof1[0]+prof1[1])
    c2 = 0.5*(prof2[0]+prof2[1])
    ctr1 = 0.5*(c1+c2)
    w1 = 0.5*(w1+w2)
    h1 = 0.5*(h1+h2)
    
    if ('size' in comp):
        [w1, h1] = comp['size']
    com = comp['desc']
    
    rec = createRec(dist, comp['type'])
    rec['ID'] = comp['id']
    rec['end'] = '{:.1f}'.format(end)
    rec['length'] = '{:.1f}'.format(L)
    rec['name'] = comp['key']
    rec['w1'] = '{:.2f}'.format(w1)
    rec['h1'] = '{:.2f}'.format(h1)
    rec['ctr1'] = '{:.2f}'.format(ctr1)
    rec['comment'] = com
    return rec

def getSampleData(dist, coord = 'FP'):
    """Return hash map with strings for component row cells
    """    
    axis = B.beamAxis(dist, coord=coord).reshape(3,)    
    com = 'Sample axis'
    rec = createRec(dist, 'sample')
    rec['ctr1'] = '{:.2f}'.format(axis[1])
    rec['comment'] = com
    return rec

def getWindowData(comp, coord = 'FP'):
    """Return hash map with strings for component row cells
    """        
    dist =  comp['start']
    end = comp['end']
    L = comp['thickness']   
    com = comp['desc']    
    rec = createRec(dist, comp['type'])
    rec['end'] = '{:.1f}'.format(end)
    rec['length'] = '{:.1f}'.format(L)
    rec['comment'] = com
    return rec

def getGapData(dist1, dist2, typ='gap'):
    """Return hash map with strings for component row cells
    """   
    L = dist2-dist1  
    rec = createRec(dist1, typ)
    rec['end'] = '{:.1f}'.format(dist2)
    rec['length'] = '{:.1f}'.format(L)
    return rec


def getComponentData(comp, coord = 'ISCS'):
    """
    Encapsulating function for geting a record with parameters
    of given component.
    
    Parameters:
    ----------
    
    comp:
        record returned by component definition functions (slit, chopper, guide, ...)
        
    coord: str
        reference frame to be used in coordinate calculation
    """
    if (comp['type'] == 'optics'):
        row = getGuideData(comp, coord = coord)
    elif (comp['type'] == 'slit'):
        row = getSlitData(comp, coord = coord)
    elif (comp['type'] == 'chopper'):
        row = getChopperData(comp, coord = coord) 
    elif (comp['type'] == 'window'):
        row = getWindowData(comp, coord = coord)
    else:
        raise Exception('Unknown component type: {}'.format(comp['type']))
    return row

#%% Write table of components

def writeComponents(coord = 'ISCS', file = '', gaps=False):
    """ Exports tab-separated table with neutron optics elements as they are 
    shown in the BEER optics specifications table, ESS-0478295.
    
    Arguments
    ----------
    coord: str
        coordinate system in which the beam centre positions should be expressed.
        Note that distances are ALWAYS defined as ISCS_x coordinates 
        (provided that the global variable _COORD of beer.geometry is set to 'ISCS') 
    file: str
        output file name
    gaps: boolean
        if true, report also gaps between optics elements
    
    """
    global _hdr
    def formatCells(fmt,row):
        cells = []
        for i in range(len(_hdr)):
            cells.append(row[_hdr[i]])
        ln = fmt.format(* cells)
        return ln
    
    out = '# Generated by module: beer.components\n'
    out += '# Date:\t{}\n'.format(DATE)
    out += '# Version:\t{}\n'.format(VERSION)
    n = len(_hdr)
    fmt = '{}'
    fmt += (n-1)*'\t{}'+'\n'
    
    # get table header for output
    header = fmt.format(*_hdr)
    out += header
    keys = sortedKeys()
    pre = None
    nwin = 0
    ngap = 0
    nair = 0
    dwin = 0.0
    dgap = 0.0
    dair = 0.0
    air = True
    
    for key in keys:
        comp = BEER[key]       
        row = getComponentData(comp, coord = coord)
        if (comp['type'] == 'window'):
            nwin += 1
            dwin += comp['thickness']  
        nr = len(row)
        fmt = '{}'
        fmt += (nr-1)*'\t{}'+'\n'
        if (nr != n):
            raise Exception('Number of collumns must be {}'.format(n))
        # report gaps
        if (gaps and (pre is not None)):
            d1 = pre['end']
            d2 = comp['start']
            if (d2-d1>0.1):
                # don't add gaps before and after SL3 to the total thickness
                if (key != 'SL3'):
                    if (air): 
                        nair += 1
                        dair += (d2-d1)
                    else:
                        ngap += 1
                        dgap += (d2-d1)
                if (air): gap = getGapData(d1, d2, typ='air')
                else: gap = getGapData(d1, d2)
                ln = formatCells(fmt, gap)
                out += ln
        
        ln = formatCells(fmt, row)
        out += ln
        pre = comp
        if (comp['type'] == 'window'):
            air = not(air)
    if (gaps):
        gap = getGapData(BEER['SL3']['end'], sample_dist,typ='air') 
        ln = formatCells(fmt, gap)
        out += ln
    row = getSampleData(sample_dist, coord = coord)
    ln = formatCells(fmt, row)
    out += ln
    if (file != ''):
        f = open(file, 'w')
        f.write(out)
        f.close()
        print('Components table written in {}'.format(file))
    print('{} air gaps, total thickness = {:.1f} mm'.format(nair,dair))
    print('{} vacuum gaps, total thickness = {:.1f} mm'.format(ngap,dgap))
    print('{} windows, total thickness = {:.1f} mm'.format(nwin,dwin))

#%% Execute on import

defineComponents()
