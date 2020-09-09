#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 01:08:49 2020

@author: jguterl
"""
from UEDGEToolBox.Plot.PlotUtils import UBoxPlotUtils,MatplotlibKw
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

class UBoxPlot1D(UBoxPlotUtils):
    def __init__(self):
        pass
    
    @staticmethod
    def CheckShape1DData(x,data):
        if len(data.shape)>1:
            return False
        if x is not None and len(x)!=data.shape[0]:
            return False
        else:
            return True
    
        
    def PlotSeparatrix(self,rm,zm,iysptrx,ax=None,color='r',linewidth=1,**kwargs):
       sepx=np.concatenate((rm[:,iysptrx,3],np.array([rm[-1,iysptrx,4]])))
       sepy=np.concatenate((zm[:,iysptrx,3],np.array([zm[-1,iysptrx,4]])))
       
       if ax is None:
           ax=plt.gca()
       ax.plot(sepx,sepy,color=color,linewidth=linewidth,**kwargs)
       
    def PlotData1D(self,x,data,Label=None,ShowLegend=True,**kwargs):
        ax=self.GetAx(**kwargs)
        p=ax.plot(x,data,**self.PlotKw(**kwargs))
        if Label is not None:
            if type(Label)!=list:
                Label=[Label]
            for pp,l in zip(p,Label):
                pp.set_label(l)
        ax.legend().set_visible(ShowLegend)
        return p
    
    @staticmethod
    def PlotKw(*args,**kwargs):
        L=MatplotlibKw.Plot()
        return dict((k,v) for (k,v) in kwargs.items() if k in L)

        
    def Check1DDim(XData,Data):
        if type(XData)==np.ndarray and len(XData.shape)>1:
                return False
        if type(Data)==np.ndarray and len(Data.shape)>1:
                return False
        return True
        
        
                    
    def PickLabel(self,Grid):
         if len(Grid.shape)>1:
            if Grid.shape[0]==1:
                XLabel='Z [m]'
                YLabel=None
            elif Grid.shape[1]==1:
                XLabel='R [m]'
                YLabel=None
            else:        
             XLabel='R [m]'
             YLabel='Z [m]'
             
         return (XLabel,YLabel)
     
    
    
    
    
    
    
    