# -*- coding: utf-8 -*-
"""
Collects guide profiles exported from SIMRES and creates plots in FP/W2 coordinates
Created on Wed Mar 20 11:25:12 2019

@author: User
"""


import numpy as np
#import BEERcomponents as BC
from matplotlib import pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)




def path2win(name):
    out = name.replace('\\','/')
    if (out[-1] != '/'):
        out += '/'
    return out
inpath = path2win(r'D:\Saroun\Simulace\ESS\phase2\simres\profiles')

# collect guide IDs
"""
guides = ['NBOA', 'BBG']
for key in BC.BEER.keys():
    if (key.startswith('G') and (key != 'GEX2')):
        guides.append(key)
print(guides)        
"""       
guides = ['NBOA', 'BBG', 'GSW', 
          'GCA1', 'GCA2', 'GCA3', 'GCA4', 'GCB', 'GCC', 'GCE', 'GCF', 'GCG', 
          'GE1', 'GN1', 'GN2', 'GSH2', 'GE2A', 'GE2B', 'GT1', 'GT2', 
          'GF1', 'GF2', 'GEX1']

# shit for conversion to W2 coordinates:
sh = np.array([0, -30, -30, 0, 0])
# read profile tables and merge them into one:
table = []
for key in guides:
    tab = np.loadtxt(inpath+'prof_'+key+'.dat')
    for i in range(tab.shape[0]):
        # append one column for axis position
        tt = np.concatenate((tab[i,:],[0.0]))
        tt[1:5] += sh[0:4]
        ctr = 0.5*(tt[2]+tt[3])
        tt[-1] = ctr
        ltab = [key] + tt.tolist()
        table.append(ltab)

with open(inpath+"simres_guide_profile.dat", "w") as file:
    nc = len(table[0])
    nr = len(table)
    hdr = ['ID', 'iseg', 'dist', 'left', 'right', 'top', 'bottom', 'mL', 'mR', 'mT', 'mB', 'ctr' ]
    fmt = "# " + (len(hdr)-1)*"{}\t" + "{}\n"
    file.write(fmt.format(*hdr))
    fmt = "{}\t" + (nc-2)*"{:.8g}\t" + "{:.8g}\n"
    for i in range(nr):
        ss = fmt.format(*table[i])
        file.write(ss)

#%% Plot profiles
# set default plot properties
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (9, 3),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
plt.rcParams.update(params)



guides = ['NBOA', 'BBG', 'GSW', 
          'GCA1', 'GCA2', 'GCA3', 'GCA4', 'GCB', 'GCC', 'GCE', 'GCF', 'GCG', 
          'GE1', 'GN1', 'GN2', 'GSH2', 'GE2A', 'GE2B', 'GT1', 'GT2', 
          'GF1', 'GF2', 'GEX1']

palette = ['#000000','#0070C0','#833C0C','#7030A0','#00B050','#305496','#C00000']

feeder = [['NBOA', 'BBG'],'NBOA + BBG', palette[0]]
chopper = [['GCA1', 'GCA2', 'GCA3', 'GCA4', 'GCB', 'GCC', 'GCE', 'GCF', 'GCG'],'choppers', palette[1]]
bunker = [['GE1', 'GN1', 'GN2'],'bunker guide', palette[2]]
shutter = [['GSH2'],'shutter', palette[3]]
expansion = [['GE2A', 'GE2B'],'expansion guide', palette[4]]
transport = [['GT1', 'GT2'],'transport guide', palette[5]]
focusing = [['GF1', 'GF2', 'GEX1'],'focusing guide', palette[6]]
groups = [feeder, chopper, bunker, shutter, expansion, transport, focusing]



def plotGroup(gr, ix):
    x = []
    y1 = []
    y2 = []
    for row in table:
        if (row[0] in gr[0]):
           x.append(row[2]/1000)
           y1.append(row[ix+2])
           y2.append(row[ix+3])
    plt.errorbar(x, y1, color=gr[2], linestyle='-')       
    ln2 = plt.errorbar(x, y2, color=gr[2], linestyle='-', label=gr[1])
    return ln2

#%%
    
def plotProf(ix=1, file=''):
    if ix==1:
        plt.ylabel('y, mm')
        plt.title('Horizontal profile, FP/W2 coordinates')
        plt.ylim(-200, 100)
        mintics = MultipleLocator(50)
        majtics = MultipleLocator(10)
    elif ix==2:
        plt.ylabel('z, mm')
        plt.title('Vertical profile, FP/W2 coordinates')
        plt.ylim(-60, 60)
        mintics = MultipleLocator(20)
        majtics = MultipleLocator(5)
    else:
        raise Exception('Invalid coordinate index')
    ax = plt.axes()
    plt.xlabel('x, m')
    plt.xlim(0, 160)
    
    for g in groups:
        plotGroup(g, 1 + 2*(ix-1))
    ax.xaxis.set_major_locator(MultipleLocator(20))
    ax.xaxis.set_minor_locator(MultipleLocator(2))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.yaxis.set_major_locator(mintics)
    ax.yaxis.set_minor_locator(majtics)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    plt.grid(b=True, which='both', color= (0.8, 0.8, 0.8), linestyle='-', linewidth=0.5)
    ax.axvline(x=5.408, color= (0.2, 0.2, 0.2), linestyle='--', linewidth=1)
    ax.axvline(x=28, color= (0.2, 0.2, 0.2), linestyle='--', linewidth=1)
    dist_D03 = 40.5/np.cos(np.deg2rad(144.7-90))
    ax.axvline(x=dist_D03, color= (0.2, 0.2, 0.2), linestyle='--', linewidth=1)
    ax.axvline(x=154.1, color= (0.2, 0.2, 0.2), linestyle='--', linewidth=1)
    plt.legend(loc='best', frameon=True, facecolor='w', framealpha=0.9, ncol=2, 
                        fontsize='large', columnspacing=1)
    #frame = legend.get_frame()
    #frame.set_facecolor('white')
    #lns = (ln)
    #labs = ('beam axis', leg2) 
    #ax.legend(lns, labs, loc='best', frameon=False)

    if (len(file)>0):
        plt.savefig(file+'.png', bbox_inches='tight')
    plt.show()

# %%
plotProf(ix=1, file='guide_profile_H')
plotProf(ix=2, file='guide_profile_V')
       
