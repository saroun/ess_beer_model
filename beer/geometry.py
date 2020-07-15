# -*- coding: utf-8 -*-
"""
Module for calculation of BEER beam axis and beam profile, utilities
for coordinate conversions and plotting of beam profile.

Created on Tue Oct 10 10:49:35 2017
@author: J. Saroun, saroun@ujf.cas.cz
Copyright (c) 2020 Nuclear Physics Institute, CAS, Rez


update 2019-06-21: 
    getSlice() and printSlice() give correct x-coordinate, not just the given distance 
    Added printSliceCal() to calculate and print slice in one command
    
update 2019-08-27:
    Updated true distances of optical components according to the detailed design.
    Geometry of the beam and optical surfaces remains unchanged.
    
update 2020-03-04:
    Moved to submodule and renamed from BEERgeometry.py.
    Updated doc texts 
    
update 2020-05-11:
    Updated according to the final CAD model submitted to TG3 review.
    Only a cleanup. Geometry of the beam and optical surfaces did not change.
"""


import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import fsolve
deg = np.pi/180;

# set default plot properties
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (8, 4),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
plt.rcParams.update(params)

# %% Useful functions

def ell(dist, E):
    """Calulate an ellipse profile for given distance and ellipse parameters.
    """
    n = np.size(dist)
    dist =  np.array(dist).reshape(n,)
    D = np.array(1.0 - ((dist - E['c'])/E['a'])**2)
    y = np.zeros(n)
    idx = np.where(D > 0)
    y[idx] = 2*E['b']*np.sqrt(D[idx])
    return y

def getRotationZ(omega):
    """ Generate rotation matrix for z-axis """
    s, c = np.sin(omega), np.cos(omega)
    R = np.array([[c, -s, 0.], [s, c, 0.], [0., 0., 1.]])
    return R

    
# %% Beamport definition
# ref. to https://confluence.esss.lu.se/display/SPD/Guidance+on+ISCS+and+Focal+Points
"""
To avoid confusion about coordinate systems: 

ISCS origin is shifted by -30 mm from the West moderator focal point (i.e. towards CSPEC) in direction normal 
to the beamport axis FP_x (aiming at 144.7 deg from the focal point). 

ISCS x-axis (= BEER optical axis) has the angle 144.7 + 0.3 deg from TCS_x.  

FP coordinates are defined with origin at the moderator focal point and x-axis angle equal to the beamport angle.
"""

# W2 Angle 
theta = 144.7*deg
# moderator focal point in TCS coordinates
rm = [-54., 89., 137.]

# ISCS coordinates vs. moderator focal point 
alpha = 0.3*deg
rc = [0., -30., 0.]

# 
"""
Primary coordinate system:
--------------------------
Choose either ISCS or FP as the primary coordinates system. This defines
reference frame in which you define following primary parameters, such as 
distance from the source or distance (y-coord) from the x-axis. It also defines 
the axis of symmetry for ellipses, i.e. either FP_x or ISCS_x.
There is a tiny difference between physical profiles defined in these two 
reference frames (e.g. ~ 2 mm in the sample distance or ~ 0.13 mm in the distance 
of the entry to the first curved section.) 
"""

_COORD='ISCS'

# %% USER INPUT - primary parameters
# NOTE: these numbers may be updated during detailed design ...

"""
Definition of beam axis
-------------------------
Give curvatures and distances (x-coordinates) of the curved sections.
"""
# curvature 1
curve1 = -1./2e6  # curvature 1 [1/mm]
curve1_begin = 10000.0  # begin from FP centre [mm]
curve1_end = 28000.0   # end from FP centre [mm]
# curvature 2
curve2 = 1./2e7  # curvature 2 [1/mm]
curve2_begin = 39000.0   # begin from FP centre [mm]
curve2_end = 144500.0  # end from FP centre [mm]

"""
Definition of beam profile parameters
-------------------------------------

Elliptic profiles:
a = long semi axis
b = short semi axis
c = centre distance along x
"""
# Vertical ellipse, NBOA + up to 15 m 
E1 = {'a':14423, 'b':40, 'c':15000}

