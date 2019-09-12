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

#dat = kp.xyz2dat(x,y,z)

#eye = np.eye(3,k=0)
#eye = eye.reshape([1,9])
#eye = np.r_[eye,eye,eye,eye,eye]
#D = np.ones([5,9])*np.arange(9).T+1

## Test case calc_axis_col
#A = np.array([(11,2,23,4,52,16,27,81,91),([11,21,13,14,15,16,71,81,9]),(29,28,37,63,52,64,43,42,31),(9,84,7,64,5,54,36,2,1)])
#B = kp.calc_axis_col(A)

## Test case prod_col
#A = np.array([(1,2,3,4,5,6,7,8,9),([1,2,3,4,5,6,7,8,9])])
#B = np.array([(9,8,7,6,5,4,3,2,1),(9,8,7,6,5,4,3,2,1)])
#kp.prod_col(A,B)

## test case chgframe
#eye2 = np.eye(3,k=0)
#eye2 = eye2.reshape([1,9])
#eye2 = np.r_[eye2,eye2,eye2,eye2,eye2]
#eye2[0,1] = 2 
#R,D2 = kp.chgframe(eye2,eye,D)

## test case for kp.prod_col
#eye = np.eye(3,k=0)
#eye = eye.reshape([1,9])
#eye = np.r_[eye,eye,eye,eye,eye]
#C = kp.prod_col(eye,dat[0:5:1,0:9:1])
#np.subtract(dat[0:5:1,0:9:1],C)

mat = scipy.io.loadmat('testdata/TN000076.mat')
traj =mat['traj']

com = kp.calc_combined_com(traj)

#kp.plot_3d(traj)
    
    
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

BLM=dict()
BLM['segment']=dict()
n_seg=len(settings['segments'])
for i_seg in range(n_seg): 
    BLM['segment'][0,i_seg]=dict()
    BLM['segment'][0,i_seg]['segment_name']=settings['segments']['segment_name'][i_seg]
    BLM['segment'][0,i_seg]['pointer_nr']=settings['segments']['pointer nr'][i_seg]# this needs to be converted to integers still
    BLM['segment'][0,i_seg]['opto_kol']=settings['segments']['marker columns'][i_seg]# this needs to be converted to integers still
    BLM['segment'][0,i_seg]['side']=settings['segments']['side'][i_seg]
    BLM['segment'][0,i_seg]['circumference']=settings['segments']['circumference'][i_seg]
    BLM['segment'][0,i_seg]['gender']=settings['segments']['gender'][i_seg]
    BLM['segment'][0,i_seg]['blmforaxis']=settings['segments']['BLM from segments'][i_seg]    
    BLM['segment'][0,i_seg]['axis_function']=settings['segments']['ACS function'][i_seg]    

pointer= kp.ImportPointerFile(settings['pointerfilename']) 


