# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 16:14:06 2020

@author: User
"""
import os, sys, shutil, glob


def getTemplate(template='BEER_reference.instr', inpath=None):
    """
    Return required template content from beer/templates.
    
    Parameters:
    ----------
    template: str
        template name without the ``.template`` extension
    inpath: str
        if defined, search for the temlate in given directory 
        rather than package resources
    """
    if inpath:
        root = os.path.normpath(inpath)
    else:
        root = os.path.join(os.path.dirname(__file__),'templates')
    fn = os.path.join(root, template+'.template')
    lines = ''
    try:
        with open(fn, 'r') as fi:
            lines = fi.readlines()
    except Exception as e:
        msg = 'Can''t read file {}.\n {}\n'.format(fn,e)
        sys.exit(msg)
    return lines

def getResource(name=''):
    """
    Return full path to the requred resource file.
    
    Parameters:
    ----------
    name: str
        resource file name
    """
    root = os.path.join(os.path.dirname(__file__),'resources')
    fn = os.path.normpath(os.path.join(root, name))
    if not os.path.isfile(fn):
        raise Exception('Resource {} does not exist'.format(fn))
    return fn


def copyResources(outdir, dirs=[], globs=[], files=[], force=True):
    """
    Copy resources needed to run simulations into the workspace.
    
    If not force, only copy files if they do not exist in destination.
    """
    root = os.path.join(os.path.dirname(__file__),'resources')

    for d in dirs:
        fulld = os.path.join(root, d)
        dfs = os.listdir(fulld)
        for f in dfs:
            files.append(os.path.join(d,f)) 
            
    for g in globs:
        fullg = os.path.join(root, g)
        lg = glob.glob(fullg)
        for fn in lg:
            f = os.path.basename(fn)
            files.append(f)

    for rs in files:
        src = getResource(name=rs)
        dest = os.path.join(outdir,rs)
        p = os.path.dirname(dest)
        if not os.path.isdir(p):
            try:
                print('Creating directory: {}'.format(p))
                os.makedirs(p)
            except Exception as e:
                raise Exception(e)
        if force or (not os.path.isfile(dest)):
            shutil.copyfile(src, dest)