""" Horizontal, expansion after the bunker
"a" is defined so that the width starts expanding from 20 mm at E2_start to 
40 mm at curve2_begin
E2_start should equal to the actual start of the expanding section after 
the shutter, but we fix it at the rounded value of 29 m so that it is 
independent of the shutter design changes. 
"""
E2_start = 29000 
E2_a = (curve2_begin - E2_start)/np.sqrt(1.0 - (20.0/40)**2)

E2 = {'a':E2_a, 'b':20, 'c':curve2_begin}

# Vertical, focusing guide 
E3 = {'a':13484, 'b':40, 'c':curve2_end}

"""
Feeder horizontal geometry:
--------------------------    
start:    entry distance along x
end:      distance where the feader reaches the 22 mm width (should be at the exit from BBG)
langle:   angle [deg] of the left wall rel. to ISCS_x
rangle:   angle [deg] of the right wall rel. to ISCS_x
exit:     exit width (should be 22 mm at the exit from BBG)

NOTE: this is just a geometry description. 
Real component can have different distance/length and hence also widths, 
but it must follow these walls.
"""
# Helper: caculate angles from entry wall positions and distances
#aleft=-np.arctan2(67.5 - 11, 3877.0)
#aright=-np.arctan2(-17.5 + 11, 3877.0)
#feeder = {'start':2026, 'end':5903, 'langle':aleft, 'rangle':aright, 'exit':22.0}

aleft=-np.arctan2(67.5 - 11, 5894-2026)
aright=-np.arctan2(-17.5 + 11, 5894-2026)
feeder = {'start':2026, 'end':5894, 'langle':aleft, 'rangle':aright, 'exit':22.0}

"""
Actual distances of NBOA and BBG faces
"""
# Start of NBOA as designed
nboa_start = 2030.5

# End of NBOA as designed (end of 4 mm window)
# nboa_end = 5404.42
nboa_end = nboa_start + 3361.5 # revision 1.5 according to design

# End of BBG as designed
# This should be the 22 mm wide window at the exit from BBG (0.5 mm window end)
#bbg_end = 5896.92
bbg_end = 5893.843 # revision 1.5 according to design

# Start of BBG as designed (start of 0.5 mm window)
# bbg_start = bbg_end - 489.00
bbg_start = 5410.843 # revision 1.5 according to design

#%% Derived parameters

# convert feeder wall angles to required _COORD
if (_COORD=='FP'):
    feeder['langle'] += alpha
    feeder['rangle'] += alpha


"""
# no more used ...

feeder_angle = 0.5*(feeder['langle']+feeder['rangle'])
feeder_length = feeder['end'] - feeder['start']
# NBOA y-coordinates of the left and right wall at the feeder entry
feeder_entry_left = 0.5*feeder['exit'] - feeder_length*np.tan(feeder['langle'])
feeder_entry_right = -0.5*feeder['exit'] - feeder_length*np.tan(feeder['rangle'])
feeder_entry_width = feeder_entry_left - feeder_entry_right
feeder_entry_ctr =  0.5*(feeder_entry_left + feeder_entry_right)

# NBOA parameters
nboa_length = nboa_end - nboa_start
nboa_entry_left = 0.5*feeder['exit'] - (feeder['end'] - nboa_start)*np.tan(feeder['langle'])
nboa_entry_right = -0.5*feeder['exit'] - (feeder['end'] - nboa_start)*np.tan(feeder['rangle'])
nboa_entry_width = nboa_entry_left - nboa_entry_right
nboa_exit_left = 0.5*feeder['exit'] - (feeder['end'] - nboa_end)*np.tan(feeder['langle'])
nboa_exit_right = -0.5*feeder['exit'] - (feeder['end'] - nboa_end)*np.tan(feeder['rangle'])
nboa_exit_width = nboa_exit_left - nboa_exit_right

# BBG parameters
bbg_length = bbg_end - bbg_start
bbg_entry_left = 0.5*feeder['exit'] - (feeder['end'] - bbg_start)*np.tan(feeder['langle'])
bbg_entry_right = -0.5*feeder['exit'] - (feeder['end'] - bbg_start)*np.tan(feeder['rangle'])
bbg_entry_width = bbg_entry_left - bbg_entry_right
bbg_exit_left = 0.5*feeder['exit'] - (feeder['end'] - bbg_end)*np.tan(feeder['langle'])
bbg_exit_right = -0.5*feeder['exit'] - (feeder['end'] - bbg_end)*np.tan(feeder['rangle'])
bbg_exit_width = bbg_exit_left - bbg_exit_right
"""

