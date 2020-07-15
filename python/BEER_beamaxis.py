# -*- coding: utf-8 -*-
"""
Calculation of BEER beam axis
version: 1.3
Date: 20/3/2019

Created on Tue Oct 10 10:49:35 2017
@author: J. Saroun, saroun@ujf.cas.cz
"""

import numpy as np
#from matplotlib import pyplot as plt
import BEERgeometry as BA
deg = np.pi/180;
    

    
# %% Validation - are the given points on the beam axis?
    
# Measured points (x,y,z) in TCS, 
# inner bunker wall
p = np.array([
     [-19850.437, 14048.417, 137.0],
     [-19999.493,	14154.949, 137.0]
     ])

p_in = np.zeros(np.array(p).shape)
print('\nCheck points at inner bunker wall:')
for i in range(p_in.shape[0]):
    p_in[i,:] = BA.positionAtWall(p[i,1])
    fmt = 'y={:g}, difference: [{:g}\t{:g}\t{:g}], dist={:g}'
    diff = p[i,:] - p_in[i,:]
    dis = np.linalg.norm(diff)
    print(fmt.format(p[i,1], diff[0], diff[1], diff[2], dis))


# Measured points (x,y,z) in TCS, 
# outer bunker wall
p = np.array([
     [-23025.438, 16309.781, 137.000],
     [-22835.689, 16175.192, 137.000]
     ])

p_out = np.zeros(np.array(p).shape)
print('\nCheck points at outer bunker wall:')
for i in range(p_out.shape[0]):
    p_out[i,:] = BA.positionAtWall(p[i,1])
    fmt = 'y={:g}, difference: [{:g}\t{:g}\t{:g}], dist={:g}'
    diff = p[i,:] - p_out[i,:]
    dis = np.linalg.norm(diff)
    print(fmt.format(p[i,1], diff[0], diff[1], diff[2], dis))

# Measured points (x,y,z) in TCS, 
# inner bunker wall (Confluence, p1, p3)
p = np.array([
    [-19972.508,	14192.090, 137.0],
    [-22814.512, 16204.341, 137.000]
     ])

p_ax = np.zeros(np.array(p).shape)
print('\nCheck position of beamport axis at bunker wall:' )
for i in range(p_ax.shape[0]):
    p_ax[i,:] = BA.portAxisAtWall(p[i,1])
    fmt = 'y={:g}, difference: [{:g}\t{:g}\t{:g}], dist={:g}'
    diff = p[i,:] - p_ax[i,:]
    dis = np.linalg.norm(diff)
    print(fmt.format(p[i,1], diff[0], diff[1], diff[2], dis))


# %%Measured points (x,y,z) in TCS, 
# sample position

dist_5500 = 5500
r5500_TCS = BA.positionAtRadius(dist_5500)
r5500_ISCS =BA.TCS2ISCS(r5500_TCS)
r5500_FP =BA.TCS2FOC(r5500_TCS)
print('\nBeam axis at the monolith exit (R_TCS={:g}):'.format(dist_5500))
print('TCS: [{:g}, {:g}, {:g}]'.format(*r5500_TCS))
print('ISCS: [{:g}, {:g}, {:g}]'.format(*r5500_ISCS))
print('FP: [{:g}, {:g}, {:g}]'.format(*r5500_FP))

dist_6000 = 6000
r6000_TCS = BA.positionAtRadius(dist_6000)
r6000_ISCS =BA.TCS2ISCS(r6000_TCS)
r6000_FP =BA.TCS2FOC(r6000_TCS)
print('\nBeam axis at the monolith exit (R_TCS={:g}):'.format(dist_6000))
print('TCS: [{:g}, {:g}, {:g}]'.format(*r6000_TCS))
print('ISCS: [{:g}, {:g}, {:g}]'.format(*r6000_ISCS))
print('FP: [{:g}, {:g}, {:g}]'.format(*r6000_FP))

dist_bkrin = 24500
rbkrin_TCS = BA.positionAtRadius(dist_bkrin)
print('\nBeam axis at the bunker entry (R_TCS={:g}):'.format(dist_bkrin))
print('TCS: [{:g}, {:g}, {:g}]'.format(*rbkrin_TCS))

dist_bkrout = 28000
rbkrout_TCS = BA.positionAtRadius(dist_bkrout)
print('\nBeam axis at the bunker exit (R_TCS={:g}):'.format(dist_bkrout))
print('TCS: [{:g}, {:g}, {:g}]'.format(*rbkrout_TCS))

