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


#import pdb #for debugging
#pdb.set_trace()

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
    mult_ord = np.arange(9).reshape(3,3)
    C = np.zeros(B.shape)
    for i_col in range(B.shape[1]):
        if B.shape[1]==3:
            C[:,i_col] = np.sum(np.multiply(A[:,mult_ord[i_col,:]],B),axis=1)
        elif B.shape[1]==9:
            C[:,i_col] = np.sum(np.multiply(A[:,mult_ord[int(np.floor(i_col/3)),:]],B[:,mult_ord[:,int(i_col%3)]]),axis=1)
    return C
    
    

def plot_3d(traj):
    class Player(FuncAnimation):
        def __init__(self, fig, func, frames=None, init_func=None, fargs=None,
                     save_count=None, mini=0, maxi=100, pos=(0.125, 0.92), **kwargs):
            self.i = 0
            self.min=mini
            self.max=maxi
            self.runs = False
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
            yield self.i
    
        def start(self, event=None):
            self.runs=True
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