# Rotation matrix ISCS vs. TCS 
Rot = getRotationZ(theta + alpha)

# Rotation matrix FP vs. TCS 
RotW2 = getRotationZ(theta)

# Get ISCS centre in TCS coord.
T = np.array(rm) + RotW2.dot(np.array(rc))

# Critical points: start/end of the curved sections and associated deflections
#if (_COORD=='ISCS'):
#    c0_begin = [0., rc[1], 0.]
#    c0_angle = np.arctan(alpha)
#elif (_COORD=='FP'):

#else:
#    raise Exception('_COORD setting not supported: {}'.format(_COORD))

c0_begin = [0., 0., 0.]
c0_angle = 0.    
c0_delta = c0_begin[1] + c0_angle*curve1_begin

dx = curve1_end - curve1_begin
c1_begin = [curve1_begin, c0_delta, 0.]
c1_angle = c0_angle + curve1*dx
c1_delta = c1_begin[1] + 0.5*curve1*dx**2 + c0_angle*dx
c1_end = [curve1_end, c1_delta, 0.]

dx = curve2_end - curve2_begin
c2_begin = [curve2_begin, c1_delta + c1_angle*(curve2_begin - curve1_end), 0.]
c2_angle = c1_angle + curve2*dx
c2_delta = c2_begin[1] + 0.5*curve2*dx**2 + c1_angle*dx
c2_end = [curve2_end, c2_delta, 0.]


# %% Coordinate transformations

def ISCS2TCS(r):
    """Convert positions from ISCS to TCS coordinates
    
    Arguments
    ---------
        r    array
            positions, one row per point Carthesian coordinates in ISCS
            
    NOTE: ISCS refers to the thermal beam axis starting at -30 mm and +0.3 deg from the moderator focal point ...
    """
    r1 = Rot.dot(r.T)
    return r1.T + T

def ISCS2FOC(r):
    """Convert positions from ISCS to FP coordinates
    
    Arguments
    ---------
        r    array
            positions, one row per point Carthesian coordinates in ISCS
            
    NOTE: ISCS refers to the thermal beam axis starting at -30 mm and +0.3 deg from the moderator focal point ...
    """
    r1 = ISCS2TCS(r)
    r2 = TCS2FOC(r1)
    return r2

def FOC2ISCS(r):
    """Convert positions from FP to ISCS coordinates
    
    Arguments
    ---------
        r    array
            positions, one row per point Carthesian coordinates in FP
            
    NOTE: ISCS refers to the thermal beam axis starting at -30 mm and +0.3 deg from the moderator focal point ...
    """
    r1 = FOC2TCS(r)
    r2 = TCS2ISCS(r1)
    return r2

def FOC2TCS(r):
    """Convert positions from FP to TCS coordinates
    
    Arguments
    ---------
        r    array
            positions, one row per point Carthesian coordinates in FP
            
    NOTE: FP refers to the coordinates starting at the moderator focal point, 
    x-axis rotated by beamport angle (theta)
    """
    r1 = RotW2.dot(r.T)
    return r1.T + np.array(rm)

def TCS2ISCS(r):
    """Convert positions from TCS to ISCS coordinates
    
    Arguments
    ---------
        r    array
            positions, one row per point Carthesian coordinates in TCS
    """
    r1 = Rot.T.dot((r-T).T)
    return r1.T

def TCS2FOC(r):
    """Convert positions from TCS to FP coordinates
    
    Arguments
    ---------
        r    array
            of positions, one row per point Carthesian coordinates in TCS
    """
    r1 = r-np.array(rm)
    r2 = RotW2.T.dot(r1.T)
    return r2.T

def convertTo(coord, r):
    """Convert position r from default to required coordinates.
    
    Arguments
    ---------
        r: array[:,3]
            position coordinates in the default _COORD system
        coord: str
            ISCS, TCS or FP
    
    Returns
    -------
        r: array[3]
            coordinates of the axis as a function of distance
    """
    def raiseError(c):
        raise Exception('Coordinates not supported: {}'.format(c))        
    if (coord != _COORD):
        if (_COORD=='ISCS'):
            if (coord=='TCS'):
                d = ISCS2TCS(r)
            elif (coord=='FP'):
                d = ISCS2FOC(r)
            else:
                raiseError(coord)
        elif (_COORD=='FP'):
            if (coord=='TCS'):
                d = FOC2TCS(r)
            elif (coord=='ISCS'):
                d = FOC2ISCS(r)
            else:
                raiseError(coord)
        else:
            raiseError(coord)
    else:
        d = r
    return d

