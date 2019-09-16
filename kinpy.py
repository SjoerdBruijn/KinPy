#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 11:21:36 2019

@author: Nick1
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import mpl_toolkits.axes_grid1
import matplotlib.widgets
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import CheckButtons
#<<<<<<< HEAD
from scipy import linalg
#=======
import pandas as pd
#>>>>>>> 9d8ff53a32d4f04a7f266ac9619ce0ad3a402027


#import pdb #for debugging
#pdb.set_trace()


##### CORE  #########
def fread(fid, nelements, dtype):
    """Equivalent to Matlab fread function"""
    if dtype is np.str:
        dt = np.uint8  # WARNING: assuming 8-bit ASCII for np.str!
    else:
        dt = dtype
    data_array = np.fromfile(fid, dt, nelements)
    data_array.shape = (nelements, 1)
    return data_array

def readndf(naam):
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
    aantal = items[0][0]*subitems[0][0]*numframes[0][0]    
    data = np.array(fread(fid,int(aantal),'float32'))
    data[data< -1e21] = np.nan
    data = data.reshape(int(numframes[0][0]),int(items[0][0]*subitems[0][0]))
    x = data[:,0::3]
    y = data[:,1::3]
    z = data[:,2::3]
    fid.close()
    return x,y,z,frequency[0][0]

def ImportPointerFile(pointerfilename): 
    n_markers= pd.read_csv(pointerfilename,skiprows=3,nrows=1,delimiter=';',header=None)
    pointer=pd.read_csv(pointerfilename,skiprows=6, nrows=n_markers[0][0], usecols=[1,2,3], delim_whitespace=True) 
    return pointer 

def xyz2dat(s1,s2,s3):
# omzetten van datastructuur:
#
#   van 3 matrices X, Y en Z van format  [X1  X2  Xk
#                                        ...........
#                                        X1m X2m Xkm]
#
# naar   [X1  Y1  Z1 .... Xk  Yk  Zk             met: k = aantal markers
#         .........................                   m = aantal samples
#        X1m Y1m Z1m ....Xkm Ykm Zkm ]
#
    data = np.empty([s1.shape[0],s1.shape[1]*3])
    data[:,0::3] = s1
    data[:,1::3] = s2
    data[:,2::3] = s3
    return data

def dat2xyz(data):
    x = data[:,0::3]
    y = data[:,1::3]
    z = data[:,2::3]
    return x,y,z

def prod_col(A,B):   
    mult_ord = (np.arange(9).reshape(3,3)).T
    C = np.zeros(B.shape)
    for i_col in range(B.shape[1]):
            Ai = mult_ord[int(i_col%3),:]
            Bi = np.array([0,1,2])+ int(3*np.floor(i_col/3))
            C[:,i_col] = np.sum(np.multiply(A[:,Ai],B[:,Bi]),axis=1)
    return C

def transpose_col(mat):
    Tmat = np.c_[mat[:,0::3],mat[:,1::3],mat[:,2::3]]
    return Tmat

def chgframe(ref1,ref2,data):
    # Create empty matrices
    R = np.ones([ref2.shape[0],9])*np.nan
    c1_tot= np.ones([ref2.shape[0],int(data.size/data.shape[0])])*np.nan
    c2_tot= c1_tot.copy()
    dat2est = data*np.nan
    # Create temporary ref1 and ref2
    ref1_temp = ref1[0,:].reshape(3,int(ref1.shape[1]/3))
    ref2_temp = ref2[0,:].reshape(3,int(ref2.shape[1]/3))*np.nan
    for i_t in range(ref2.shape[0]):
        # If ref1 has >1 sample, iterate along the matrix
        if ref1.shape[0]>1:
            ref1_temp = ref1[i_t,:].reshape(3,int(ref1.shape[1]/3))
        # reshape to 3x3 matrix
        ref2_temp = ref2[i_t,:].reshape(3,int(ref2.shape[1]/3))
        # find nans in data        
        innan = sum(np.isnan(np.add(ref1_temp,ref2_temp)))<1 #i not NaN
        # check whether there are 3 markers visible
        if sum(innan)>3:
            ref1_temp = ref1_temp[:,innan]
            ref2_temp = ref2_temp[:,innan]
        # length of new vector
        nref = ref1_temp.shape[1]
        # mean position of marker pos        
        c1 = np.mean(ref1_temp,axis=1)
        c2 = np.mean(ref2_temp,axis=1)
        # Perform least squares function to data (misshien hier ref2 nog transpose)
        G = np.matmul(ref2_temp-np.tile(c2,[nref,1]).T,(ref1_temp-np.tile(c1,[nref,1]).T).T)/nref
        # Get eigenvalues of the         
        mu = np.sort(linalg.eigvals(np.matmul(G.T,G)))**(.5)
        # Get sign of Det
        t = np.sign(linalg.det(G))
        # adjoint of a 3x3 matrix
        Gadj = adjoint(G)
        R_temp    = np.real(np.matmul((Gadj.T+(mu[2]+mu[1]+t*mu[0])*G),linalg.inv(np.matmul(G.T,G)+(mu[2]*mu[1]+t*mu[0]*(mu[2]+mu[1])) * np.eye(3))))
        R[i_t,:] = R_temp.T.reshape(1,9) 
        c1_tot[i_t,:] = np.tile(c1,[1,int(data.size/data.shape[0]/3)])
        c2_tot[i_t,:] = np.tile(c2,[1,int(data.size/data.shape[0]/3)])
    dat2est = c2_tot + prod_col(R,data-c1_tot)
    return R, dat2est
    
