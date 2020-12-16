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
        if not hasattr(cls, '_Plot'):
            setattr(cls,'_Plot',[])

            for m in dir(matplotlib.lines.Line2D):
                if m.startswith('set_'):
                    cls._Plot.append(m.split('set_')[1])
        return cls._Plot

    @classmethod
    def Legend(cls):
        if not hasattr(cls, '_Legend'):
            setattr(cls,'_Legend',[])

            for m in dir(matplotlib.legend.Legend):
                if m.startswith('set_'):
                    cls._Legend.append(m.split('set_')[1])
        return cls._Legend

    @classmethod
    def Axes(cls):
        if not hasattr(cls,'_Axes'):
            setattr(cls,'_Axes',[])
        for m in dir(matplotlib.axes.Axes):
            if m.startswith('set_'):
                cls._Axes.append(m.split('set_')[1])
        return cls._Axes

class UBoxPlotUtils(UBoxDataParser):

    @staticmethod
    def PlotKw(*args, **kwargs):
        L = MatplotlibKw.Plot()
        return dict((k, v) for (k, v) in kwargs.items() if k in L and type(v) != dict)

    @staticmethod
    def LegendKw(*args, **kwargs):
        L = MatplotlibKw.Legend()
        L.append('ncol')
        return dict((k, v) for (k, v) in kwargs.items() if k in L and type(v) != dict)

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

def SetPlotType(Data,Type='auto'):

    if Data is None:
        raise ValueError('Data cannot be none')
    elif type(Data) != np.ndarray:
        raise ValueError('Data for Plotter must be a numpy array')
    elif len(Data.shape) > 2 and Data.shape[2] > 1:
        raise ValueError('Plotter object cannot contain arrays of dimension>2')

    DataDim = len(np.squeeze(Data).shape)
    Type=Type.strip()
    if Type.lower() == 'auto':
        if DataDim == 1:
            PlotType ='1D'
            AxisType ='r'
        else:
            PlotType ='2D'
            AxisType ='rz'

    elif Type.strip().lower() in ['r', 'z', 'psi', 'p', 'ix', 'iy']:
        PlotType = '1D'
        AxisType=Type.lower()

    elif Type.strip().lower() in ['ij', 'rz']:
        if DataDim < 2:
            raise ValueError ('2D plot requested for data array of dimension <2')
        else:
            PlotType = '2D'
            AxisType=Type.lower()
    else:
        raise ValueError('Type of plot must be: auto,rz,ij,r, z, psi, p, ix, iy')

    return (PlotType,AxisType)