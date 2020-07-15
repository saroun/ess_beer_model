# -*- coding: utf-8 -*-
"""
Worksheet for calculation of BEER beam profile.
version: 1.4
Date: October 13, 2018

@author: J. Saroun, saroun@ujf.cas.cz
"""

import numpy as np
import BEERgeometry as BA
import BEERcomponents as BC
from BEERcomponents import BEER
deg = np.pi/180;
 
# %% Calculate critical slices in FP coordinates:

coord = 'ISCS'

# NBOA entry
win = BA.getSlice(BA.nboa_start, coord=coord)
BA.printSlice(win,leg='NBOA start '+coord)
# NBOA end
win = BA.getSlice(BA.nboa_end, coord=coord)
BA.printSlice(win,leg='NBOA end '+coord)
# BBG start
win = BA.getSlice(BA.bbg_start, coord=coord)
BA.printSlice(win,leg='BBG start '+coord)
# BBG end
win = BA.getSlice(BA.bbg_end, coord=coord)
BA.printSlice(win,leg='BBG end '+coord)


# %% Define distance points

d_start = 2030.5 # start distance [mm]
d_end = 157000.0   # end distance [mm]
dx = 100.0 # step [mm]

#d_start = 2030.5 # start distance [mm]
#d_end = BA.bbg_end   # end distance [mm]
#dx = 10.0 # step [mm]

nx = int(np.floor((d_end-d_start)/dx))
d = np.linspace(d_start, d_start+nx*dx, num=nx+1)

# %% Calculate profile
profile = BA.beamSize(d, coord='ISCS')
axis = BA.beamAxis(d, coord='ISCS')
# save profile
np.savetxt('NBOA_profile_FP.dat', profile, fmt='%g', 
           header='x\tleft\tright\ttop\tbottom', delimiter='\t')
np.savetxt('NBOA_axis_FP.dat', axis, fmt='%g', 
           header='x\ty\tz', delimiter='\t')

# %% Plot profile

# in FP = FOC
BA.plotProfile(d, coord='FP', file='BEER_profile_FP')
# in ISCS
BA.plotProfile(d, coord='ISCS', file='BEER_profile_ISCS')


# %% Caclulate and save component list table

table = BC.writeComponents(coord = 'FP', file = 'components_list.txt', gaps=True)

# %%
win = BA.getSlice(BC.BEER['BBG']['end'], coord=coord)
BA.printSlice(win,leg='BBG optics end '+coord)


# %%
key = 'NBOA'
[w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(BEER[key], coord = 'ISCS')
print('\n{} start:\n'.format(key))

r_ISCS = np.array([BEER[key]['start'], ctr1, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('center, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))
r_in = np.copy(r_FP)

r_ISCS = np.array([BEER[key]['start'], ctr1+w1/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('left, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))

r_ISCS = np.array([BEER[key]['start'], ctr1-w1/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('right, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))

print('height: {:.3f}'.format(h1))

r_ISCS = np.array([BEER[key]['start'], ctr1-w1/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('right, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))


print('\n{} end:\n'.format(key))
r_ISCS = np.array([BEER[key]['end'], ctr2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('center, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))
r_out = np.copy(r_FP)

r_ISCS = np.array([BEER[key]['end'], ctr2+w2/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('left, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))

r_ISCS = np.array([BEER[key]['end'], ctr2-w2/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('right, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))

print('height: {:.3f}'.format(h2))
rdiff = r_out-r_in
cros = np.cross(rdiff, np.array([1, 0, 0]))
sin =np.sqrt(cros.dot(cros)/rdiff.dot(rdiff))
#sin = np.sqrt(cros(rdiff, np.array([1, 0, 0]))/np.sqrt(rdiff.dot(rdiff))
angle = np.arcsin(sin)*180/np.pi
print('angle: {:.5f} deg'.format(angle))




#%%
key = 'BBG'
[w1, h1, w2, h2, ctr1, ctr2] = BC.getEntryExit(BEER[key], coord = 'ISCS')
print('\n{} start:\n'.format(key))

r_ISCS = np.array([BEER[key]['start'], ctr1, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('center, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))
r_in = np.copy(r_FP)

r_ISCS = np.array([BEER[key]['start'], ctr1+w1/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('left, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))

r_ISCS = np.array([BEER[key]['start'], ctr1-w1/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('right, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))

print('height: {:.3f}'.format(h1))

r_ISCS = np.array([BEER[key]['start'], ctr1-w1/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('right, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))


print('\n{} end:\n'.format(key))
r_ISCS = np.array([BEER[key]['end'], ctr2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('center, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))
r_out = np.copy(r_FP)

r_ISCS = np.array([BEER[key]['end'], ctr2+w2/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('left, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))

r_ISCS = np.array([BEER[key]['end'], ctr2-w2/2, 0])
r_FP = BA.ISCS2FOC(r_ISCS)
print('right, W2 [{:.3f}, {:.3f}, {:.3f}]'.format(*r_FP))

print('height: {:.3f}'.format(h2))

