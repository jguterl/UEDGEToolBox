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
from mpl_toolkits.axes_grid1 import ImageGrid
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import pyplot as plt
import numpy as np
class UBoxPlotTest(UBoxDataParser):
    DataPlot={}
    def __init__(self):
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
        
        
        for (NameData,DicData) in Data.items():
            NameDataPlot=NameData
            if DicData.get('Data') is not None and Grid is not None:
                if not Refresh:
                    i=1
                    while self.DataPlot.get(NameDataPlot) is not None:
                        NameDataPlot=NameDataPlot+'_#'+str(i)
                        i=i+1
                DicPlotter=self.PreparePlotter(DicData,Grid,Tag,NameDataPlot,NameData,**kwargs)
                self.DataPlot[NameDataPlot]=UBoxPlotter(**DicPlotter)
            else:
                print('Cannot add plot for the datafield {}'.format(NameDataPlot))
    
    @ClassInstanceMethod
    def PreparePlotter(self,DicData,Grid,Tag,NameDataPlot,NameData,**kwargs):
        DicPlotter=DicData
        DicPlotter['Grid']=Grid
        DicPlotter['Tag']=Tag
        DicPlotter['NameData']=NameData
        DicPlotter['NameDataPlot']=NameDataPlot
        DicPlotter.update(kwargs)
        
        if kwargs.get('PlotLabel') is None:
            DicPlotter['PlotLabel']=NameData
            
        if kwargs.get('PlotTitle') is None:
            Project=Tag.get('Project')
            CaseName=Tag.get('CaseName')
            PlotTitle=[]
            if Project is not None:
                PlotTitle.append(Project)
            if CaseName is not None:
                PlotTitle.append(CaseName)
            if PlotTitle != []:
                DicPlotter['PlotTitle']=':'.join(PlotTitle)    
            
        return DicPlotter
             
    @ClassInstanceMethod         
    def ShowPlot(self,TightLayout=True,**kwargs):
        Nplot=len(list(self.DataPlot.keys()))
        self.fig, self.axs=self.FigLayout(Nplot,**kwargs)
        count=1
        for (Name,Plotter),ax in zip(self.DataPlot.items(),self.axs.flat):
            print('Plotting "{}" ...'.format(Name))
            Plotter.ax=ax
            Plotter.IsBottom=self.IsBottom(count,self.Nx,self.Ny)
            Plotter.IsLeft=self.IsLeft(count,self.Nx,self.Ny)
            Plotter.Plot(**kwargs)
            count += 1
        self.LinkAxis(**kwargs)
        if TightLayout:
            plt.tight_layout()
        
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
            Nrow=int(np.ceil(Nplot/Ncol))
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
    def FigLayout(self,Nplot,pad=0.5,**kwargs):
        
        (self.Nx,self.Ny)=self.SetNxNy(Nplot,**kwargs)
        # fig, axs = plt.subplots(Nx, Ny, sharex='col', sharey='row',
        #                 gridspec_kw={'hspace': 0, 'wspace': 0})
        fig, axs = plt.subplots(self.Nx, self.Ny)
        #fig.tight_layout(pad=pad)
        if type(axs)!=np.ndarray: axs=np.array([axs])
        #=[]
        for ax in axs.flat:
            ax.set_visible(False)
            # divider = make_axes_locatable(ax)
            # caxs.append(divider.append_axes('right', size='10%', pad=0.6)) 
        # axs = ImageGrid(fig, 111,          # as in plt.subplot(111)
        #          nrows_ncols=(self.Nx,self.Ny),direction='column',
        #          axes_pad=0.10,
        #          share_all=True,
        #          cbar_location="right",
        #          cbar_mode="each",
        #          cbar_size="7%",
        #          cbar_pad=0.15,
        #          label_mode='1',
        #          cbar_set_cax=True
        #          )
        
        return fig,axs
    
    
    def SetAspect(self,*args):
        for Plotter in self.DataPlot.values():
            if Plotter.ax is not None:
                Plotter.ax.set_aspect(*args)
                #,adjustable='datalim'
                
    @ClassInstanceMethod            
    def ShareAxis(self,Axis='xy',PlotType='2D'):
        Plotter=[P for P in self.DataPlot.values() if P.PlotType == PlotType]
        axesPlotter=[P.ax for P in Plotter]  
        if (len(axesPlotter))>0:
            for P in Plotter:
                if 'x' in Axis.lower(): 
                    P.SetSharedXAxis(axesPlotter[0])
                    
                if 'y' in Axis.lower(): 
                    P.SetSharedYAxis(axesPlotter[0])
                    P.ax.set_ylim(axesPlotter[0].get_ylim())
                    if not P.IsLeft:
                        P.ax.set_ylabel(None)
                        plt.setp(P.ax.get_yticklabels(),visible=False)
                        
    @ClassInstanceMethod            
    def ShareCLim(self,**kwargs):
        Plotter = [P for P in self.DataPlot.values() if P.PlotType == '2D']
        axesPlotter = [P.ax for P in Plotter]  
        clow=np.array([P.PlotHandle.get_clim()[0] for P in Plotter])
        chigh=np.array([P.PlotHandle.get_clim()[1] for P in Plotter])
        cmin=min(clow)
        cmax=max(chigh)
        for P in Plotter:
            [P.PlotHandle.set_clim([cmin,cmax]) for P in Plotter]
            
    
    @ClassInstanceMethod            
    def LinkAxis(self,Axis='xy',PlotType='all',ShareCLim=True,**kwargs):
        if PlotType=='all':
            self.ShareAxis(Axis,PlotType='1D')
            self.ShareAxis(Axis,PlotType='2D')
        elif PlotType == '1D':
            self.ShareAxis(Axis,PlotType='1D')
        elif PlotType == '2D':
            self.ShareAxis(Axis,PlotType='2D')
        else:
            raise KeyError('PlotType must be: "all", "1D" or "2D"')
        if ShareCLim:
            self.ShareCLim(**kwargs)              

    @staticmethod
    def IsBottom(i,Nx,Ny):
        if int(np.ceil(i/Ny)) == Nx:
            return True
        else:
            return False
    @staticmethod
    def IsLeft(i,Nx,Ny):
        if np.mod(i,Ny) == 1:
            return True
        else:
            return False