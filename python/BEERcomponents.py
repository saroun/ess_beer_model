# -*- coding: utf-8 -*-
"""
Module with definitions of BEER guide system sections and tools for 
exporting tables and graphical output of schematics.
version: 1.5
Date: October 13, 2018, 2018

Created on Wed Jul  4 11:17:33 2018
@author: J. Saroun, saroun@ujf.cas.cz


update 2019-08-27: revision 1.5
    Adjusted NBOA+BBG according actual drawings
    Adjusted shutter pit , W02-13 to W02-15 according actual drawings.
"""

#import numpy as np
#from matplotlib import pyplot as plt
import BEERgeometry as B
import datetime
VERSION = '1.5'
DATE = datetime.datetime.now().strftime("%B %d, %Y, %H:%M:%S")

# %% Define component list sections

def guide(num, start, end, desc, m=[4., 4., 4., 4.], gh = None, gv=None, 
          RH=0., RV=0., const=False):
    el = {}
    el['id'] = 'W02-{}'.format(num)
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
    return el
  
def chopper(name, distance, desc, status=True, thickness=10, fmax=280, win='144'):
    el = {}
    el['id'] = name
    el['start'] = distance-0.5*thickness
    el['end'] = distance+0.5*thickness
    el['desc'] = desc
    el['type'] = 'chopper'
    el['thickness']=thickness
    el['rad'] = 350.0 # disc radius
    el['fmax'] = fmax
    el['win'] = win
    el['status'] = status # false if not included in the TG2 scope setting
    return el
    
def slit(name, distance, desc, thickness=20):
    el = {}
    el['id'] = name
    el['start'] = distance-0.5*thickness
    el['end'] = distance+0.5*thickness
    el['desc'] = desc
    el['type'] = 'slit'
    el['thickness']=thickness
    return el
 
def window(name, distance, thickness=0.5):
    el={}
    el['id']=name
    el['start']=distance
    el['end'] = distance+thickness
    el['desc']=' '
    el['type']='window'
    el['thickness']=thickness
    return el

def switch(num, distance, thickness=15, m=[3., 3., 0., 0.], size=[22.5, 65.]):
    el={}
    el['id'] = 'W02-{}'.format(num)
    el['start']=distance
    el['end'] = distance+thickness
    el['desc']='bi-spectral switch, adjustable angle, movable on/off the beam'
    el['type']='optics'
    el['thickness']=thickness
    el['m']=m
    el['gh']='stack of 150 um Si wafers, angle=-0.57o rel. to ISCS_x axis'
    el['gv']=' '
    el['RH']=0.
    el['RV']=0.
    el['const'] = True
    prof = [0.5*size[0], -0.5*size[0], 0.5*size[1], -0.5*size[1], size[0], size[1]]
    el['prof'] = prof
    
    return el

# Each section contains: Section ID, name,
# start, end, type, description 

w = 0.5 # Al window thickness
g = 1 # std. gap between major guide sections (no windows)
go = 1.5 # gap between Al window and optics
gw = w + go
gc = 50 # gap between chopper discs
gcg = 25 # chopper center to guide in common housing
#gsh = 20 # air gap between shutter and guide window
gsh = 5 # air gap between shutter and guide window
gsl = 30 # gap for a slit


# %% Define BEER component list
def getEllStr(E):
    fmt = 'a:{:g}, b:{:g}, ctr:{:g}'
    out = fmt.format(E['a'], E['b'], E['c'])
    return out

def getChopperGuide(num, start, end):
    stre = 'flat expanding, on ellipse '+getEllStr(B.E1)
    g = guide(num, start, end,'chopper guide element', 
              m=[4., 4., 3., 3.], gv=stre)
    return g

BEER = {}

# NBOA
# BEER['W0'] = window('W0', B.nboa_start - 5, thickness=1)
BEER['W0'] = window('W0', B.nboa_start - 5, thickness=1.5)

#BEER['NBOA'] = guide(1, B.nboa_start, B.nboa_end-4-3-1-go, 'monolith insert', 
#    m=[2.5, 2.5, 4., 4.], gv=B.E1)
BEER['NBOA'] = guide(1, B.nboa_start, B.nboa_end, 'monolith insert', 
    m=[2.5, 2.5, 4., 4.], gv=B.E1)

BEER['W1'] = window('W1', B.nboa_end+5-1, thickness=1)
# BEER['NBW'] = window('NBW', B.nboa_end-4, thickness=4) # rev. 1.5, not included !!!
# BBG
BEER['W2'] = window('W2', B.bbg_start-w-2.5, thickness=w)
BEER['BBG'] =  guide(2, B.bbg_start, B.bbg_end, 'bridge beam guide',
    m=[2.5, 2.5, 4., 4.], gv='flat expanding, on ellipse '+getEllStr(B.E1))

