#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
Created on Tue Sep  1 21:37:32 2020
 
@author: jguterl
"""
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod,SetClassArgs 
from UEDGEToolBox.Plot.PlotUtils import UBoxPlotUtils,MatplotlibKw
from UEDGEToolBox.Plot.Plot1D import UBoxPlot1D
from UEDGEToolBox.Plot.Plot2D import UBoxPlot2D
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

#@UBoxPreFix()   
class UBoxPlotter(UBoxPlot2D,UBoxPlot1D,UBoxPlotUtils):
 
    def __init__(self,**kwargs):
        self.Grid=kwargs.get('Grid')
        self.Data=kwargs.get('Data')
        self.zshift=kwargs.get('zshift')
        self.rshift=kwargs.get('rshift')
        self.Indexes=kwargs.get('Indexes')
        self.DataPlotName=kwargs.get('DataPlotName')
        self.DataName=kwargs.get('DataName')
        self.Label=kwargs.get('Label')
        self.Tag=kwargs.get('Tag')
        self.OriginalShape=kwargs.get('OriginalShape')
        self.ax=kwargs.get('ax')
        self.cax=kwargs.get('cax')
        if kwargs.get('Verbose') is None:
            self.Verbose=False
        else:
            self.Verbose=kwargs.get('Verbose')
        self.XType=kwargs.get('XType')
        self.PlotLabel=kwargs.get('PlotLabel')
        self.PlotTitle=kwargs.get('PlotTitle')
        self.PlotType=None
        self.XLabel=None
        self.YLabel=None
           
    

   
    def CheckDataDim(self,Data):
        if Data is not None:
                if type(Data)!=np.ndarray:
                    return 'Data for Plotter must be a numpy array'
                if len(Data.shape)>2 and Data.shape[2]>1:
                    return 'Plotter object cannot contain arrays of dimension>2'
        return True
    

    def SetAxProperties(self,**kwargs):
        if self.ax is not None:
            List=MatplotlibKw.Axes()
            Dic=dict((k,v) for (k,v) in kwargs.items() if k in List)
            for (k,v) in Dic.items():
                if hasattr(self.ax,'set_{}'.format(k)):
                    getattr(self.ax,'set_'+k)(v)
                    
            
            
    def Plot(self,**kwargs):
        
            
        if self.Grid is None:
            return 'No grid loaded in plotter object. Cannot plot'
        
        
        #self.BuildLabelPlot(**kwargs)
        DataDim=self.GetDim(self.Data)
        if self.Verbose: print('PlotData:DataDim:{}, Label:{},Data:{} Grid:{}' .format(DataDim,self.Label,self.Data.shape,self.Grid['rm'].shape))
        if DataDim==1:
            self.PlotHandle = self.Plotter1D(**kwargs)
            self.PlotType ='1D'
        elif DataDim==2:
            self.PlotHandle = self.Plotter2D(**kwargs)
            self.PlotType = '2D'
        elif DataDim>2:
            print('Cannot plot data in more than two dimensions.')  
            self.PlotHandle = None
            self.PlotType = None
        elif DataDim<1:
            print('Cannot plot empty data.')  
            self.PlotHandle = None
            self.PlotType = None
        self.SetPlotLabel(**kwargs)
        self.SetPlotTitle(**kwargs)
        self.SetXLabel(**kwargs)
        self.SetXLabel(**kwargs)
        self.SetAxProperties(**kwargs)
    # def GetData(Name):
        
    # def PlotSingle2D(self,DataField,Grid=None,ax=None,ColorMap='jet',DataLim=None,DataScale='linear',fig=None):
    #     Grid=self.GetGrid()
    #     self.PlotData2DBase(Grid['rm'],Grid['zm'],self.GetData(DataField),ax,ColorMap,DataLim,DataScale)    
    
    
    def PreparePlot1DData(self,XType=None,DimSplit=None):
        (DimSplit,XType)=self.GetDimSplit(XType,DimSplit,self.Data)

        if self.Verbose: print('Preparing 1D for for XType:{} ; DimSplit={}'.format(XType,DimSplit))   
        DataSplit=self._SplitDataArray(self.Data,DimSplit)
        IndexesSplit=self._SplitIndexes(self.Indexes,DimSplit)
        if self.Verbose: print('IndexesSplit={}'.format(IndexesSplit))         
        # Now we get the grid for each Data 

        DataOut=[]
        XDataOut=[]
        LabelOut=[]
        for I,D in zip(IndexesSplit,DataSplit): 
            XData=self.GetXData(self.Grid,XType,Indexes=I)
            XDataOut.append(XData.squeeze())
            DataOut.append(D.squeeze())
            if DimSplit is not None:
                LabelOut.append('_{}'.format(I[DimSplit]))
            else:
                LabelOut.append('')
            
            
        XDataOut=np.array(XDataOut).squeeze().transpose()
        DataOut=np.array(DataOut).squeeze().transpose()
        return (XDataOut,DataOut,LabelOut,XType)
    
    
    
    def Plotter1D(self,XType=None,DimSplit=None,**kwargs):
 
        (XDataOut,DataOut,LabelOut,XType)=self.PreparePlot1DData(XType,DimSplit)
        Labels=['{} {}={}'.format(self.Label,XType,L) for L in LabelOut] 
        if self.Verbose: print('Plot1D: XType:{},DataOut.shape:{} ; XDataOut.shape={}'.format(XType,DataOut.shape,XDataOut.shape))
        return self.PlotData1D(XDataOut,DataOut,Labels,**kwargs)
    
    def PreparePlot2DGrid(self,XType=None,**kwargs):
        if self.Grid is None:
            print('No grid available in plotter')
            return (None,None) 
        if XType=='ixiy':
            pass
        else:
            
            r=self.Grid.get('rm')
            z=self.Grid.get('zm')
            
            if self.zshift is not None:
                z=z+self.zshift
            if self.rshift is not None:
                r=r+self.rshift
                
            if z is None or r is None:
                return (None,None)
            else:
                r=self._SliceDataArray(r,self.Indexes[0:2])
                z=self._SliceDataArray(z,self.Indexes[0:2])
        return (r,z)
    
    def Plotter2D(self,**kwargs):
        
        (r,z)=self.PreparePlot2DGrid(**kwargs)
        if r is None or z is None:
            print('Problem with the grid in plotter. Grid:',self.Grid)
            return None
        else:
            PlotHandle = self.PlotData2D(r,z,self.Data,**kwargs)
            return PlotHandle

    def SetPlotLabel(self,PlotLabel=None,PlotLabelLocation:str or tuple='se',PlotLabelFontSize=10,**kwargs):
        if PlotLabel is None:
            PlotLabel = self.PlotLabel
        if self.ax is None:
           return 
                
        Pos=dict(se=(1,0),sw=(0,0),nw=(0,1),ne=(1,1))    
            
        if type(PlotLabelLocation)==str:
           PlotLabelLocation=Pos.get(PlotLabelLocation)
        PlotLabelLocation
        self.HandlePlotLabel=self.ax.text(PlotLabelLocation[0], PlotLabelLocation[1], PlotLabel,transform=self.ax.transAxes, fontsize=PlotLabelFontSize,verticalalignment='bottom',horizontalalignment='right')
        
        
        
    def SetXLabel(self,XLabel=None,XLabelFontSize=10,**kwargs):
        if XLabel is None:
            if self.XLabel is None:
                if self.PlotType == '2D':
                    self.XLabel='R [m]'
        else:
            self.XLabel=XLabel
        
        self.ax.set_xlabel(self.XLabel,fontsize=XLabelFontSize)
        
    def SetYLabel(self,YLabel=None,YLabelFontSize=10,**kwargs):
        if YLabel is None:
            if self.YLabel is None:
                if self.PlotType == '2D':
                    self.YLabel='R [m]'
        else:
            self.YLabel=YLabel
        
        self.ax.set_ylabel(self.YLabel,fontsize=YLabelFontSize)    
        
           
    def SetPlotTitle(self,PlotTitle=None,TitleFontSize=10,**kwargs):
        if PlotTitle is None:
            if self.PlotTitle is not None:
                PlotTitle = self.PlotTitle
            else:
                return
        if self.ax is None:
           return 
        else:
            self.ax.set_title(PlotTitle.TitleFontSize)
        
    
            
            # self.ax.set_title('{}:({},{})'.format(self.Label,self.CompactStr(self.Indexes[0]),self.CompactStr(self.Indexes[1])))
        
    
                    
    def GetAxProperties(self,Override=False):
        for P in self.AxProperties:
            Prop=getattr(self,P)
            if Prop is None:
                if self.ax is not None:
                    if hasattr(self.ax,'get_'+P):
                        f=getattr(self.ax,'get_'+P)
                        setattr(self,P,f())
    
    
    @staticmethod 
    def GetDim(Data):
        Dat=np.squeeze(Data)
        return len(Dat.shape)
            
            
    def SetupAx(self,Data,Label,ax=None,**kwargs):
        ax=self.GetAx(ax)
        Data=np.squeeze(Data)
        if kwargs.get('xlabel') is not None:
            ax.set_xlabel(kwargs.get('XLabel'))
            
    def SetGrid(self,Grid):
        self.Grid=Grid
        
    def SetSharedXAxis(self,ax):
        if not self.IsBottom:
            self.ax.set_xlabel(None)
            self.ax.xaxis.set_ticklabels([])
        if self.ax != ax:
            self.ax.get_shared_x_axes().join(self.ax, ax)
        self.ax.set_xlim(ax.get_xlim())
            
    
    def SetSharedYAxis(self,ax):
        if not self.IsLeft:
            self.ax.set_ylabel(None)
            self.ax.yaxis.set_ticklabels([])
        if self.ax != ax:
            self.ax.get_shared_y_axes().join(self.ax, ax)
        self.ax.set_ylim(ax.get_ylim())
            