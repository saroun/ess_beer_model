
def reportTables(outdir=''):
    """
    Exports three tables in text format which describe BEER optics geometry:
        
    1. **Table of components** - the content of the document ESS-0478295 
    `BEER optics specifications table`, in file `components_list.txt`.
    
    2. **Beam axis table**, a detailed table of BEER beam axis coordinates in 
    three reference frame (TCS, FP and ISCS), in file `BEER_beam.txt`.
    
    3. **Reference operaton modes** for BEER, in file 
    `BEER_modes.txt`.
    
    Refer to ESS-0238217, `Optics Report for the BEER Instrument
    `
    Parameters:
    -----------
    outdir: str
        output directory (default is the current directory)    
    
    """
    import beer.geometry as BG
    import beer.components as BC
    import beer.modes as BMOD 
    import os
    # Beam axis table 
    fout = os.path.normpath(os.path.join(outdir,'BEER_beam.txt'))
    BG.writeTable(file=fout, Lmin=0.0, Lmax=158100, dstep=20)

    # Optics table
    # NOTE: we want to have beam centres in FP coordinates ... 
    fout = os.path.normpath(os.path.join(outdir,'BEER_components.txt'))
    BC.writeComponents(file=fout, gaps=True, coord='FP')
    
    #  Export BEER modes as a table
    fout = os.path.normpath(os.path.join(outdir,'BEER_modes.txt'))
    BMOD.reportModes(file=fout)


def reportChoppers(outdir=''):
    """ 
    Report on chopper settings for various reference modes. 
    For each mode:
        
    - Print parameters of active choppers.
    
    - Calculate ToF and wavelength transmissivity distributions at the detector
    and show in a graph. 
    
    **NOTE**
    
    Actual source spectrum is not considered, assumes uniform spectrum. 
    
    Parameters:
    -----------
    outdir: str
        output directory (default is the current directory)
    
    """
    # Plot chopper characteristics for selected reference modes
    import beer.modes as BMOD 
    import os
    modes = [5, 10, 13, 14, 15]
    fdir = os.path.normpath(outdir)
    fout = os.path.join(fdir,'BEER_choppers.txt')
    out = ''
    for m in modes:
        mod = BMOD.modes[m]
        pdf = os.path.join(fdir,'choppers_{}.pdf'.format(mod['ID']))
        out += '\n'
        out += BMOD.reportChoppers(imode=m, 
                            pulses=[-1,0,1,2], 
                            wrange=[0.1, 20, 0.02], 
                            trange=[0, 400, 0.01],
                            pdf=pdf)
    with open(fout, 'w') as f: 
        f.write(out)
        f.close()
        print('Chopper settings reported in {}'.format(fout))


def plotGuides(outdir='', coord='FP'):
    """ 
    Plot profiles of neutron guides along BEER beamline.  
    
    Parameters:
    -----------
    outdir: str
        output directory (default is the current directory)
    coord: str
        reference frame to use:
            
        - ISCS = instrument coordinate system
        - FP = focal point system (x = W2 beamport axis)
    """
    import numpy as np
    import os
    import beer.geometry as BG
    dmin = 2030
    dmax = 157000
    n = int((dmax-dmin)/500)
    dist = np.linspace(dmin, dmax, num=n)
    fdir = os.path.normpath(outdir)
    fout = os.path.join(fdir,'BEER_guides')
    BG.plotProfile(dist, coord=coord, file=fout)
    