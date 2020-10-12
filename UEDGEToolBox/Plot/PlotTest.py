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
    def Plot(self,DataFields=None,Reset=False,**kwargs):
        if Reset:
            self.ResetPlot()
            
        if DataFields is not None and DataFields!=[]: 
            self.AddPlot(DataFields,**kwargs)
            
        self.ShowPlot(**kwargs)
            
        # if not Replot:
        #     if DataFields is not None and DataFields!=[]:
        #         self.ResetPlot()
        #     else:
        #         raise IOError('Cannot reset DataPlot when no data fields are given')
        
    @ClassInstanceMethod            
    def AddPlot(self,DataFields=[],DataType='UEDGE',Refresh=True,**kwargs):
        if not hasattr(self,'DataPlot'):
            print('Adding DataPlot attribute')
            self.DataPlot={}
        
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
                if not Refresh:
                    i=1
                    while self.DataPlot.get(Name) is not None:
                        Name=Name+'_#'+str(i)
                        i=i+1
                
                self.DataPlot[Name]=UBoxPlotter(Dic=Dic,Grid=Grid,Tag=Tag,**kwargs)
            else:
                print('Cannot add plot for the datafield {}'.format(Name))
                
    @ClassInstanceMethod         
    def ShowPlot(self,**kwargs):
        Nplot=len(list(self.DataPlot.keys()))
        fig, axs =self.FigLayout(Nplot,**kwargs)
        
        for (Name,Plotter),ax in zip(self.DataPlot.items(),axs.flat):
            print('Plotting "{}" on {} ...'.format(Name,ax))
            Plotter.ax=ax
            Plotter.Plot(**kwargs)
            
        plt.show()    
    @staticmethod       
    def SetNxNy(Nplot,Nrow=None,Ncol=None,**kwargs):
        if Nplot==0:
            return (1,1)
        
        Np   =[1,2,3,4,5,6,7,8,9,10,11,12]
        Nx   =[1,1,1,2,2,2,2,2,2,2,3,3]
        Ny   =[1,2,3,2,3,3,4,4,5,5,4,4]
        if Ncol is None and Nrow is not None and Nrow>0:
            Ncol=int(np.ceil(Nplot/Nrow))
            return (Nrow,Ncol)
        elif Nrow is None and Ncol is not None and Ncol>0:
            Nrow=int(ceil(Nplot/Ncol))
            return (Nrow,Ncol)
        elif Nrow is not None and Ncol is not None:
            if Nplot>Nrow*Ncol:
                raise IOError('Nplot>Nrow*Ncol')
            return (Nrow,Ncol)
        else:
            if Nplot>12:
                raise IOError('Cannot plot more than 12 plots on the same figure... Type ResetPlot() to clear plot')
            else:
                return (Nx[Np.index(Nplot)],Ny[Np.index(Nplot)])
        
        
            
        
    
    @ClassInstanceMethod
    def FigLayout(self,Nplot,pad=1,**kwargs):
        
        (Nx,Ny)=self.SetNxNy(Nplot,**kwargs)
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