def convertFrom(coord, r):
    """Convert position r from default from given coordinates to default (_COORD).
    
    Arguments
    ---------
        r: array[:,3]
            position coordinates in the "coord" system
        coord: str
            ISCS, TCS or FP
    
    Returns
    -------
        r: array[3]
            coordinates of the axis as a function of distance in _COORD
    """
    def raiseError(c):
        raise Exception('Coordinates not supported: {}'.format(c))        
    if (coord != _COORD):
        if (_COORD=='ISCS'):
            if (coord=='TCS'):
                d = TCS2ISCS(r)
            elif (coord=='FP'):
                d = FOC2ISCS(r)
            else:
                raiseError(coord)
        elif (_COORD=='FP'):
            if (coord=='TCS'):
                d = TCS2FOC(r)
            elif (coord=='ISCS'):
                d = ISCS2FOC(r)
            else:
                raiseError(coord)
        else:
            raiseError(coord)
    else:
        d = r
    return d

#%% Beam axis calculation

def __beamAxis(dist):
    """Beam axis coordinates as a function of distance along x.
    Defines beam axis in the _COORD system
    
    Arguments
    ---------
        dist: float
            distance from origin = x coordinate
    
    Returns
    -------
        r: array[3]
            coordinates of the axis as a function of distance
    """
    if (dist <= curve1_begin):
        dx = dist
        delta = c0_angle*dx
        r = c0_begin + np.array([dx, delta, 0.])
    elif (dist <= curve1_end):
        dx = dist-curve1_begin
        delta = 0.5*curve1*dx**2  + c0_angle*dx
        r = c1_begin + np.array([dx, delta, 0.])
    elif (dist <= curve2_begin):
        dx = dist - curve1_end
        delta = c1_angle*dx
        r = c1_end + np.array([dx, delta, 0.])
    elif (dist <= curve2_end):
        dx = dist - curve2_begin
        delta = 0.5*curve2*dx**2 + c1_angle*dx
        r = c2_begin + np.array([dx, delta, 0.])
    else:
        dx = dist - curve2_end
        delta = c2_angle*dx
        r = c2_end + np.array([dx, delta, 0.])  
    return r


def __beamAngle(dist):
    """Beam axis angle with respect to ISCS_x as a function of distance along x.
    
    Arguments
    ---------
        dist: float
            distance from origin = x coordinate
    
    Returns
    -------
        angle: float
            beam direction angle with respect to ISCS_x, in rad
    """
    angle = 0.0
    if (dist <= curve1_begin):
        angle = c0_angle
    elif (dist <= curve1_end):
        dx = dist-curve1_begin
        angle = c0_angle + curve1*dx
    elif (dist <= curve2_begin):
        angle = c1_angle
    elif (dist <= curve2_end):
        dx = dist - curve2_begin
        angle = c1_angle + curve2*dx
    else:
        angle = c2_angle  
    return angle


def beamAxis(dist, coord='ISCS'):
    """Returns beam axis coordinates as a function of distance,
    converted to the required coordinate system.
    
    Arguments
    ---------
        dist: array or list
            distances from origin = x coordinate in _COORD
        coord: str
            ISCS, TCS or FP
    Returns
    -------
        array
            coordinates, one row per distance value
    
    """
    n = np.size(dist)
    dist =  np.array(dist).reshape(n,)
    r = np.zeros((n,3))
    for i in range(n):
        r[i,:] = __beamAxis(dist[i])        
    # convert to required system
    d = convertTo(coord, r)
    if d.shape[0] == 1:
        return d.reshape((3,))
    else:
        return d


