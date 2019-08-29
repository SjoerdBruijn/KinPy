#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 11:21:36 2019

@author: Nick1
"""

import numpy as np

def fread(fid, nelements, dtype):
    """Equivalent to Matlab fread function"""
    if dtype is np.str:
        dt = np.uint8  # WARNING: assuming 8-bit ASCII for np.str!
    else:
        dt = dtype
    data_array = np.fromfile(fid, dt, nelements)
    data_array.shape = (nelements, 1)
    return data_array

#class
#def __init__(dat,x,y,z,frequency)

def readndf(naam):
    import pdb
    fid = open(naam,"rb")
    fread(fid,1,'uint8')
    items = fread(fid,1,'uint8')
    fread(fid,1,'uint8')
    subitems = fread(fid,1,'uint8')
    fread(fid,1,'uint8')
    numframes = fread(fid,1,np.dtype(np.int32))
    frequency = fread(fid,1,'float32')
    fread(fid,60,'uint8')
    fread(fid,183,'uint8')
#    print('items')
#    print(items[0][0])
#    print('subitems')
#    print(subitems[0][0])
#    print('numframes')
#    print(numframes[0][0])
#    print('frequency')
#    print(frequency[0][0])
    aantal = items[0][0]*subitems[0][0]*numframes[0][0]    
#    print(aantal)
    data = np.array(fread(fid,int(aantal),'float32'))
    data[data< -1e21] = np.nan
    data = data.reshape(int(numframes[0][0]),int(items[0][0]*subitems[0][0]))
#    data = data.T
#    pdb.set_trace()
#    print('length')
#    print(items[0][0]*subitems[0][0])
    x = data[:,0::3]
    y = data[:,1::3]
    z = data[:,2::3]
    fid.close()
    return x,y,z,frequency[0][0]


def calc_combined_com(traj):
    n_seg           = traj[0,0]['segment'][0,:]['mass'].size
    n_samples       = int(traj[0,0]['segment'][0,1]['com'].size/3.0)
    com_combined    = np.zeros((n_samples,3))
    mass_total      = 0
    for i_seg in range(n_seg):
        mass    = traj[0,0]['segment'][0,i_seg]['mass']
        com     = traj[0,0]['segment'][0,i_seg]['com']
        com_combined = com_combined+ mass*com
        mass_total  = mass_total+mass
    com_combined    = com_combined/mass_total
    return com_combined

