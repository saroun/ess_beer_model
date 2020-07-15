# -*- coding: utf-8 -*-
"""
Export of SIMRES configuration scripts
version: 1.4
Date: October 13, 2018, 2018

@author: J. Saroun, saroun@ujf.cas.cz
"""

import numpy as np
import BEERgeometry as BG
import BEERcomponents as BC
deg = np.pi/180;

# %%


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
    #data = BC.getComponentData(comp, key, coord = 'ISCS')
    [w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(comp, coord = 'ISCS')    
    #ctr1 = float(data['ctr1'])
    #ctr2 = float(data['ctr2'])
    length = comp['end']-comp['start']
    angle = np.arctan2(ctr2-ctr1, length)
    info = {}
    info['shift'] = '{:.2f}'.format(ctr1)
    info['angle'] = '{:.4f}'.format(angle/deg)
    return info
        
def infoGUIDE(key, key0=None):
    comp = BC.BEER[key]       
    data = BC.getComponentData(comp, key, coord = 'ISCS')
    L0 = getPreviousDistance(key0)
    ID = data['name']
    L = comp['start'] - L0
    rho = [0., 0.]
    RH = comp['RH']
    RV = comp['RV']
    if (RH != 0):
        rho[0] =  1e-3/RH
    if (RV != 0):
        rho[1] =  1e-3/RV
    info = {}
    info['ID'] = ID
    info['DIST'] = '{:.1f}'.format(L)
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
    data = BC.getComponentData(comp, key, coord = 'ISCS')
    L0 = getPreviousDistance(key0)
    ID = data['name']
    L = comp['start'] - L0
    if (comp['type'] == 'chopper' or comp['type'] == 'slit'):
        L += 0.5*comp['thickness']
    dist='SET {} DIST {:.1f}\n'
    out ='# '+ID+'\n'
    out += dist.format(ID, L)
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
    out += cfgDist('PSC1', key0='GCA1' )
    out += cfgGUIDE('GCA2', key0='PSC1' )
    out += cfgGUIDE('GCA3', key0='GCA2' )
    out += cfgDist('PSC2', key0='GCA3' )
    out += cfgGUIDE('GCA4', key0='PSC2' )
    out += cfgGUIDE('GCB', key0='GCA4' )
    out += cfgDist('PSC3', key0='GCB' )
    out += cfgGUIDE('GCC', key0='PSC3' )
    out += cfgDist('FC1A', key0='GCC' )
    out += cfgDist('FC1B', key0='FC1A' )
    out += cfgGUIDE('GCE', key0='FC1B' )
    out += cfgDist('MCA', key0='GCE' )
    out += cfgDist('MCB', key0='MCA' )
    out += cfgGUIDE('GCF', key0='MCB' )
    out += cfgDist('MCC', key0='GCF' )
    out += cfgGUIDE('GCG', key0='MCC' )
    out += '\n'
    return out

def cfgBunkerSection():
    out = sectionHeader('Bunker section')
    out += cfgSGUIDE('GE1', seg = 500., key0='GCG')
    out += cfgSGUIDE('GN1', seg = 500., key0='GE1')
    out += cfgSGUIDE('GN2', seg = 500., key0='GN1')
    out += cfgGUIDE('GSH2', key0='GN2')
    out += '\n'
    return out

def cfgTransportSection():
    out = sectionHeader('Transport section')
    out += cfgSGUIDE('GE2A', seg = 1000., key0='GSH2')
    out += cfgSGUIDE('GE2B', seg = 1000., key0='GE2A')
    out += cfgSGUIDE('GT1', seg = 2000., key0='GE2B')
    out += cfgDist('FC2A', key0='GT1' )
    out += cfgDist('FC2B', key0='FC2A' )
    out += cfgSGUIDE('GT2', seg = 2000., key0='FC2B')
    out += '\n'
    return out

def cfgFocusingSection():
    out = sectionHeader('Focusing section')
    #seg = 5*[1000.] + 5*[500.]
    seg = 10*[500.] + 10*[250.]
    out += cfgSGUIDE('GF1', seg = 500., key0='GT2')
    out += cfgDist('SL1', key0='GF1')
    #seg = 4*[500.] + 4*[250.]
    #seg = 8*[250.] + 8*[125.]
    seg = 6*[500.]
    m = BC.BEER['GF2']['m']
    segm = 5*[m] + 1*[[0., 0., m[2], m[3]]]
    out += cfgSGUIDE('GF2', seg = seg, segm = segm, key0='SL1')
    out += cfgDist('SL2', key0='GF2')
    seg = 8*[200.] + 4*[100.]
    out += cfgSGUIDE('GEX1', seg = 250., key0='SL2')
    out += cfgDist('SL3', key0='GEX1')
    out += '\n'
    return out


# %%
#seg = 4*[500.] + 3*[1000.]
#sgm = infoSegments('GE1', seg = seg)
#print(sgm)

#out = cfgSGUIDE('GE1', seg = seg, key0='GCG')
#print(out)

# %%
out = cfgMonolithSection()
out += cfgChopperSection()
out += cfgBunkerSection()
out += cfgTransportSection()
out += cfgFocusingSection()

with open('simres_setup.inp', 'w') as f:
    f.write(out)
    f.close()