def beamAngle(dist, coord='ISCS'):
    """Returns beam axis angle as a function of distance,
    converted to the required coordinate system.
    
    Arguments
    ---------
        dist: array or list
            distances from origin = x coordinate in _COORD
        coord: str
            ISCS, TCS or FP
    Returns
    -------
        array or float
            angles [rad], one element per distance value
    
    """
    da = 0.0
    if (coord != 'ISCS'):
        if (coord=='TCS'):
            da = theta+alpha
        elif (coord=='FP'):
            da = alpha

    n = np.size(dist)
    d =  np.array(dist).reshape(n,)
    if (n==1):
        a = __beamAngle(d[0]) + da
    else:
        a = np.zeros(n)
        for i in range(n):
            a[i] = __beamAngle(d[i]) + da 
    return a



#%% Beam profile calculations

def divideToSections(dist):
    """Divide sequential array of distances into profile sections. 
    
    Return
    ------
        sect: hash map of arrays
            indices of dist array corresponding to given sections.    
    """
    sect = {}
    # feeder
    sect['feeder'] = np.where(dist <= feeder['end']+20)
    # narrow
    sect['narrow'] = np.where((dist > feeder['end']+20) & (dist <= E2_start))
    # wide
    sect['wide']   = np.where((dist > E2_start) & (dist <= E3['c']))
    # foc
    sect['foc']    = np.where(dist > E3['c'])
    return sect


def prof_feeder(dist):
    """Beam dimensions as a function of distance along  x.
    
    Arguments
    ---------
        dist: array
            distance from origin = x coordinate
    Returns
    -------
        dimensions: array[:,6]
            left, right, top, bottom, width, height
    """ 
     # tg(angle) of the left and right feeder wall w.r.t. ISCS
    aL=np.tan(feeder['langle'])
    aR=np.tan(feeder['rangle'])
    
    n = np.size(dist)
    dist =  np.array(dist).reshape(n,)
    left = 0.5*feeder['exit'] - (feeder['end'] - dist)*aL
    right = -0.5*feeder['exit'] - (feeder['end'] - dist)*aR
    height = ell(dist, E1)
    width = left - right
    d = [left, right, 0.5*height, -0.5*height, width, height]
    return np.array(d).T


def prof_narrow(dist):
    """Beam dimensions in the section between BBG and bunker exit, before expansion
    
    Arguments
    ---------
        dist: array
            distance from origin = x coordinate
    Returns
    -------
        dimensions: array[:,6]
            left, right, top, bottom, width, height
            Return zeros outside the segment range.
    """ 
    n = np.size(dist)
    dist =  np.array(dist).reshape(n,)
    width = 20.*np.ones(n)
    height =80.*np.ones(n)    
    idx = np.where(dist <= E1['c'])
    height[idx] = ell(dist[idx], E1)
    aux = beamAxis(dist, coord=_COORD).reshape((n,3))
    y0 =  aux[:,1]
    d = [y0 + 0.5*width, y0 - 0.5*width, 0.5*height, -0.5*height, width, height]
    return np.array(d).T


def prof_wide(dist):
    """Beam dimensions from the expansion guide to the end of the curved wide guide.
    
    Arguments
    ---------
        dist: array
            distance from origin = x coordinate
    Returns
    -------
        dimensions: array[:,6]
            left, right, top, bottom, width, height
            Return zeros outside the segment range.
    """  
    n = np.size(dist)
    dist =  np.array(dist).reshape(n,)
    width = 40.*np.ones(n)
    height = 80*np.ones(n)    
    idx = np.where((dist >= E2_start) & (dist <= E2['c']))
    width[idx] = ell(dist[idx], E2)  
    aux = beamAxis(dist, coord=_COORD).reshape((n,3))
    y0 =  aux[:,1]
    d = [y0 + 0.5*width, y0 - 0.5*width, 0.5*height, -0.5*height, width, height]
    return np.array(d).T


def prof_foc(dist):
    """Beam dimensions through the focusing guide.
    
    Arguments
    ---------
        dist: array
            distance from origin = x coordinate
    Returns
    -------
        dimensions: array[:,6]
            left, right, top, bottom, width, height
            Return zeros outside the segment range.
    """ 
    n = np.size(dist)
    dist =  np.array(dist).reshape(n,)
    width = 40.*np.ones(n)
    height = 80*np.ones(n)    
    idx = np.where(dist >= E3['c'])
    height[idx] = ell(dist[idx], E3)  
    aux = beamAxis(dist, coord=_COORD).reshape((n,3))
    y0 =  aux[:,1]
    d = [y0 + 0.5*width, y0 - 0.5*width, 0.5*height, -0.5*height, width, height]
    return np.array(d).T


