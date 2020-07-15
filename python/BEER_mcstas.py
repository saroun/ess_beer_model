# -*- coding: utf-8 -*-
"""
Export of McStas configuration file.
Requires template text of the *.instr file.
version: 1.0
Created on Sat Jan 12 10:43:23 2019

@author: Jan Saroun, sarun@ujf.cas.cz
"""


import numpy as np
import BEERgeometry as BG
import BEERcomponents as BC
import BEER_modes as BM
deg = np.pi/180;
indent = '   '
statinfo = False # to include extensions for tracing statistics

# %% Define template file
instrname = 'BEER_primary'
template = instrname+'.instr.template'
inpath = '.\\'
outpath = '.\\'

# %% Functions for collecting info

def infoTilt(key):
    comp = BC.BEER[key]       
    [w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(comp, coord = 'ISCS')    
    length = comp['end']-comp['start']
    angle = np.arctan2(ctr2-ctr1, length)
    info = {}
    mm = 0.001
    info['shift'] = '{:.5f}'.format(ctr1*mm)
    info['angle'] = '{:.4f}'.format(angle/deg)
    return info

def infoMonitor(key, mtype='single'):
    """
    Create info with properties of given component: Monitor.
    
    Arguments:
    ----------
    
    key: str
        component ID after which the monitor is placed
    mtype: str
        monitor type: single (default) or spectrum
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
        
    """
    #comp = BC.BEER[key]
    info = {}
    #mm = 0.001
    info['ID'] = 'mon{}'.format(key)
    info['desc'] = ''
    info['dist'] = '{}.dist + {}.L + 0.001'.format(key,key)
    info['w'] = '{:.4f}'.format(0.1)
    info['h'] = '{:.4f}'.format(0.1)
    info['type'] = mtype
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
    info['dist'] = '{:.4f} - bp_dist'.format(comp['start']*mm)
    info['w'] = '{:.4f}'.format(0.5*(w1+w2)*mm)
    info['h'] = '{:.4f}'.format(0.5*(h1+h2)*mm)
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
    comp = BC.BEER[key]
    [w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(comp, coord = 'ISCS')
    info = {}
    mm = 0.001
    info['ID'] = key
    info['desc'] = comp['desc']
    info['dist'] = '{:.4f} - bp_dist'.format(comp['start']*mm)
    info['start'] = '{:.4f}'.format(comp['start']*mm)
    info['end'] = '{:.4f}'.format(comp['end']*mm)
    info['L'] = '{:.4f}'.format(((comp['end']-comp['start'])*mm))
    info['w1'] = '{:.5f}'.format(w1*mm)
    info['w2'] = '{:.5f}'.format(w2*mm)
    info['h1'] = '{:.5f}'.format(h1*mm)
    info['h2'] = '{:.5f}'.format(h2*mm)
    # note: Guide_gravity has only two m values for horizontal and vertical directions: 
    info['mx'] = '{:g}'.format(comp['m'][0])
    info['my'] = '{:g}'.format(comp['m'][2])
    return info
 

def infoGuideTapering(key, nseg=1, isTilted=False, ellH='', ellV=''):
    """
    Create info with properties of given component: Guide_tapering.
    
    Arguments:
    ----------
    
    key: str
        component ID
    nseg: str
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
    # add additional info
    info['mx'] = '{:g}'.format(comp['m'][0])
    info['my'] = '{:g}'.format(comp['m'][2])
    info['nseg'] = '{:g}'.format(nseg)
    if (isTilted):
        info.update(infoTilt(key))
    if (ellH and ellV):
        raise Exception('{}: Cannot define both horizontal and vertical ellipses.'.format(key))
    if (ellH):
        info['ell'] = {'file':'prof_{}.txt'.format(key), 'ID':ellH, 'dir':0}
    if (ellV):
        info['ell'] = {'file':'prof_{}.txt'.format(key), 'ID':ellV, 'dir':1}
    return info

def infoGuideMultichannel(key, angle=-0.57, blades=150):
    """
    Create info with properties of given component: Guide_multichannel.
    
    Arguments:
    ----------
    
    key: str
        component ID
    angle: str
        rotation angle [deg]
    blades: str
        number of Si blades
        
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
    info['angle'] = '{:.4f}'.format(angle)
    info['nseg'] = '{:g}'.format(blades)
    length = comp['end']-comp['start']
    shift = -0.5*length*0.001*np.tan(angle*deg)
    info['shift'] = '{:.5f}'.format(shift)
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
        
    Return:
    -------
        hash map with items for export to McStas files (e.g. parameter values formatted as strings)
        
    """
    comp = BC.BEER[key]
    RH = comp['RH']*1000 # km to m
    # get basic info from Guide
    info = infoGuide(key)
    # add additional info
    info['mL'] = '{:g}'.format(comp['m'][0])
    info['mR'] = '{:g}'.format(comp['m'][1])
    info['mT'] = '{:g}'.format(comp['m'][2])
    info['mB'] = '{:g}'.format(comp['m'][3])
    info['RH'] = '{:g}'.format(RH)
    # no focusing by default
    info['linh'] = '{:g}'.format(1e5)
    info['linw'] = '{:g}'.format(1e5)
    info['louth'] = '{:g}'.format(1e5)
    info['loutw'] = '{:g}'.format(1e5)
    if (ell):
        info['ell'] = {'ID':ell, 'dir':fdir}
    return info

def infoDChopper(key, win=144, nwin=1):
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
    info = {}
    info['ID'] = key
    info['desc'] = comp['desc']
    info['dist'] = '{:.4f} - bp_dist'.format(0.5*(comp['start']+comp['end'])*0.001)
    info['win'] = '{:.4f}'.format(win)
    info['ns'] = '{:g}'.format(nwin)
    return info


def infoMDChopper(key, wins, ctrs, nwin=1):
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
    info = {}
    info['ID'] = key
    info['desc'] = comp['desc']
    info['dist'] = '{:.4f} - bp_dist'.format(0.5*(comp['start']+comp['end'])*0.001)
    fmt = (nwin-1)*'{:g};'+'{:g}'
    info['wins'] = fmt.format(* wins)
    info['ctrs'] = fmt.format(* ctrs)
    info['ns'] = '{:g}'.format(nwin)
    return info

#%%


def cfgSlit(info, indent):
    ID = info['ID']
    out = ''
    # define guide parameters
    fmt = indent+'{}.{}={};\n'
    # out += indent+'strcpy({}.id, "ID");\n'.format(ID, ID)
    varkeys = ['dist','w', 'h']
    for p in varkeys:
        if (p in info.keys()):
            out += fmt.format(ID, p, info[p])
    return out

def cfgGuideBasic(info, indent):
    ID = info['ID']
    out = ''
    # define guide parameters
    fmt = indent+'{}.{}={};\n'
    # out += indent+'strcpy({}.id, "{}");\n'.format(ID, ID)
    varkeys = ['dist','L', 'w1', 'w2', 'h1', 'h2']
    for p in varkeys:
        if (p in info.keys()):
            out += fmt.format( ID, p, info[p])
    return out

def cfgGuide(info, indent):
    ID = info['ID']
    out = cfgGuideBasic(info, indent)
    # define guide parameters
    fmt = indent+'{}.{}={};\n'
    varkeys = ['mx', 'my']
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
    varkeys = ['mx', 'my', 'nseg', 'shift', 'angle']
    for p in varkeys:
        if (p in info.keys()):
            out += fmt.format(ID, p, info[p])
    # define elliptic profile
    if ('ell' in info.keys()):
        ell = info['ell']
        fmt = '{}writeTaperingFile("{}", {}, {:d}, {}, &{});\n'
        out += fmt.format(indent, ell['file'], ell['ID'], ell['dir'], info['start'], ID)
        fmt = r'{}if (verbose) printf("%s: shift=%g [mm], angle = %g [deg]\n","{}",{}.shift*1000,{}.angle);'
        out += fmt.format(indent, ID, ID, ID) +'\n'
    return out

def cfgGuideMultichannel(info, indent):
    ID = info['ID']
    # get basics from Guide
    out = cfgGuideBasic(info, indent)
    # define additional parameters
    fmt = indent+'{}.{}={};\n'
    varkeys = ['mx', 'my', 'nseg', 'shift', 'angle']
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
    varkeys = ['dist', 'win', 'ns']
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
    return out

#%% Component definitions in TRACE

def statFunction(beam, tab):
    n = len(beam)
    out = ''
    out += '/* Print counting statistics */\n'
    out += 'void printStat() {\n'
    out += tab + 'const int n={:d};\n'.format(n)
    out += tab + 'double eff[n], effRel[n]; // efficiencies absolute and relative\n'
    out += tab + 'double sum, sumPre;\n'
    out += tab + 'int i;\n'
    out += tab + 'long cnt;\n'
    out += tab + 'FILE *hfile;\n'
    out += tab + 'sum = srccount;\n'
    out += tab + 'sumPre = sum;\n'
    out += tab + 'for (i=0;i<n;i++) {\n'
    out += 2*tab + 'cnt = stats[i].cnt;\n'
    out += 3*tab + 'if  (cnt>0) {\n'
    out += 3*tab + 'eff[i] = cnt/sum;\n'
    out += 3*tab + 'effRel[i] = cnt/sumPre;\n'
    out += 3*tab + 'sumPre = cnt;\n'
    out += 2*tab + '}\n'
    out += tab + '}\n'
    out += tab + 'hfile=fopen("statistics.txt","w");\n'
    hdr = r'"Counting statistics [ID, counts, eff_rel, eff]:\n"'
    out += tab + 'printf('+hdr+');\n'
    out += tab + 'if (hfile) fprintf(hfile, '+hdr+');\n'
    out += tab + 'for (i=0;i<n;i++) {\n'
    out += 2*tab + 'if  (stats[i].cnt>0) {\n'
    out += 3*tab + r'printf("%s:\t%ld\t%g\t%g\n",stats[i].id, stats[i].cnt, effRel[i], eff[i]);'+'\n'
    out += 3*tab + r'if (hfile) fprintf(hfile, "%s:\t%ld\t%g\t%g\n",stats[i].id, stats[i].cnt, effRel[i], eff[i]);'+'\n'
    out += 2*tab + '}\n'
    out += tab + '}\n'
    out += tab + 'if (hfile) fclose(hfile);\n'
    out += '}\n'
    return out


def extStatistics(comp, indent):
    i = beam.index(comp)
    out = 'EXTEND\n%{\n'
    out += '{}if (p>0) stats[{:d}].cnt++;\n'.format(indent,i)
    out += '%}\n'
    return out

def compMonitor(info, relto='BPArm'):
    """
     Place simple monitor after given component
    """
    tab = '\t'
    ID = info['ID']
    if (info['type']=='spectrum'):
        fmt = 'COMPONENT @C = L_monitor(filename="@C.dat", xwidth = 0.1, yheight = 0.1, restore_neutron = 1,\n'
        fmt += tab + 'nL = 80, Lmin = 0.2, Lmax = 8.2)\n'
    else:
        fmt = 'COMPONENT @C = Monitor(xwidth = 0.1, yheight = 0.1, restore_neutron = 1)\n'
    out = fmt.replace('@C',ID)
    fmt = 'AT (0, 0, {}) RELATIVE {}\n'
    out += fmt.format(info['dist'], relto)
    return out


def compSlit(info, relto='BPArm'):
    ID = info['ID']
    fmt = 'COMPONENT c@C = Slit(xwidth = @C.w, yheight = @C.h)\n'
    out = fmt.replace('@C',ID)
    fmt = 'AT (0, 0, {}.dist) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    return out
        
def compGuide(info, relto='BPArm'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c@C = Guide_gravity(\n'.replace('@C',ID)
    fmt = 'l = @C.L, w1 = @C.w1, h1 = @C.h1, w2 = @C.w2, h2 = @C.h2,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'alpha = m_alpha, Qc = m_Qc, W = m_W,\n'.replace('@C',ID)
    out += tab+fmt.replace('@C',ID)
    fmt = ' mleft = @C.mx, mright = @C.mx, mtop = @C.my, mbottom = @C.my\n'.replace('@C',ID)
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    fmt = 'AT (0, 0, {}.dist) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    return out
        
def compDChopper(info, relto='BPArm'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c@C = DiskChopper(\n'.replace('@C',ID)
    fmt = 'theta_0 = @C.win, radius = @C.R, yheight = @C.h, nu = @C.nu,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'nslit = @C.ns, phase = @C.phase\n'
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    fmt = 'AT (0, 0, {}.dist) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    fmt = 'ROTATED (0, {}.flip*180, 0) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    return out

def compMDChopper(info, relto='BPArm'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c@C = MultiDiskChopper(\n'.replace('@C',ID)
    fmt = 'radius = @C.R, delta_y = 0.5*@C.h - @C.R, nu = @C.nu,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'nslits = @C.ns, phase = @C.phase, abs_out=0,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'slit_width = @C.wins, slit_center = @C.ctrs\n'
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    fmt = 'AT (0, 0, {}.dist) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    return out
    
def compGuideTapering(info, relto='BPArm'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c@C = Guide_tapering(\n'.replace('@C',ID)
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
    fmt = tab+'alphax = m_alpha, alphay = m_alpha, Qcx = m_Qc, Qcy = m_Qc, W = m_W,\n'
    out += fmt.replace('@C',ID)
    fmt = tab+'mx = @C.mx, my = @C.my, segno = @C.nseg\n'
    out += fmt.replace('@C',ID)    
    out += ')\n'
    fmt = 'AT ({}.shift, 0, {}.dist) RELATIVE {}\n'
    out += fmt.format(ID, ID, relto)
    fmt = 'ROTATED (0, {}.angle, 0) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    return out
  
def compGuideMultichannel(info, relto='BPArm'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c@C = Guide_multichannel(\n'.replace('@C',ID)
    fmt = 'l = @C.L,w1 = @C.w1, h1 = @C.h1, w2 = @C.w2, h2 = @C.h2, \n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'alphax = m_alpha, alphay = m_alpha, Qcx = m_Qc, Qcy = m_Qc, W = m_W, dlam = @C.dlam,\n'
    out += tab+fmt.replace('@C',ID)
    fmt = 'mx = @C.mx, my = @C.my, nslit = @C.nseg+1, mater = "Si"\n'
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    fmt = 'AT ({}.shift, 0, {}.dist) RELATIVE {}\n'
    out += fmt.format(ID, ID, relto)
    fmt = 'ROTATED (0, {}.angle, 0) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    return out

def compEGuideGravity(info, relto='BPArm'):
    ID = info['ID']
    tab = '\t'
    out = 'COMPONENT c@C = Elliptic_guide_gravity(\n'.replace('@C',ID)
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
    fmt = 'R0 = 0.99, Qc = m_Qc, alpha = m_alpha, W = m_W\n'
    out += tab+fmt.replace('@C',ID)
    out += ')\n'
    if ('when' in info.keys()):
        out += 'WHEN ({} = 1) '.format(info['when'])
    fmt = 'AT (0, 0, {}.dist) RELATIVE {}\n'
    out += fmt.format(ID, relto)
    return out

# %% Fuctions for adding components

listGuide = []
listSlit = []
listGuideTapering = []
listGuideMultichannel = []
listEGuideGravity = []
listDChopper = []
listMDChopper = []

# define types:
TMonitor='TMonitor'
TSlit='TSlit'
TGuide='TGuide'
TGuideTA='TGuideTA'
TGuideMC='TGuideMC'
TGuideEG='TGuideEG'
TCDisc='TCDisc'
TMDChopper='TMDChopper'


def addMonitor(beam, key, mtype='single'):
    """
    Add monitor after the component with ID=key
    """
    item = {'info': infoMonitor(key, mtype=mtype), 'type':TMonitor}
    beam.append(item)
    #listSlit.append(item)
    
def addSlit(beam, key):
    item = {'info': infoSlit(key), 'type':TSlit}
    beam.append(item)
    listSlit.append(item)

def addGuide(beam, key):
    item = {'info': infoGuide(key), 'type':TGuide}
    beam.append(item)
    listGuide.append(item)

def addGuideTapering(beam, key, **kwargs):
    item = {'info': infoGuideTapering(key, **kwargs), 'type':TGuideTA}
    beam.append(item)
    listGuideTapering.append(item)

def addGuideMultichannel(beam, key, **kwargs):
    item = {'info': infoGuideMultichannel(key, **kwargs), 'type':TGuideMC}
    beam.append(item)
    listGuideMultichannel.append(item)

def addEGuideGravity(beam, key, when='', **kwargs):
    item = {'info': infoEGuideGravity(key, **kwargs), 'type':TGuideEG}
    if (when):
        item['info']['when'] = when 
    beam.append(item)
    listEGuideGravity.append(item)
    
def addDChopper(beam, key, **kwargs):
    item = {'info': infoDChopper(key, **kwargs), 'type':TCDisc}
    beam.append(item)
    listDChopper.append(item)
    
def addMDChopper(beam, key, **kwargs):
    item = {'info': infoMDChopper(key, **kwargs), 'type':TMDChopper}
    beam.append(item)
    listMDChopper.append(item)

def cfgComponent(comp, indent='    '):
    typ = comp['type']
    info = comp['info']
    out = ''
    if (typ==TSlit):
        out += cfgSlit(info, indent)
    elif (typ==TGuide):
        out += cfgGuide(info, indent)
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

def traceComponent(comp, relto='BPArm'):
    typ = comp['type']
    info = comp['info']
    out = ''
    if (typ==TSlit):
        out += compSlit(info, relto)
    elif (typ==TMonitor):
        out += compMonitor(info, relto)    
    elif (typ==TGuide):
        out += compGuide(info, relto)
    elif (typ==TGuideTA):
        out += compGuideTapering(info, relto)
    elif (typ==TGuideMC):
        out += compGuideMultichannel(info, relto)
    elif (typ==TGuideEG):
        out += compEGuideGravity(info, relto)
    elif (typ==TCDisc):
        out += compDChopper(info, relto)
    elif (typ==TMDChopper):
        out += compMDChopper(info, relto)        
    return out



def clearLists():
    listGuide.clear()
    listSlit.clear()
    listGuideTapering.clear()
    listGuideMultichannel.clear()
    listEGuideGravity.clear()
    listDChopper.clear()


# %% Define BEER instrument components
clearLists()
# Add Monolith section    
beamMonolith = []
addGuideTapering(beamMonolith,'NBOA', nseg=1, isTilted=True, ellV='ellV1')
addMonitor(beamMonolith,'NBOA', mtype='spectrum')
addGuideTapering(beamMonolith,'BBG', nseg=1, isTilted=True, ellV='ellV1')
addMonitor(beamMonolith,'BBG')
# Add Bunker section
beamBunker = []
addGuideMultichannel(beamBunker,'GSW', angle=-0.57, blades=150)
addMonitor(beamBunker,'GSW')
addGuide(beamBunker,'GCA1')
addDChopper(beamBunker, 'PSC1', win=144, nwin=1)
addGuide(beamBunker,'GCA2')
addGuide(beamBunker,'GCA3')
addDChopper(beamBunker, 'PSC2', win=144, nwin=1)
addGuide(beamBunker,'GCA4')
addGuide(beamBunker,'GCB')
addDChopper(beamBunker, 'PSC3', win=144, nwin=1)          
addGuide(beamBunker,'GCC')
addDChopper(beamBunker, 'FC1A', win=72, nwin=1)      
addDChopper(beamBunker, 'FC1B', win=180, nwin=1) 
addGuide(beamBunker,'GCE')
addMonitor(beamBunker,'GCE')
addDChopper(beamBunker, 'MCA', win=4, nwin=8)      
addDChopper(beamBunker, 'MCB', win=4, nwin=16) 
addGuide(beamBunker,'GCF')
addMonitor(beamBunker,'GCF')
addMDChopper(beamBunker, 'MCC', 
             wins=[180, 4, 4, 4, 4, 4, 4, 4], 
             ctrs=[0, 180-3*22.5, 180-2*22.5, 180-1*22.5, 180, 180+1*22.5, 180+2*22.5, 180+3*22.5], 
             nwin=8)
addGuide(beamBunker,'GCG')
addMonitor(beamBunker,'GCG')
addEGuideGravity(beamBunker, 'GE1', ell='ellV1', fdir=1)
addEGuideGravity(beamBunker, 'GN1')
addEGuideGravity(beamBunker, 'GN2')
addMonitor(beamBunker,'GN2', mtype='spectrum')


# Add Transport section
beamTransport = []
addGuide(beamTransport,'GSH2')
addMonitor(beamTransport,'GSH2')
addEGuideGravity(beamTransport, 'GE2A', ell='ellH1', fdir=0)
addEGuideGravity(beamTransport, 'GE2B', ell='ellH1', fdir=0)
addMonitor(beamTransport,'GE2B')
addEGuideGravity(beamTransport, 'GT1')
addMonitor(beamTransport,'GT1', mtype='spectrum')
addDChopper(beamTransport, 'FC2A', win=180, nwin=1)      
addDChopper(beamTransport, 'FC2B', win=90, nwin=1) 
addEGuideGravity(beamTransport, 'GT2')
addMonitor(beamTransport,'GT2')

# Add Focusing section
beamFocusing = []
addEGuideGravity(beamFocusing, 'GF1', ell='ellV2', fdir=1)
addMonitor(beamFocusing,'GF1')
addSlit(beamFocusing, 'SL1')
addEGuideGravity(beamFocusing, 'GF2', ell='ellV2', fdir=1)
addMonitor(beamFocusing,'GF2')
addSlit(beamFocusing, 'SL2')
addEGuideGravity(beamFocusing, 'GEX1', ell='ellV2', fdir=1, when='GF3On')
addMonitor(beamFocusing,'GEX1')
addSlit(beamFocusing, 'SL3')

beam = []
beam.extend(beamMonolith)
beam.extend(beamBunker)
beam.extend(beamTransport)
beam.extend(beamFocusing)

# %%


def cfgBeam(beam, comment):
    out = '\n/*'+50*'-'+'\n'
    out += '{}\n'.format(comment)
    out += 50*'-'+'*/\n'
    for comp in beam:
        # print(comp['info']['ID'])
        if (comp['type'] != TMonitor):
            info = comp['info']
            out += '\n'
            out += '/* {}: {}*/\n'.format(comp['info']['ID'], info['desc'])
            out += cfgComponent(comp, indent)
            # out += 'comp[{:d}] = &{};\n'.format(i,comp['info']['ID'])
            i = beam.index(comp);
            ID = comp['info']['ID']
            out += indent + '{}.idx = {:d};\n'.format(ID, i)
            out += indent + 'addComponent("{}");\n'.format(info['ID'])
    return out

def reportBeam(beam, comment, indent):
    fmt = '\n'+indent+'/* {}*/\n'
    out = fmt.format(comment)
    fmt = indent+'report{}("{}", {});\n'
    for comp in beam:
        if (comp['type'] != TMonitor):
            ID = comp['info']['ID']
            out += fmt.format(comp['type'],ID,ID)
    out +='\n'
    return out


def declaretype(listC):
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

        
def traceBeam(beam, comment):
    out = '\n/*'+50*'-'+'\n'
    out += '{}\n'.format(comment)
    out += 50*'-'+'*/\n'
    for comp in beam:
        # print(comp['info']['ID'])
        info =  comp['info'] 
        out += '\n'
        out += '/* {}: {}*/\n'.format(info['ID'], info['desc'])
        out += traceComponent(comp, relto='BPArm')
        if (statinfo): out += extStatistics(comp, indent)
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

def initPrimary():
    out = cfgBeam(beamMonolith, 'Monolith section')
    out += cfgBeam(beamBunker, 'Bunker section')
    out += cfgBeam(beamTransport, 'Transport section')
    out += cfgBeam(beamFocusing, 'Focusing section')
    return out

def modesChoppers(indent):
    out = '\n// Define frequencies for resolution choppers \n'
    out += indent+'double mod_PSC1_nu[] = {'+BM.getChopperStr('PSC1')+ '};\n' 
    out += indent+'double mod_PSC2_nu[] = {'+BM.getChopperStr('PSC2')+ '};\n'
    out += indent+'double mod_PSC3_nu[] = {'+BM.getChopperStr('PSC3')+ '};\n'
    out += indent+'double mod_MCA_nu[] = {'+BM.getChopperStr('MCA')  + '};\n'
    out += indent+'double mod_MCB_nu[] = {'+BM.getChopperStr('MCB')  + '};\n'
    out += indent+'double mod_MCC_nu[] = {'+BM.getChopperStr('MCC')  + '};\n'
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
    out = '\n// Define focusingg guide setting [on/off]  \n'
    out += indent+'int mod_GF3[] = {'+BM.getGEXStr() + '};\n' 
    return out

def modesPSC2dist(indent):
    out = '\n// Define distance of the PSC2 chopper  \n'
    out += indent+'double mod_PSC2dist[] = {'+BM.getPSC2distStr() + '};\n' 
    return out


def modes(indent):
    out = modesLegend()
    out += modesSlits(indent)
    out += modesChoppers(indent)
    out += modesFChoppers(indent)
    out += modesGEX1(indent)
    out += modesPSC2dist(indent)
    out += '\n// Chopper modes  \n'
    out += indent+'int mod_cmodes[] = {'+BM.getCmodesStr() + '};\n'
    out += indent+'int mod_wmodes[] = {'+BM.getWmodesStr() + '};\n'
    return out
    return out

def modesLegend():
    out = '\n/*'+50*'-'+'\n'
    out += 'Define reference operation modes \n'
    out += 50*'-'+'\n'
    for i in range(len(BM.modes)):
        m = BM.modes[i]
        out += '{}\t{}\t{}\t{}\n'.format(i, m['ID'], m['label'], m['comment'])
    out += 50*'-'+'*/\n'
    return out

def initReports():
    out = reportBeam(beamMonolith, 'Monolith section', indent+indent)
    out += reportBeam(beamBunker, 'Bunker section', indent+indent)
    out += reportBeam(beamTransport, 'Transport section', indent+indent)
    out += reportBeam(beamFocusing, 'Focusing section', indent+indent)
    return out

def declarePrimary():  
    out = "\n/* Component declarations */\n"
    out += declaretype(listSlit)
    out += declaretype(listGuide)
    out += declaretype(listEGuideGravity)
    out += declaretype(listGuideMultichannel)
    out += declaretype(listGuideTapering)
    out += declaretype(listDChopper)
    out += declaretype(listMDChopper)
    out += indent + 'TStat stats[{:d}];\n'.format(len(beam))
    out += '\n'
    return out

def tracePrimary():
    out = traceBeam(beamMonolith, 'Monolith section')
    out += traceBeam(beamBunker, 'Bunker section')
    out += traceBeam(beamTransport, 'Transport section')
    out += traceBeam(beamFocusing, 'Focusing section')
    return out

def parseTemplate(outfile):
    out = ''
    declare = declarePrimary()
    init = initPrimary()
    trace = tracePrimary()
    ell = ellipses(indent)
    rep = initReports()
    mymodes = modes(indent)
    with open(inpath+template, 'r') as fi:
        lines = fi.readlines()
    for i in range(len(lines)):
        line = lines[i]
        k = line.find('@')
        if (k>=0):
            line = line.replace('@DECLARE_PRIMARY', declare)
            if (line.find('@')>-1): line = line.replace('@INIT_PRIMARY', init)
            if (line.find('@')>-1): line = line.replace('@MODES', mymodes)
            if (line.find('@')>-1): line = line.replace('@TRACE_PRIMARY', trace)
            if (line.find('@')>-1): line = line.replace('@ELLIPSES', ell)
            if (line.find('@')>-1): line = line.replace('@REPORT', rep)
            if (line.find('@')>-1): line = line.replace('@VERSION', BC.VERSION)
            if (line.find('@')>-1): line = line.replace('@DATE', BC.DATE)
            if (line.find('@')>-1): line = line.replace('@TEMPLATE', template)
            if (line.find('@')>-1): line = line.replace('@SOURCE', 'BEER_mcstas.py')
            if (line.find('@')>-1): line = line.replace('@NAME', instrname)
            if (line.find('@')>-1): 
                if statinfo:
                    line = line.replace('@STATFNC', statFunction(beam, indent))
                else:
                    line = line.replace('@STATFNC', '')
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
    fi.close()
    with open(outfile, 'w') as fo:
        lines = fo.write(out)
    fo.close()
 
# %%
    
# parse template 

parseTemplate(outpath+instrname+'.instr')


    