y_D03 = 40500;   
r_D03 = BA.positionAtWall(y_D03)
r_D03_ISCS = BA.TCS2ISCS(r_D03)
dist_D03 = np.sqrt(r_D03_ISCS[0]**2+r_D03_ISCS[1]**2)
print('\nBeam axis at D03 exit (y_TCS={:g}):'.format(y_D03))
print('TCS: [{:g}, {:g}, {:g}]'.format(*r_D03)); 
print('ISCS Distance to D03 exit: {:g}'.format(dist_D03))

y_E021 = 154100-49000;   
r_E021 = BA.positionAtRadius(y_E021)
r_E021_ISCS = BA.TCS2ISCS(r_E021)
dist_E021 = np.sqrt(r_E021_ISCS[0]**2+r_E021_ISCS[1]**2)
print('\nBeam axis at E02-2, E02-1 boundary (y_TCS={:g}):'.format(y_E021))
print('ISCS: [{:g}, {:g}, {:g}]'.format(*r_E021_ISCS)); 
print('ISCS Distance to E02-2, E02-1 boundary: {:g}'.format(dist_E021))

dist_cave = 154100
rcave_TCS = BA.positionAtRadius(dist_cave)
print('\nBeam axis at the cave entry (R_TCS={:g}):'.format(dist_cave))
print('TCS: [{:g}, {:g}, {:g}]'.format(*rcave_TCS)); 
rcave_ISCS = BA.TCS2ISCS(rcave_TCS)
print('ISCS: [{:g}, {:g}, {:g}]'.format(*rcave_ISCS));

dist = 158000;
rsam_TCS = BA.ISCS2TCS(BA.beamAxis(dist)).reshape((3,));  
print('\nAssumed sample position:')
print('TCS: [{:g}, {:g}, {:g}]'.format(*rsam_TCS));
rsam_R=np.sqrt(rsam_TCS[0]**2+rsam_TCS[1]**2)
print('TCS radius: {:g}'.format(rsam_R));
rsam_FOC = BA.TCS2FOC(rsam_TCS);
print('Distance from beamport axis: {:g}'.format(rsam_FOC[1]));

# %% Detailed table of BEER beam


d = np.arange(0.0, 158100, 100);
tcs = np.zeros([d.size,3]);
iscs = np.zeros([d.size,3]);
foc = np.zeros([d.size,3]);
for i in range(d.size):
    dist = d[i];
    r = BA.beamAxis(dist, coord='ISCS');
    tcs[i,:] = BA.ISCS2TCS(r);
    foc[i,:] = BA.TCS2FOC(tcs[i,:]);
    iscs[i,:] = r;

hdr='x_tcs\ty_tcs\tz_tcs\tx_w2\ty_w2\tz_w2\tx_iscs\ty_iscs\tz_iscs';
np.savetxt('BEER_beam.txt', np.concatenate((tcs,foc,iscs), axis=1), fmt='%.5f', delimiter='\t', 
           header=hdr);
           
  

# %% Test section
fmt = 'r_beam({:g}) = [{:g},{:g},{:g}]_iscs = [{:g},{:g},{:g}]_tcs'
# Dirk's value
print('\nDirk:')
r_tcs1 = np.array([-128943.5, 91475.583, 137])
r_iscs1 = BA.TCS2ISCS(r_tcs1)
print('r_tcs=[{:g},{:g},{:g}]'.format(*r_tcs1))
print('r_iscs=[{:g},{:g},{:g}]'.format(*r_iscs1))
r_beam1 = BA.beamAxis(r_iscs1[0], coord='ISCS')
r_beam1_tcs = BA.ISCS2TCS(r_beam1)
print(fmt.format(r_iscs1[0], *r_beam1, *r_beam1_tcs))

# NUVIA's value
print('\nNUVIA:')
x_sample = 158000.
r_beam2 = BA.beamAxis(x_sample, coord='ISCS')
r_beam2_tcs = BA.ISCS2TCS(r_beam2)
r_beam2_fp = BA.ISCS2FOC(r_beam2)
fmt = 'r_beam({:g}) = [{:g},{:g},{:g}]_iscs = [{:g},{:g},{:g}]_fp = [{:g},{:g},{:g}]_tcs'
print(fmt.format(x_sample, *r_beam2, *r_beam2_fp, *r_beam2_tcs))


# %%