def beamSize(dist, coord='ISCS'):
    """Beam size as a function of distance along x.
    
    Arguments
    ---------
        dist: array
            distance from origin = x-coordinate
        coord: str
            ISCS, TCS or FP
    Returns:
        dimensions: array[:,6]
            left, right, top, bottom, width, height, 
            converted to required coordinates.
    """
    n = np.size(dist)
    dist =  np.array(dist).reshape(n,)
    sect = divideToSections(dist)
    size = np.zeros((len(dist),6))
    idx = sect['feeder']
    if (np.size(idx) > 0):
        size[idx] = prof_feeder(dist[idx])
    idx = sect['narrow']
    if (np.size(idx) > 0):
        size[idx] = prof_narrow(dist[idx])    
    idx = sect['wide']
    if (np.size(idx) > 0):
        size[idx] = prof_wide(dist[idx])  
    idx = sect['foc']
    if (np.size(idx) > 0):
        size[idx] = prof_foc(dist[idx])
    
    if (coord != _COORD):
        LT = np.array([dist, size[:,0], size[:,2]]).T
        BR = np.array([dist, size[:,1], size[:,3]]).T
        LTc = convertTo(coord, LT)
        BRc = convertTo(coord, BR)
        size[:,0] = LTc[:,1]
        size[:,1] = BRc[:,1]
        size[:,2] = LTc[:,2]
        size[:,3] = BRc[:,2]
    return size
    

#%% Beam axis cross-sections with walls


def portAxisAtWall(y_tcs):
    """ Get cross-section of beamport axis with a wall normal to the y_tcs axis
    
    Arguments
    ---------
        y_tcs: float
            wall distance from TCS origin
    Returns
    -------
        array
            TCS coordinates of the cross-section point
    """
    v = RotW2.dot(np.array([1., 0., 0.]))  # direction vector, x_FP axis in TCS
    d = (y_tcs - rm[1])/v[1]  # distance from FP origin
    def fnc(x):
        r0 = np.array([x, 0., 0.])  # position at distance x, FP coord.
        r1 = FOC2TCS(r0)
        return r1[1] - y_tcs
    d0 = fsolve(fnc, d)
    r0 = np.array([d0, 0., 0.])
    res = FOC2TCS(r0)
    return res


def positionAtWall(y_tcs):
    """ Get cross-section of beam axis with a wall normal to the y_tcs axis
    
    Arguments
    ---------
        y_tcs: float
            wall distance from TCS origin
    Returns
    -------
        array
            TCS coordinates of the cross-section point
    """
    v = Rot.dot(np.array([1., 0., 0.]))  # direction vector, x_FP axis in TCS
    d = (y_tcs - T[1])/v[1]  # distance from FP origin
    def fnc(x):
        r1 = ISCS2TCS(beamAxis([x], coord = 'ISCS'))
        return r1[1] - y_tcs
    d0 = fsolve(fnc, d)
    r1 = beamAxis([d0], coord = 'ISCS')
    res = ISCS2TCS(r1)
    return res


def positionAtRadius(rad):
    """ Get cross-section of beam axis with a circle centered at TCS
    
    Arguments
    ---------
        rad: float
            radius
    Returns
    -------
        array
            TCS coordinates of the cross-section point
    """
    def fnc(x):
        r1 = ISCS2TCS(beamAxis([x], coord = 'ISCS'))
        r0 = np.sqrt(r1[0]**2 + r1[1]**2)
        return r0 - rad
    d0 = fsolve(fnc, rad)
    r1 = beamAxis([d0], coord = 'ISCS')
    res = ISCS2TCS(r1)
    return res

#%% Beam slices

