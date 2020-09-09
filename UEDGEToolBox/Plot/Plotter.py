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


class UBoxPlotter(UBoxPlot2D,UBoxPlot1D,UBoxPlotUtils):
 
    def __init__(self,Dic={},Verbose=True,**kwargs):
        self.Grid=kwargs.get('Grid')
        self.Data=kwargs.get('Data')
        self.Indexes=kwargs.get('Indexes')
        self.Label=kwargs.get('Label')
        self.Label=kwargs.get('Tag')
        self.OriginalShape=kwargs.get('OriginalShape')
        self.ax=kwargs.get('ax')
        self.Verbose=kwargs.get('Verbose')
        self.XType=kwargs.get('XType')
        self.LabelPlot=''
        self.ImportDic(Dic)
        
        # for (k,v) in kwargs.items():
        #     if hasattr(self,k):
        #         set(self,k,v)
           
        
    def ImportDic(self,Dic):
        
        if type(Dic)==dict:
            Data=Dic.get('Data')
            Indexes=Dic.get('Indexes')
            OriginalShape=Dic.get('OriginalShape')
            Label=Dic.get('Label')
            
            if Data is not None:
                self.Data=Data
            else:
                self.Data=None
                
            if Indexes is not None:
                self.Indexes=Indexes
            else:
                self.Indexes=None
                
            if OriginalShape is not None:
                self.OriginalShape=OriginalShape
            else:
                self.OriginalShape=None
                
            if Label is not None:
                self.Label=Label
            else:
                self.Label=None

   
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
            print(List)
            print(kwargs)
            Dic=dict((k,v) for (k,v) in kwargs.items() if k in List)
            for (k,v) in Dic.items():
                if hasattr(self.ax,'set_{}'.format(k)):
                    print('ax attr:',k)
                    getattr(self.ax,'set_'+k)(v)
                    
            
            
    def Plot(self,**kwargs):
        
        
        XType=kwargs.get('XType')
            
        if self.Grid is None:
            return 'No grid loaded in plotter object. Cannot plot'
        
        
        self.BuildLabelPlot(**kwargs)
        DataDim=self.GetDim(self.Data)
        if self.Verbose: print('PlotData:DataDim:{}, Label:{},Data:{} Grid:{}' .format(DataDim,self.Label,self.Data.shape,self.Grid['rm'].shape))
        if DataDim==1:
            self.Plotter1D(XType=XType,**kwargs)
        elif DataDim==2:
            self.Plotter2D(**kwargs)
        elif DataDim>2:
            print('Cannot plot data in more than two dimensions.')  
            self.PlotHandle=None
        elif DataDim<1:
            print('Cannot plot empty data.')  
            self.PlotHandle=None
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
            if z is None or r is None:
                return (None,None)
            else:
                r=self._SliceDataArray(r,self.Indexes[0:2])
                z=self._SliceDataArray(z,self.Indexes[0:2])
        return (r,z)
    
    def Plotter2D(self,**kwargs):
        
        (r,z)=self.PreparePlot2DGrid(**kwargs)
        if r is None or z is None:
            print('Problem with the grid in plotter')
        else:
            self.PlotHandle=self.PlotData2D(r,z,self.Data,**kwargs)
            self.SetPlotLabel(**kwargs)

    def SetPlotLabel(self,PlotLabel='se',ExtraLabel=None,**kwargs):
        self.BuildLabelPlot(ExtraLabel)
        if self.ax is None or PlotLabel is None:
            return
        
        if PlotLabel=='title':
                self.ax.set_title(self.LabelPlot)
        else:    
            BBox=kwargs.get('BBox')
            if BBox is None:
                BBox = dict(boxstyle='round', facecolor='blue', alpha=0.5) 
                
            PlotLabelFontSize=kwargs.get('PlotLabelFontSize')
            if PlotLabelFontSize is None:
                PlotLabelFontSize=10
                
            Pos=dict(se=(0,1),sw=(1,1),nw=(1,0),ne=(0,0))    
            
            if type(PlotLabel)==str:
                PosLabel=Pos.get(PlotLabel)
            elif type(PlotLabel)==tuple:
                PosLabel=PlotLabel
            print('PosLabel',PosLabel,'K',self.LabelPlot)
            if PosLabel is not None:
                self.HandlePlotLabel=self.ax.text(PosLabel[0], PosLabel[1], self.LabelPlot, transform=self.ax.transAxes, fontsize=PlotLabelFontSize,verticalalignment='bottom',horizontalalignment='right', bbox=BBox)
    
            
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
            