BEER['W3'] = window('W3', B.bbg_end+2.5, thickness=w)
BEER['W4'] = window('W4', B.bbg_end + 17.5)

# bi-spectral switch, assumed to be in air before 1st chopper housing
BEER['GSW'] =  switch(3, BEER['W4']['end']+20, m=[3., 3., 0., 0.])

# start of the chopper section
PSC1_dist = 6450
PSC1_width = 200 # width of the PSC1 housing 
# format chopper guide section:
    
BEER['GCA1'] =  getChopperGuide('4-01',BEER['GSW']['end']+20, PSC1_dist-gcg)
BEER['PSC1'] = chopper('PSC1',PSC1_dist, desc='pulse shaping')
BEER['GCA2'] =  getChopperGuide('4-02', PSC1_dist+gcg, PSC1_dist+0.5*PSC1_width-gw)
BEER['W5'] = window('W5', BEER['GCA2']['end']+go)

PSC2_dist = 6850
PSC2_width = 200 # width of the PSC2 housing 
BEER['W6'] = window('W6', PSC2_dist-0.5*PSC2_width)
BEER['GCA3'] =  getChopperGuide('4-03', BEER['W6']['end']+go, PSC2_dist-gcg)
BEER['PSC2'] = chopper('PSC2',PSC2_dist, desc='pulse shaping, variable distance 6650 to 6850')
BEER['GCA4'] =  getChopperGuide('4-04', PSC2_dist+gcg, PSC2_dist+0.5*PSC2_width-gw)
BEER['W7'] = window('W7', BEER['GCA4']['end']+go)

PSC3_dist = 7375
FC1_dist = 8300
BEER['W8'] = window('W8', BEER['W7']['end']+10)
BEER['GCB'] =  getChopperGuide(5, BEER['W8']['end']+go, PSC3_dist-gcg)
BEER['PSC3'] = chopper('PSC3',PSC3_dist, 'pulse shaping', status=False)
BEER['GCC'] =  getChopperGuide(6, PSC3_dist+gcg, FC1_dist-0.5*gc-gcg)
BEER['FC1A'] = chopper('FC1A',FC1_dist-0.5*gc, fmax=14, win=72, desc='WFD')
BEER['FC1B'] = chopper('FC1B',FC1_dist+0.5*gc, fmax=70, win=180, desc='WFD', status=False)
BEER['GCE'] =  getChopperGuide(7, FC1_dist+0.5*gc+gcg, 9300-gcg)
BEER['MCA'] =  chopper('MCA',9300, fmax=280, win='8 x 4', desc='modulation')
BEER['MCB'] =  chopper('MCB',9350, fmax=280, win='16 x 4', desc='modulation', status=False)
BEER['GCF'] =  getChopperGuide(8, 9350+gcg, 9825)
BEER['MCC'] =  chopper('MCC',9875, fmax=280, win='180 + 7 x 4', desc='modulation', status=False)
BEER['GCG'] =  getChopperGuide(9, 9875+gcg, B.curve1_begin-gw-10-gw)
BEER['W9'] = window('W9', B.curve1_begin-gw-10-w)
# end of the chopper section

# Start of the curved guide
# narrow bent guide
# bunker wall:
wall_in=24500 # start of the bunker wall insert
""" NOTE: 
Bunker wall radius is R=28000 TCS (outer pillars), which is 27904.46 ISCS.  
B.curve1_end is set to the bunker radius of 28 m ISCS. 
The wall througput is assumed to end at 28 + 0.3 m TCS, which is 28204.45 ISCS.
We use a rounded value of 28200, until the exact designed value is known.

Upadte ver. 1.5: throughput flange ends at =27999.893 according to the drawings.
Rounded to 28000. The air gaps are set to 5 mm on both sides.
Note that GN2 curvature ends at 27904.46 ISCS, cca 95.5 mm before the end ...

"""
wall_out_calc = B.TCS2ISCS(B.positionAtRadius(28000+300))[0]
# wall_out=28200 # end of the bunker wall insert
wall_out=28000 # update ver. 1.5

BEER['W10'] = window('W10', B.curve1_begin-gw)
BEER['GE1'] =  guide(10, B.curve1_begin, B.E1['c']-g, 
    'NOTE: bent & vertically expanding !', m=[3., 2.5, 3., 3.], RH=1e-6/B.curve1, gv=B.E1)
BEER['GN1'] =  guide(11, B.E1['c'], wall_in-g, 
    ' ', m=[3., 2.5, 2., 2.], RH=1e-6/B.curve1)
BEER['GN2'] =  guide(12, wall_in, wall_out-gw, 
    'bunker wall insert', m=[3., 2.5, 2., 2.], RH=1e-6/B.curve1)
BEER['W11'] = window('W11', wall_out-w)