def getSlice(dist, coord='ISCS'):
    """Generate coordinates of a slice through the beam at given distance.
    The slice is always normal to the x axis in default coordinates !
    
    Arguments
    ---------
        dist: float
            distance from origin (x coordinate)
        coord: str
            ISCS or FP 
    Returns
    -------
        corners: hash map of array[3,]
            CTR (center) and TL, TR, BL, BR corners in given coordinates
    
    """
    # get profile in ISCS
    d = dist
    size = beamSize(d, coord = _COORD)
    TL = np.array([dist, size[:,0], size[:,2]]).T
    TR = np.array([dist, size[:,1], size[:,2]]).T
    BL = np.array([dist, size[:,0], size[:,3]]).T
    BR = np.array([dist, size[:,1], size[:,3]]).T
    CTR = 0.25*(TL+TR+BL+BR)
    if (coord != _COORD):
        TL = convertTo(coord, TL)
        TR = convertTo(coord, TR)
        BL = convertTo(coord, BL)
        BR = convertTo(coord, BR)
        CTR = convertTo(coord, CTR)
        
    # corner coordinates
   # TL = np.array([d, win[0], win[2]])
  #  TR = np.array([d, win[1], win[2]])
  #  BL = np.array([d, win[0], win[3]])
  #  BR = np.array([d, win[1], win[3]])
  #  CTR = 0.25*(TL+TR+BL+BR)    
    corners = {}
    corners['CTR'] = CTR
    corners['TL'] = TL
    corners['TR'] = TR
    corners['BL'] = BL
    corners['BR'] = BR
    return corners


def getSliceReport(win):
    sfx2 = '\t{:.3f}\t{:.3f}\n'
    sfx3 = '\t{:.3f}\t{:.3f}\t{:.3f}\n'
    fmt = 'width, height:'+sfx2
    fmt += 'centre:'+sfx3
    fmt += 'top - left:'+sfx3
    fmt += 'top - right:'+sfx3
    fmt += 'bottom - left:'+sfx3
    fmt += 'bottom - right:'+sfx3
    width = win['TL'][1]-win['TR'][1]
    height = win['TL'][2]-win['BL'][2]
    out = fmt.format(width, height, *win['CTR'], *win['TL'], *win['TR'], *win['BL'], *win['BR'])
    return out


def printSlice(win, leg=''):
    out = 'Slice of {}:\n'.format(leg)
    out += getSliceReport(win)
    print(out)    


def printSliceCal(dist, leg='', coord='ISCS'):
    win = getSlice(dist, coord=coord)
    out = '{}: Slice at {:.3f} (ISCS_x), coord={}\n'.format(leg,dist,coord)
    out += getSliceReport(win)
    print(out)


#%% Top level output functions

def printCFG(dist, segments, gap=0.2):
    """Print configuration for SIMRES segmented guide.
    """
    sg = np.array(segments)    
    n = sg.shape[0]
    itm = []
    d = dist
    win = beamSize(d, coord='ISCS').reshape(6,)
    w1 = win[4]
    h1 = win[5]
    c1 = 0.5*(win[1]+win[0])
    nseg = 0
    for i in range(n):
        m = int(sg[i,0]) 
        L = sg[i,1]  
        ref = list(sg[i,2:6])           
        for j in range(m): 
            nseg += 1                      
            d += L
            win = beamSize(d, coord='ISCS').reshape(6,)
            itm.append([win[4], win[5], L] + ref)

            print(i)
    win = beamSize(d, coord='ISCS').reshape(6,)
    w2 = win[4]
    h2 = win[5]
    c2 = 0.5*(win[1]+win[0])
    Ltot = d - dist +  (nseg-1)*gap  
    a = np.arctan2(c2-c1, Ltot)/deg
    
    item='\t\t<ITEM>'+'{:.3f} '*3 + '{:.2f} '*4 + '</ITEM>\n'
    seg='\t<SEG name="segments parameters" rows="{}">\n'
    segend='\t</SEG>\n'
    gon='<GON name="gonio" units="deg">'+'{:.5f} '*3+'</GON>\n'
    sta='<STA name="stage" units="mm">'+'{:.3f} '*3+'</STA>\n'
    size='<SIZE name="dimensions" units="mm">'+'{:.3f} '*3+'</SIZE>\n'
    exi='<EXIT name="exit window" units="mm">'+'{:.3f} '*2 +'</EXIT>\n'

    
    out = size.format(w1, h1, Ltot)
    out += sta.format(c1, 0., 0.)
    out += gon.format(a, 0., 0.)
    out += exi.format(w2, h2)
    out += seg.format(nseg)
    for i in range(nseg):
        out += item.format(*itm[i])
    out += segend
    return out  


