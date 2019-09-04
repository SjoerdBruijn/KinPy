#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 21:43:42 2019

@author: sjoerd
"""


import scipy.io
import kinpy as kp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

x,y,z,fs = kp.readndf("testdata/TN000077.ndf")
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x[:,17:19],z[:,17:19])
ax.axis('equal')
ax.set(title= 'foot trajectory',
       ylabel = 'z pos [mm]',
       xlabel = 'x pos [mm]')

dat = kp.xyz2dat(x,y,z)

## test case for kp.prod_col
#eye = np.eye(3,k=0)
#eye = eye.reshape([1,9])
#eye = np.r_[eye,eye,eye,eye,eye]
#C = kp.prod_col(eye,dat[0:5:1,0:9:1])
#np.subtract(dat[0:5:1,0:9:1],C)

mat = scipy.io.loadmat('testdata/TN000076.mat')
traj =mat['traj']

com = kp.calc_combined_com(traj)

kp.plot_3d(traj)
    
    
##
settings=dict() 
settings['segments']         = pd.read_excel('testdata/full data set/Settings_Basketball.xls') 
settings['data_path']        = ['raw data/']; #location of the data
settings['file_prefix']      = 'TN000'; 
settings['file_extension']   = '.ndf';
settings['pointer_file']     = 'RB-06114.RIG';
settings['pointer_kol']      = range(13,18);
settings['reference_trial_nr']     = 89; 
settings['cluster_pointer_nr']     = range(78,88); 
settings['forceplate_pointers_nr'] = range(12,16);
settings['pointerfilename']         ='testdata/full data set/RB-06114.RIG'
# of course, in our setting, all is still based on 1-based indexing. 


pointer= kp.ImportPointerFile(settings['pointerfilename']) 