def adjoint(mat):# cofactor matrix of a 3x3 matrix
    adj = np.array((np.cross(mat[:,1],mat[:,2].T),np.cross(mat[:,2],mat[:,0]),np.cross(mat[:,0],mat[:,1])))
#    if abs(linalg.det(mat))>0.001:
#        cof = linalg.inv(mat).T*linalg.det(mat)
#    else:
#        cof = linalg.pinv(mat).T*linalg.det(mat)
    return adj

def calc_axis_col(dat):
    v0 = dat[:,3:6]-dat[:,0:3]
    v1_tmp = dat[:,3:6]-dat[:,6:9]
    v2 = np.cross(v0,v1_tmp)
    v1 = np.cross(v2,v0)
    v0_norm = v0/normcol(v0)
    v1_norm = v1/normcol(v1)
    v2_norm = v2/normcol(v2)
    R = np.c_[v0_norm,v1_norm,v2_norm]
    return R

def chgframe_col(ref1,ref2,*arg): # NK: Volgens mij is dit niet veel anders dan chgframe(_old); de least squares zal hierin gewoon de markers zijn . Of is dit gewoon computationeel sneller?
    c1 = np.c_[np.mean(ref1[:,0::3],axis=1),np.mean(ref1[:,1::3],axis=1),np.mean(ref1[:,2::3],axis=1)]
    c2 = np.c_[np.mean(ref2[:,0::3],axis=1),np.mean(ref2[:,1::3],axis=1),np.mean(ref2[:,2::3],axis=1)]
    R1 = calc_axis_col(ref1)
    R2 = calc_axis_col(ref2)
    R = prod_col(R2,transpose_col(R1))
    if len(arg)>0:
        dat2est = np.tile(c2,[1,int(arg[0].shape[1]/3)])+prod_col(R,arg[0]-np.tile(c1,[1,int(arg[0].shape[1]/3)]));    
    else:
        dat2est = np.ones([1,3])*np.NaN
    return R, dat2est

def normcol(dat):
    dat = np.sum(dat**2,axis=0)**.5
    return dat

######## MAIN ########

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