def plotProfile(dist, coord='ISCS', file=''):
    """
    Plot beam profile in given range of distances in required coordinates.
    NOTE: the distances are always in the default coordinates (ISCS)
    
    Parameters:
    ----------
    dist: array
        array of distances in mm
    coord: str
        reference frame in which to calculate coordinates
    file: str
        output filename
    
    """
    profile = beamSize(dist, coord = coord)
    axis = beamAxis(dist, coord = coord)
       
    zero = np.zeros(len(dist))
    r = np.array([dist, zero, zero]).T    

    d = convertFrom('FP',r)                
    # converto to required system
    ax2 = convertTo(coord, d)
    leg2 = 'FP_x axis'          
    plt.xlabel('Distance, mm')
    plt.ylabel('Width, mm')
    plt.title('Horizontal profile, {}'.format(coord))
    ax = plt.gca()
    plt.errorbar(axis[:,0], profile[:,0], fmt='b-')
    plt.errorbar(axis[:,0], profile[:,1], fmt='b-')
    ln3 = plt.errorbar(axis[:,0], axis[:,1], fmt='r--', label='beam axis')
    ln4 = plt.errorbar(ax2[:,0], ax2[:,1], fmt='g-.', label=leg2)
    plt.grid()
    lns = (ln3, ln4)
    labs = ('beam axis', leg2) 
    ax.legend(lns, labs, loc='best', frameon=False)
    if (len(file)>0):
        plt.savefig(file+'_hor'+'.pdf', bbox_inches='tight')
    plt.show()
    
    plt.xlabel('Distance, mm')
    plt.ylabel('Height, mm')
    plt.title('Vertical profile, {}'.format(coord))
    plt.errorbar(axis[:,0], profile[:,2], fmt='b-')
    plt.errorbar(axis[:,0], profile[:,3], fmt='b-')
    plt.errorbar(axis[:,0], axis[:,2], fmt='r--', label='beam axis')
    plt.grid()
    if (len(file)>0):
        plt.savefig(file+'_ver'+'.pdf', bbox_inches='tight')
    plt.show()
  

def getTable(Lmin=0.0, Lmax=158100, dstep=20):
    """ Generates a table of nominal beam axis coordinates 
    in three reference frames: TCS, W2 and ISCS.

    Arguments:
    ----------
    Lmin: float
        minimum distance, mm
    Lmax: float
        maximum distance, mm
    dstep: float
        distance step, mm
    
    Returns:
    -------
    Table as tab separated text with 1-line header
    """
    
    d = np.arange(Lmin, Lmax, dstep)
    tcs = np.zeros([d.size,3])
    iscs = np.zeros([d.size,3])
    foc = np.zeros([d.size,3])
    afoc = np.zeros([d.size,1])
    aiscs = np.zeros([d.size,1])
    for i in range(d.size):
        dist = d[i]
        r = beamAxis(dist, coord='ISCS')
        tcs[i,:] =ISCS2TCS(r)
        foc[i,:] = TCS2FOC(tcs[i,:])
        iscs[i,:] = TCS2ISCS(tcs[i,:])
        afoc[i,0] = beamAngle(dist,coord='FP')/deg
        aiscs[i,0] = beamAngle(dist,coord='ISCS')/deg
    htcs = ['x_tcs','y_tcs','z_tcs']
    hfp = ['x_w2','y_w2','z_w2', 'angle_w2']  
    hiscs = ['x_iscs','y_iscs','z_iscs', 'angle_iscs']
    hdr = '\t'.join(htcs + hfp + hiscs)
    data = np.concatenate((tcs,foc,afoc,iscs,aiscs), axis=1)
    nr = data.shape[0]
    nc = data.shape[1]
    fmt = (nc-1)*'{:.5f}\t'+'{:.5f}\n'
    out = '# {}\n'.format(hdr)
    for i in range(nr):
        out += fmt.format(*data[i,:])
    return out


def writeTable(file='BEER_beam.txt', Lmin=0.0, Lmax=158100, dstep=20):
    """ Saves a table of nominal beam axis coordinates and angles 
    in three reference frames: TCS, W2 and ISCS.

    Arguments:
    ----------
    file: str
        output file
    Lmin: float
        minimum distance, mm
    Lmax: float
        maximum distance, mm
    dstep: float
        distance step, mm
    """
    out = getTable(Lmin=Lmin, Lmax=Lmax, dstep=dstep)
    if file:
        f = open(file, 'w')
        f.write(out)
        f.close()
        print('Beam axis table written in {}'.format(file))


