#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 23:11:01 2020

@author: jguterl
"""
from UEDGEToolBox.DataManager.DataParser import UBoxDataParser
from UEDGEToolBox.Plot.Plotter import UBoxPlotter
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
class UBoxPlotTest(UBoxDataParser):
    def __init__(self,Verbose=False):
        self.DataPlot={}
    #Plot('Te')
    
    def Plot(self,DataFields=None,Replot=True,**kwargs):
        
        if DataFields is not None and DataFields!=[]: 
            self.AddDataPlot(DataFields,**kwargs)
            
        self.ShowPlot(**kwargs)
            
        if not Replot:
            if DataFields is not None and DataFields!=[]:
                self.ResetDataPlot()
            else:
                raise IOError('Cannot reset DataPlot when no data fields are given')
        
               
    def AddDataPlot(self,DataFields=[],**kwargs):
        if not hasattr(self,'DataPlot'):
            self.DataPlot={}
        Data=self.ParseDataFields(DataFields,**kwargs)
        for (Name,Dic) in Data.items():
            self.DataPlot[Name]=UBoxPlotter(Dic=Dic,Grid=self.GetGrid(),Tag=self.GetTag(),**kwargs)
            
    def ShowPlot(self,**kwargs):
        Nplot=len(list(self.DataPlot.keys()))
        fig, axs =self.FigLayout(Nplot)
        
        for (Name,Plotter),ax in zip(self.DataPlot.items(),axs.flat):
            print('Plotting "{}" on {} ...'.format(Name,ax))
            Plotter.ax=ax
            Plotter.Plot(**kwargs)
            
            
    @staticmethod       
    def SetNxNy(Nplot):
        Np   =[1,2,3,4,5,6,7,8,9,10]
        Nx   =[1,1,1,2,2,2,2,2,2,2]
        Ny   =[1,2,3,2,3,3,4,4,5,5]
        return (Nx[Np.index(Nplot)],Ny[Np.index(Nplot)])
    
    def FigLayout(self,Nplot,pad=1):
        
        (Nx,Ny)=self.SetNxNy(Nplot)
        # fig, axs = plt.subplots(Nx, Ny, sharex='col', sharey='row',
        #                 gridspec_kw={'hspace': 0, 'wspace': 0})
        fig, axs = plt.subplots(Nx, Ny)
        fig.tight_layout(pad=pad)
        if type(axs)!=np.ndarray: axs=np.array([axs])
        for ax in axs.flat:
            ax.set_visible(False)
        return fig,axs
    
    
    def SetAspect(self,*args):
        for Plotter in self.DataPlot.values():
            if Plotter.ax is not None:
                Plotter.ax.set_aspect(*args)
                #,adjustable='datalim'