#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 01:18:45 2020

@author: jguterl
"""
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod,SetClassArgs
from matplotlib import pyplot as plt
from UEDGEToolBox.DataManager.DataParser import UBoxDataParser
import matplotlib
import numpy as np

class MatplotlibKw():
    
    @classmethod
    def Plot(cls):
        if not hasattr(cls,'_Plot'):
            setattr(cls,'_Plot',[])
        
            for m in dir(matplotlib.lines.Line2D):
                if m.startswith('set_'):
                    cls._Plot.append(m.split('set_')[1])
        return cls._Plot
    
    @classmethod
    def Axes(cls):
        if not hasattr(cls,'_Axes'):
            setattr(cls,'_Axes',[])
        for m in dir(matplotlib.axes.Axes):
            if m.startswith('set_'):
                cls._Axes.append(m.split('set_')[1])
        return cls._Axes
    
class UBoxPlotUtils(UBoxDataParser):
    
    @SetClassArgs
    def __init__(self):
        pass
    @ClassInstanceMethod 
    def GetAx(self,**kwargs):
        ax=kwargs.get('ax')
        if ax is None:
            if not hasattr(self,'ax') or self.ax is None:
                self.ax=plt.gca()
        else:
            self.ax=ax
        self.ax.set_visible(True)
        return self.ax
    
    def GetCAx(self,**kwargs):
        cax=kwargs.get('cax')
        if cax is None:
            if not hasattr(self,'cax') or self.cax is None:
                self.cax=None
        else:
            self.cax=cax
        self.cax.set_visible(True)
        return self.ax
    
    def CheckIndexes(self):
        if not hasattr(self,'Indexes'):
            self.Indexes={}
        if type(self.Data)==property:
            self.Data={}
        
        if not self.Indexes:
            if self.Verbose:print('Generating indexes from scratch for:',list(self.Data.keys()))
            for (k,D) in self.Data.items():
                self.Indexes[k]=self.ProcessArrayIndexes(D.shape)
                
    def CheckLabels(self):
        if not hasattr(self,'Labels'):
            self.Indexes={}
        if type(self.Data)==property:
            self.Data={}
        
        if not self.Labels:
            if self.Verbose:print('Generating labels from scratch for:',list(self.Data.keys()))
            for k in self.Data.keys():
                self.Labels[k]=k
                
        
    def SliceGrid(self,Grid=None):
        Grid=self.GetGridPlot(Grid)
        if Grid is None:
            return
        if not hasattr(self,'Grids'):
            self.Grids={}
        if self.Verbose: print('Slicing grid...')
        self.CheckIndexes()
        for k in self.Indexes.keys():
            Indexes=self.Indexes.get(k)
            if self.Verbose: print('Slicing grid for {} with Indexes:{}'.format(k,Indexes))

            self.Grids[k]=self._SliceGrid(Grid,Indexes)
    
    def _SliceGrid(self,Grid,Indexes):
        SlicedGrid={}
        for (k,v) in Grid.items():
            if type(v)==np.ndarray and len(v.shape)>1:
                if self.Verbose:
                    print('Slicing grid array: {} of shape {} with Indexes: {}'.format(k,v.shape,Indexes[0:2]))
                SlicedGrid[k]=self._SliceDataArray(v,Indexes[0:2])
            else:
                SlicedGrid[k]=v
        return SlicedGrid
    
    def GetGridPlot(self,Grid):
        if Grid is None:
            if hasattr(self,'Grid'):
                return self.Grid
            elif hasattr(self,'GetGrid'):
                self.GetGrid()
                return self.Grid
            else:
                return None
        else:
                return Grid
            
    def SetGridPlot(self,Grid=None):
        self.Grid=self.GetGridPlot(Grid)
        
    @staticmethod
    def SqueezeGrid(Grid):
        GridOut={}
        for (k,v) in Grid.items():
            if type(v)==np.ndarray:
                GridOut[k]=np.squeeze(v)
            else:
                GridOut[k]=v
        return GridOut
    
    @staticmethod
    def GetXLabel(XType:str):
        if XType is None:
            return None
        if XType.lower()=='r':
            return 'R [m]'
        if XType.lower()=='z' or XType.lower()=='p':
            return 'Poloidal length [m]'
        if XType.lower()=='c':
            return 'length [m]'
        if XType.lower()=='psi':
            return 'Psi'
        return XType
    
    def GetDimSplit(self,XType,DimSplit,Data):
        if XType is None:
            XType=self.GetXType(XType,Data)
        
        if DimSplit is None:
            if XType.lower()=='iy' or XType.lower()=='r' or XType.lower()=='psi':
                DimSplit=0
            elif XType.lower()=='ix' or XType.lower()=='p' or XType.lower()=='z':
                DimSplit=1 
            else:
                return (None,None)
        else:    
            if (XType.lower()=='ix' or XType.lower()=='p' or XType.lower()=='z') and DimSplit!=1:
                return (None,None)
            elif (XType.lower()=='iy' or XType.lower()=='r' or XType.lower()=='psi') and DimSplit!=0:
                    return (None,None)
                
        return (DimSplit,XType)

    
    
    def GetXType(self,XType=None,Data=None):
        if XType is None and Data is not None:
                Dim=Data.shape
                if len(Dim)<2:
                    XType='l'
                 #look up dimension of Data
                elif Dim[0]==1:
                     XType='iy'
                elif Dim[1]==1:
                     XType='ix'
                elif np.nanargmin(Dim[0:2])==0:
                         XType='iy'
                elif np.nanargmin(Dim[0:2])==1:
                         XType='ix'
        return XType
    
    
    def GetXData(self,Grid,XType=None,Indexes=None,Idx=0):
        XData=None
        if self.Verbose: print('Grid["rm"] shape:',Grid['rm'].shape)
        if Grid.get('rm') is None or Grid.get('zm') is None:
            return None
        
        if XType is None:
            return None
        
        if XType.lower()=='ix':
               XData=np.indices(Grid['rm'].shape)[0]
        
        if XType.lower()=='iy':
               XData=np.indices(Grid['rm'].shape)[1]
        
               
        if XType.lower()=='r':
               XData=Grid['rm']
               
        if XType.lower()=='z' or XType.lower()=='p':
               XData=Grid['zm']
        
        if XType.lower()=='psi':
                if Grid.get('psinorm') is not None:
                    XData=Grid['psinorm'] 
                elif Grid.get('psinc') is not None:
                    XData=Grid['psinc'] 
                else:
                    return None
        if self.Verbose:print('XData:',XData,'Indexes:',Indexes)
        if Indexes is not None and XData is not None: 
            if XType.lower()=='psi':
                XData=XData[Indexes[1]]
            else:
                XData=self._SliceDataArray(XData,Indexes[0:2])
                XData=XData[...,Idx]
            
        
        return XData

    def CompactStr(self,array):
        N=array.size
        Follow=False
        L=['{},'.format(array[0])]
        
        for i in range(1,N-1):
            if array[i]-array[i-1]!=1 or array[i+1]-array[i]!=1:
                Follow=False
                L.append('{},'.format(array[i]))
            else:
                if not Follow:
                    L.append(':')
                    Follow=True
        L.append('{}'.format(array[-1]))
        Out=''.join(L)
        return '[{}]'.format(Out.replace(',:',':'))
    
    
    def BuildLabelPlot(self,ExtraLabel=None,**kwargs):
        if hasattr(self,'Tag') and type(self.Tag)==dict:
            Project=self.Tag['Project']
            CaseName=self.Tag['CaseName']
        else:
            Project='?'
            CaseName='?'
            
        self.LabelPlot='{}:{} \n {}'.format(Project,CaseName,self.Label)
        if ExtraLabel is not None:
            self.PlotLabel='{} \n {}'.format(self.LabelPlot,ExtraLabel)    
            