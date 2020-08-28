# -*- coding: utf-8 -*-
"""

Created on Fri Jul  3 11:23:11 2020
@author: Jan Saroun, saroun@ujf.cas.cz
"""

from setuptools import setup

beer_data = ['templates/*.template', 
             'resources/*', 
             'resources/tables/*',
			 'simres/*',
			 'mcstas/*']


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='beer',
    version='1.6.0',
    description='Neutron optics model for the diffractometer BEER at ESS',
    long_description = long_description,
    long_description_content_type='text/markdown',
    author='Jan Saroun',
    author_email='saroun@ujf.cas.cz',
    license='MIT',
    url='https://bitbucket.org/saroun/beer_optics',
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
    platforms=['any'],
    keywords='ESS, BEER, neutron', 
    python_requires='>=3.6',
    install_requires=['numpy', 'matplotlib'],
    packages=['beer'],
    package_data={'beer': beer_data}, 
    data_files=[('.',['run_simres.py', 'run_mcstas.py', 'LICENSE'])]
)