####### Plot 3d functions ########
def plot_3d(traj):
    class Player(FuncAnimation):
        def __init__(self, fig, func, frames=None, init_func=None, fargs=None,
                     save_count=None, mini=0, maxi=100, pos=(0.125, 0.92), **kwargs):
            self.i = 0
            self.min=mini
            self.max=maxi
            self.runs = True
            self.fig = fig
            self.func = func
            self.setup(pos)
            FuncAnimation.__init__(self,self.fig, self.update, frames=self.play(), 
                                               init_func=init_func, fargs=fargs,
                                               save_count=save_count, **kwargs )  
          
        def play(self):
            while self.runs:
                self.i = self.i+1
                if self.i > self.min and self.i < self.max:                  
                    yield self.i
                else:
                    self.stop()
                    yield self.i 
    
        def start(self, event=None):
            self.runs = True
            self.event_source.start()
    
        def stop(self, event=None):
            self.runs = False
            self.event_source.stop()
    
        def setup(self, pos):
            playerax = self.fig.add_axes([pos[0],pos[1], 0.64, 0.04])
            divider = mpl_toolkits.axes_grid1.make_axes_locatable(playerax)
           
            sax = divider.append_axes("right", size="80%", pad=0.05)
            fax = divider.append_axes("right", size="80%", pad=0.05)
            sliderax = divider.append_axes("right", size="500%", pad=0.07)
    
            self.button_stop = matplotlib.widgets.Button(sax, label='stop')
            self.button_forward = matplotlib.widgets.Button(fax, label='play')
    
            self.button_stop.on_clicked(self.stop)
            self.button_forward.on_clicked(self.start)
            self.slider = matplotlib.widgets.Slider(sliderax, '', 
                                                    self.min, self.max, valinit=self.i)
            self.slider.on_changed(self.set_pos)
    
            col = (0,0,0,0)
            rax = plt.axes([0.1, 0.2, 0.2, 0.6], facecolor=col )
            self.check = CheckButtons(rax, ('joints', 'blue', 'green'), (1,0,1))
            self.check.on_clicked(self.set_pos)

        def set_pos(self,i):
            self.i = int(self.slider.val)
            self.func(self)
    
        def update(self,i):
            self.slider.set_val(i)
    
    
    
    #https://stackoverflow.com/questions/41602588/matplotlib-3d-scatter-animations
    def update(tmp):
        i = tmp.i
        statuses = tmp.check.get_status()
        n_seg = traj[0,0]['segment'][0,:]['mass'].size
        
        #for i_seg in range(n_seg):
        comdata=np.zeros((n_seg,3))
        for i_seg in range(n_seg):
            comdata[i_seg,0]=traj[0,0]['segment'][0,i_seg]['com'][i,0]
            comdata[i_seg,1]=traj[0,0]['segment'][0,i_seg]['com'][i,1]
            comdata[i_seg,2]=traj[0,0]['segment'][0,i_seg]['com'][i,2]
       
        blmdata= np.zeros((0,3)) 
        for i_seg in range(n_seg):
            tmp_blm=traj[0,0]['segment'][0,i_seg]['blm'][i,:]
            tst= tmp_blm.reshape(int(tmp_blm.size/3),3)   
            blmdata=np.append(blmdata,tst, axis = 0)
            blmdata=np.append(blmdata,np.ones((1,3))*np.nan,axis=0)
        
        jointdata= np.zeros((0,3)) 
        if statuses[0]:
            for i_seg in range(n_seg):
                tmp_joint=traj[0,0]['segment'][0,i_seg]['joint'][i,:]
                tst= tmp_joint.reshape(int(tmp_joint.size/3),3)   
                jointdata=np.append(jointdata,tst, axis = 0)
                jointdata=np.append(jointdata,np.ones((1,3))*np.nan,axis=0)

        complot.set_data(comdata[:,0],comdata[:,1])#
        complot.set_3d_properties(comdata[:,2])
        
        blmplot.set_data(blmdata[:,0],blmdata[:,1])#
        blmplot.set_3d_properties(blmdata[:,2])
        
        jointplot.set_data(jointdata[:,0],jointdata[:,1])#
        jointplot.set_3d_properties(jointdata[:,2])
        
        return complot, blmplot, jointplot
    
    
    
    def set_axes_equal(ax):
        '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
        cubes as cubes, etc..  This is one possible solution to Matplotlib's
        ax.set_aspect('equal') and ax.axis('equal') not working for 3D.
    
        Input
          ax: a matplotlib axis, e.g., as output from plt.gca().
        '''
    
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()
    
        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)
    
        # The plot bounding box is a sphere in the sense of the infinity
        # norm, hence I call half the max range the plot radius.
        plot_radius = 0.5*max([x_range, y_range, z_range])
    
        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
    
    
    ## set up the figur
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    i=1
    
    n_seg = traj[0,0]['segment'][0,:]['mass'].size
    max_t=int(traj[0,0]['segment'][0,1]['com'].size/3)

    
    comdata=np.zeros((n_seg,3))
    for i_seg in range(n_seg):
        comdata[i_seg,0]=traj[0,0]['segment'][0,i_seg]['com'][i,0]
        comdata[i_seg,1]=traj[0,0]['segment'][0,i_seg]['com'][i,1]
        comdata[i_seg,2]=traj[0,0]['segment'][0,i_seg]['com'][i,2]
     
    blmdata= np.zeros((0,3)) 
    for i_seg in range(n_seg):
        tmp_blm=traj[0,0]['segment'][0,i_seg]['blm'][i,:]
        tst= tmp_blm.reshape(int(tmp_blm.size/3),3)   
        blmdata=np.append(blmdata,tst, axis = 0)
        blmdata=np.append(blmdata,np.ones((1,3))*np.nan,axis=0)
    
    jointdata= np.zeros((0,3)) 
    for i_seg in range(n_seg):
        tmp_joint=traj[0,0]['segment'][0,i_seg]['joint'][i,:]
        tst= tmp_joint.reshape(int(tmp_joint.size/3),3)   
        jointdata=np.append(jointdata,tst, axis = 0)
        jointdata=np.append(jointdata,np.ones((1,3))*np.nan,axis=0)
    

     
    complot,    =ax.plot(comdata[:,0],comdata[:,1],comdata[:,2],linestyle="", marker="o")
    blmplot,    =ax.plot(blmdata[:,0],blmdata[:,1],blmdata[:,2])
    jointplot,  =ax.plot(jointdata[:,0],jointdata[:,1],jointdata[:,2])
    
    set_axes_equal(ax)
    
    ani = Player(fig, update, maxi=max_t,interval=50)