# shutter (after bunker throughput, length 0.7 m)
# shutter_len = 700
shutter_len = 610 # update ver. 1.5
shutter_start = BEER['W11']['end'] + gsh
BEER['W12'] = window('W12', shutter_start)
BEER['GSH2'] =  guide(13, shutter_start + gw, shutter_start + shutter_len-gw, 
    'shutter insert', m=[2.5, 2.5, 2., 2.])
BEER['W13'] = window('W13', BEER['GSH2']['end'] + go)

""" 
NOTE:
Guide after the shutter starts as soon as possible.
Expansion starts at B.E2_start, which is not necessary the guide entry.
Hence we have to insert a straight element if we want keep the ellipse parameters. 

update ver. 1.5: downstream shutter pit outer dimension is ~ 3260 mm. Hence GE2A should 
end after that, estmate is 300 mm, which sets the end of GE2A to ~ 28000-300+3260+300 = 31260.
This is to be updated with the actual throughput design.     

"""

# shutter_wall=30800 # Assuming shutter wall end at 27700 + 3200 (TCS) = 30804 (ISCS)
shutter_wall=31260 # update ver. 1.5

BEER['W14'] = window('W14', BEER['W13']['end'] + gsh)
# update ver. 1.5, adding straight element
BEER['GE2AS'] =  guide(14,BEER['W14']['end'] + go , B.E2_start-g, 
    'shutter pit insert, parallel', m=[2.5, 2.5, 2., 2.])
BEER['GE2A'] =  guide(14, B.E2_start , shutter_wall-5, 
    'shutter pit insert, elliptic', m=[2.5, 2.5, 2., 2.], gh=B.E2)
BEER['GE2B'] =  guide(15, shutter_wall, B.curve2_begin-g, 
    ' ', m=[2.5, 2.5, 2., 2.], gh=B.E2)

# Transport guide
FC2_dist = 80000
BEER['GT1'] =  guide(16, B.curve2_begin, FC2_dist-0.5*gc-gcg, 
    'transport guide before chopper', m=[2.0, 2.5, 2., 2.], RH=1e-6/B.curve2)
BEER['FC2A'] = chopper('FC2A',FC2_dist-0.5*gc, fmax=14, win=180, 
    desc='WFD, fmax:  14 HZ, window: 180 deg')
BEER['FC2B'] = chopper('FC2B',FC2_dist+0.5*gc, fmax=7, win=90, 
    desc='WFD, fmax:  7 HZ, window: 90 deg', status=False)
BEER['GT2'] =  guide(17, FC2_dist+0.5*gc+gcg, B.curve2_end-g, 
    'transport guide after chopper', m=[2.0, 2.5, 2., 2.], RH=1e-6/B.curve2)

# Focusing guide
slit1_dist=152000
slit2_dist=155000
BEER['GF1'] =  guide(18, B.curve2_end, slit1_dist - 0.5*gsl, 
    ' ', m=[2.5, 2.5, 3., 3.], gv=B.E3)
BEER['SL1'] =  slit('SL1', slit1_dist, 'Adjustable diaphragm')
BEER['GF2'] =  guide(19, slit1_dist + 0.5*gsl, slit2_dist - 0.5*gsl, 
    'L/R mirror only 0 .. 2500 mm, then absorbing', m=[2.5, 2.5, 4., 4.], gv=B.E3)
BEER['SL2'] =  slit('SL2', slit2_dist, 'Adjustable diaphragm')
BEER['W15'] = window('W15', slit2_dist + 0.5*gsl)

# Guide exchanger with focusing guide and collimator
guide_end=157000
BEER['W16'] = window('W16', BEER['W15']['end'] + 10.)
BEER['GEX1'] =  guide('20-01', BEER['W16']['end'] + go, guide_end, 
    'Focusing guide on exchanger', m=[0., 0., 5., 5.], gv=B.E3)
BEER['GEX2'] =  guide('20-02', BEER['W16']['end'] + go, guide_end, 
    'Collimator on exchanger', m=[0., 0., 0., 0.], const = True)
BEER['W17'] = window('W17', BEER['GEX2']['end'] + go)

# Input slit
sample_dist=158000
BEER['SL3'] =  slit('SL3', sample_dist-50, 'Sample input slit, adjustable distance and size')


# table header id strings
hdr = ['ID', 'start', 'end', 'length', 'type', 'name', 'w1', 'w2', 'h1', 'h2', 
       'ctr1', 'ctr2', 'mL', 'mR', 'mT', 'mB', 'geomH', 'geomV', 'comment']

# %% Functions

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
    rec = {}
    for key in hdr:
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
     
def getEntryExit(comp, coord = 'ISCS'):
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

def getGuideData(key, coord = 'ISCS'):
    """Return hash map with strings for component row cells
    """
    comp = BEER[key]
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
    rec['name'] = key
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
    rec['comment'] = comp['desc']
    
    return rec

