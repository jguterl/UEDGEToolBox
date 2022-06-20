#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 14:29:38 2021

@author: guterlj
"""
from matplotlib.pylab import plt
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod, SetClassArgs
from uedge import bbb, com
import time
plt.ion()
class UBoxLivePlot():
    def __init__(self,*args,**kwargs):
        super().__init__()
        
        print('Liveplot 12------------------------------')
        self.liveplot = False
        self.ax_dens = None
        self.ax_flx = None
        self.plot_list = ['Gdes_l','Gdes_r','inflx']
        self.plot_dens_list = ['dens']
        self.plt_obj_flx = {}
        self.plt_obj_dens = {}
        self.plot_dens_ylim = [1e9,1e25]
        self.plot_flx_ylim = [1e15,1e22]
        self.plot_flx_xlim = []
        
            
            
    def init_plots(self):
        fig,axes = plt.subplots(3,1)
        self.ax_dens = axes[0]
        self.ax_up = axes[1]
        self.ax_t = axes[2]
        
        self.ax_up.set_xlabel('z [m]')
        self.ax_dens.set_xlabel('z [m]')
        self.ax_t.set_xlabel('z [m]')
        
        self.ax_dens.set_ylabel('n [m^-3]')
        self.ax_t.set_ylabel('T [eV]')
        self.ax_up.set_ylabel('up [m.s^-1]')

    def plot_livedata(self):
        
        if self.ax_dens is None:
            self.init_plots()
            
        if not self.plt_obj_dens:
            self.plt_obj_dens['ni'] = self.ax_dens.plot(self.livedata['zm'][:,1,0],self.livedata['ni'][self.iter_data,:,1,0],label='ni')
            self.plt_obj_dens['ng'] = self.ax_dens.plot(self.livedata['zm'][:,1,0],self.livedata['ng'][self.iter_data,:,1,0],label='ng')
            self.plt_obj_dens['te'] = self.ax_t.plot(self.livedata['zm'][:,1,0],self.livedata['te'][self.iter_data,:,1],label='te')
            self.plt_obj_dens['ti'] = self.ax_t.plot(self.livedata['zm'][:,1,0],self.livedata['ti'][self.iter_data,:,1],label='ti')
            self.plt_obj_dens['up'] = self.ax_up.plot(self.livedata['zm'][:,1,0],self.livedata['up'][self.iter_data,:,1,0],label='up')
        else:
            self.plt_obj_dens['ni'][0].set_ydata(self.livedata['ni'][self.iter_data,:,1,0])
            self.plt_obj_dens['ng'][0].set_ydata(self.livedata['ng'][self.iter_data,:,1,0])
            self.plt_obj_dens['te'][0].set_ydata(self.livedata['te'][self.iter_data,:,1])
            self.plt_obj_dens['ti'][0].set_ydata(self.livedata['ti'][self.iter_data,:,1])
            self.plt_obj_dens['up'][0].set_ydata(self.livedata['up'][self.iter_data,:,1,0])
                   
        self.ax_dens.set_title('iteration:{} ; time:{:3.3e}; dt={:3.3e}'.format(self.iter,bbb.dt_tot,bbb.dtreal))         
 
    def plot_live(self):

        if self.liveplot and self.data_collected:
                self.plot_livedata()
                self.ax_dens.figure.canvas.draw()
                self.ax_dens.figure.canvas.flush_events()
                time.sleep(0.1)