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
import numpy.maltib


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
    
    
    
    
    #ani = Player(fig, update, maxi=100,interval=20)
    
    #plt.show()