def getChopperData(key, coord = 'ISCS'):
    """Return hash map with strings for component row cells
    """
    dist =  BEER[key]['start']
    end = BEER[key]['end']
    L = BEER[key]['thickness']   
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
    [w1, h1, w2, h2, c1, c2] = getEntryExit(BEER[key], coord = coord)
    
    
    ctr1 = 0.5*(c1+c2)
    w1 = 0.5*(w1+w2)
    h1 = 0.5*(h1+h2)
    com = ''
    if (not BEER[key]['status']):
        com += 'UPGRADE, '
    com += BEER[key]['desc']
    com += ', fmax={} Hz, win={} deg'.format(BEER[key]['fmax'], BEER[key]['win'])
    
    rec = createRec(dist, BEER[key]['type'])
    rec['ID'] = BEER[key]['id']
    rec['end'] = '{:.1f}'.format(end)
    rec['length'] = '{:.1f}'.format(L)
    rec['name'] = key
    rec['w1'] = '{:.2f}'.format(w1)
    rec['h1'] = '{:.2f}'.format(h1)
    rec['ctr1'] = '{:.2f}'.format(ctr1)
    rec['comment'] = com
    return rec

def getSlitData(key, coord = 'ISCS'):
    """Return hash map with strings for component row cells
    """
    dist =  BEER[key]['start']
    end = BEER[key]['end']
    L = BEER[key]['thickness']
    
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
    com = BEER[key]['desc']
    
    rec = createRec(dist, BEER[key]['type'])
    rec['ID'] = BEER[key]['id']
    rec['end'] = '{:.1f}'.format(end)
    rec['length'] = '{:.1f}'.format(L)
    rec['name'] = key
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

def getWindowData(key, coord = 'FP'):
    """Return hash map with strings for component row cells
    """        
    dist =  BEER[key]['start']
    end = BEER[key]['end']
    L = BEER[key]['thickness']   
    com = BEER[key]['desc']    
    rec = createRec(dist, BEER[key]['type'])
    rec['end'] = '{:.1f}'.format(end)
    rec['length'] = '{:.1f}'.format(L)
    rec['comment'] = com
    return rec

def getGapData(dist1, dist2):
    """Return hash map with strings for component row cells
    """   
    L = dist2-dist1  
    rec = createRec(dist1, 'gap')
    rec['end'] = '{:.1f}'.format(dist2)
    rec['length'] = '{:.1f}'.format(L)
    return rec


def getComponentData(comp, key, coord = 'ISCS'):
    if (comp['type'] == 'optics'):
        row = getGuideData(key, coord = coord)
    elif (comp['type'] == 'slit'):
        row = getSlitData(key, coord = coord)
    elif (comp['type'] == 'chopper'):
        row = getChopperData(key, coord = coord) 
    elif (comp['type'] == 'window'):
        row = getWindowData(key, coord = coord)
    else:
        raise Exception('Unknown component type: {}'.format(comp['type']))
    return row

def writeComponents(coord = 'ISCS', file = '', gaps=False):

    def formatCells(fmt,row):
        cells = []
        for i in range(len(hdr)):
            cells.append(row[hdr[i]])
        ln = fmt.format(* cells)
        return ln
    
    out = '# Generated with BEERcomponents.py\n'
    out += '# Date:\t{}\n'.format(DATE)
    out += '# Version:\t{}\n'.format(VERSION)
    n = len(hdr)
    fmt = '{}'
    fmt += (n-1)*'\t{}'+'\n'
    
    # get table header for output
    header = fmt.format(*hdr)
    out += header
    keys = sortedKeys()
    pre = None
    nwin = 0
    ngap = 0
    dwin = 0.0
    dgap = 0.0
    
    for key in keys:
        comp = BEER[key]       
        row = getComponentData(comp, key, coord = coord)
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
                # don't add gaps after SL3 top the total thickness
                if (key != 'SL3'):
                    ngap += 1
                    dgap += (d2-d1)
                gap = getGapData(d1, d2) 
                ln = formatCells(fmt, gap)
                out += ln
        
        ln = formatCells(fmt, row)
        out += ln
        pre = comp
    if (gaps):
        gap = getGapData(BEER['SL3']['end'], 158000) 
        ln = formatCells(fmt, gap)
        out += ln
    row = getSampleData(158000, coord = coord)
    ln = formatCells(fmt, row)
    out += ln
    if (file != ''):
        f = open(file, 'w')
        f.write(out)
        f.close()
        print('Table written in {}'.format(file))
    print('{} gaps, total thickness = {:.1f} mm'.format(ngap,dgap))
    print('{} windows, total thickness = {:.1f} mm'.format(nwin,dwin))
    return out



# %% CALCULATIONS
    
table=writeComponents(file = 'components_list.txt', gaps=True, coord='FP')

