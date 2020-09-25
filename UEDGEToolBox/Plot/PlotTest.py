#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 23:11:01 2020

@author: jguterl
"""
from UEDGEToolBox.DataManager.DataParser import UBoxDataParser
from UEDGEToolBox.DataManager.Grid import UBoxGrid
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod
from UEDGEToolBox.Plot.Plotter import UBoxPlotter

import matplotlib
from matplotlib import pyplot as plt
import numpy as np
class UBoxPlotTest(UBoxDataParser):
    DataPlot={}
    def __init__(self,Verbose=False):
        self.DataPlot={}

    @ClassInstanceMethod 
    def ResetPlot(self):
        self.DataPlot={}
    @ClassInstanceMethod     
    def Plot(self,DataFields=None,Replot=True,**kwargs):
        
        if DataFields is not None and DataFields!=[]: 
            self.AddDataPlot(DataFields,**kwargs)
            
        self.ShowPlot(**kwargs)
            
        if not Replot:
            if DataFields is not None and DataFields!=[]:
                self.ResetPlot()
            else:
                raise IOError('Cannot reset DataPlot when no data fields are given')
        
    @ClassInstanceMethod            
    def AddDataPlot(self,DataFields=[],DataType='UEDGE',**kwargs):
        if not hasattr(self,'DataPlot'):
            self.DataPlot={}
        # if type(DataType)==list:
        #     if type(DataFields)!=list or len(DataType)>len(DataFields):
        #         for D in DataType:
        #             self.AddDataPlot(DataFields=DataFields,DataType=D,**kwargs)
        #             return
                
        Data=self.ParseDataFields(DataFields,DataType=DataType,**kwargs)
        
        # Check the grid
        if kwargs.get('Grid') is not None:
            Grid=kwargs.pop('Grid')
        else:
            Grid=None
        
        if Grid is None:
            if hasattr(self,'GetGrid'):
                Grid=self.GetGrid()
        elif type(Grid)==str:
                Grid=UBoxGrid.ReadGridFile(Grid)
        
        if kwargs.get('Tag') is not None:
            Tag=kwargs.pop('Tag')
        else:
            Tag=None
            
        if Tag is None:
            if hasattr(self,'GetTag'):
                Tag=self.GetTag()
            else:
                Tag={}
        
        for (Name,Dic) in Data.items():
            if Dic.get('Data') is not None and Grid is not None:
                self.DataPlot[Name]=UBoxPlotter(Dic=Dic,Grid=Grid,Tag=Tag,**kwargs)
            else:
                print('Cannot add plot for the datafield {}'.format(Name))
                
    @ClassInstanceMethod         
    def ShowPlot(self,**kwargs):
        Nplot=len(list(self.DataPlot.keys()))
        fig, axs =self.FigLayout(Nplot)
        
        for (Name,Plotter),ax in zip(self.DataPlot.items(),axs.flat):
            print('Plotting "{}" on {} ...'.format(Name,ax))
            Plotter.ax=ax
            Plotter.Plot(**kwargs)
            
            
    @staticmethod       
    def SetNxNy(Nplot):
        Np   =[1,2,3,4,5,6,7,8,9,10,11,12]
        Nx   =[1,1,1,2,2,2,2,2,2,2,3,3]
        Ny   =[1,2,3,2,3,3,4,4,5,5,4,4]
        if Nplot>12:
            raise IOError('Cannot plot more than 12 plots on the same figure... Type ResetPlot() to clear plot')
        return (Nx[Np.index(Nplot)],Ny[Np.index(Nplot)])
    
    @ClassInstanceMethod
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