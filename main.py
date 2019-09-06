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

eye = np.eye(3,k=0)
eye = eye.reshape([1,9])
eye = np.r_[eye,eye,eye,eye,eye]
D = np.ones([5,9])*np.arange(9).T+1


A = np.array([(1,2,3,4,5,6,7,8,9),([1,2,3,4,5,6,7,8,9])])
B = np.array([(9,8,7,6,5,4,3,2,1),(9,8,7,6,5,4,3,2,1)])
kp.prod_col(A,B)

eye2 = np.eye(3,k=0)
eye2 = eye2.reshape([1,9])
eye2 = np.r_[eye2,eye2,eye2,eye2,eye2]
eye2[0,1] = 2 
R,D2 = kp.chgframe(eye2,eye,D)
#R = kp.chgframe(eye,eye,dat[0:5:1,0:9:1])

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