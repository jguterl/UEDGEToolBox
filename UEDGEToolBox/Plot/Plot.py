"""
Created on Thu Feb 20 16:29:38 2020

@author: jguterl
"""

from UEDGEToolBox.Grid import UBoxGrid
from UEDGEToolBox.DataProcess import UBoxDataProcess
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
import numpy as np
from mpldatacursor import datacursor

#

    
    
    
    
    
        

        
        
        
    def RadialPlot(self,DataField,XType='R',idx='omp',Color=None,LineStyle='-',Marker=None,ax=None):
        if not isinstance(DataField,list):
            DataField=list(DataField)
        if not isinstance(CompareTo,list):
            CompareTo=list(CompareTo)   
        
            
            
            
        if XType.lower()=='r': #plot against R center cell [m]
        
        elif XType.lower()=='psi' :
            self.Grid['rm'][idx]
        elif XType.lower()=='psi'  :
        
        elif XType is None or XType.lower()=='idx':
            
    
        else:
            print('Error: XType must be = "R" or "Psi" or "idx" or None')
            return
        
        
        # selif XType.lower()=='psi' or :elf.Grid['rm']
        
        for DF in DataField:
            (FieldName,ExtraIndex)=ParseDataField(DF)
            DataArray=self.GetData(FieldName)
    # if no x data specified, plot again indices
    if x is None:
        x=np.linspace(0,len(data)-1,len(data),dtype=int)
        
    if ax is None:
        ax=plt.gca()  
    if LineStyle is None:
        p=ax.scatter(x,data,color=Color,marker=Marker)
    else:    
        p=ax.plot(x,data,color=Color,linestyle=LineStyle,marker=Marker)
    return p
    
    
    
    
    


        
    
            

def GetAxesAttr():
    Attributes=[]
    for m in dir(matplotlib.axes.Axes):
        if m.startswith('set_'):
            Attributes.append(m.split('set_')[1])    
class UBoxPlotSettings():
    DataFields=[]
    IdxSlice=None
    DimSlice=None
    DimSplit=None
    EnforceDataExist=False
    Data=None
    
    
        def __init__(self,Verbose=False):
            self.Verbose=Verbose
class UBoxDataPlot(UBoxDataProcess):
    def __init__(self,Object=None,Verbose=False):
        self.Verbose=False
        self.Object=Object
        self.DataFields=[]
        self.DataFieldNames=[]
        self.Data={}
        self.Indexes={}
        self.OriginalShape={}
        
    def PrepareData(self,DataFields=[],Idx=[[]],Dim=2):
                self.DataFields=DataFields
                self.Idx=Idx
                self.Dim=Dim
                self.ProcessData(Data,self.DataFields,self.Idx,self.Dim,self.Verbose)
                if self.Object is not None:
                    self.DataFieldNames=self.GetDataFieldNames(DataFields)
                    Data=self.Object.GetDataFields(self.DataFieldNames)
                    ProcessedData=self.ProcessData(Data,self.DataFields,self.Idx,self.Dim,self.Verbose)       
                    self.Data=ProcessedData[0]
                    self.Indexes=ProcessedData[1]
                    self.OriginalShape=ProcessedData[2]
                    self.Tag=self.Object.GetTag()
                    self.Grid=self.Object.GetGrid()
                    
                    
    def PlotData(self,*args,**kwargs):
        if len(Data.shape)==1:
            self.Plot1D(Data,*args,**kwargs)
        elif len(self.Data.shape)==2:
            self.Plot2D(Data,*args,**kwargs)
        elif len(self.Data.shape)>2:
            print('Cannot plot data in more than two dimensions')
        elif len(self.Data.shape)<1:
            print('Cannot plot empty data...')
                
    
            
class UBoxPlot(UBoxPlot2DBase,UBoxGrid):
    def __init__(self,Verbose=False):
        super().__init__()
        self.Ncol=2
        self.Verbose=Verbose
        self.Grid=None
        self.ColorMap='jet'
        self.DataLim=None
        self.DataScale='linear'
        self.Fig=None
        self._DataPlot={}
      
    def Plot(self,DataFields=[],Objects=[],**kwargs):
        
        self.SetDataPlot(DataFields,Objects,Idx,Dim)
        self.PlotData()
        
    
        
    def SetDataPlot(self):
        if not hasattr(self,'DataPlot'):
            self.DataPlot={}
        self.DataPlot.update(self.ParseData(DataFields,IdxSlice,DimSlice,DimSplit,EnforceDataExist,Data))
        
        
    def SetObjectPlot(self,Objects=[]):
        # Make list objects to be explore
        if type(Object)!=list:
            Objects=[Objects]
        else:
            if self not in Objects:
            Objects.append(self) # OBject=UEDGE simulation (in memeory) or UBoxData
        self.ObjectPlot=Objects.copy()
        
    def ResetDataPlot(self):
            self.DataPlot={}
    
    def PreparePlot(self,DataFields,Objects=[],IdxSlice=None,DimSlice=None,DimSplit=None,EnforceDataExist=False,DataType=None):
        
        self.SetObjectPlot(Objects)
        self.ResetDataPlot()
        
        for o in self.ObjectPlot:
            o.SetDataPlot(DataFields,IdxSlice,DimSlice,DimSplit,EnforceDataExist,DataType)
            
    def Plotter(self):
        if hasattr(self,'DataPlot'):
            for D in self.DataPlot():
                
        
    def PlotData(self,*args,**kwargs):
        if len(Data.shape)==1:
            self.Plot1D(Data,*args,**kwargs)
        elif len(self.Data.shape)==2:
            self.Plot2D(Data,*args,**kwargs)
        elif len(self.Data.shape)>2:
            print('Cannot plot data in more than two dimensions')
        elif len(self.Data.shape)<1:
            print('Cannot plot empty data...')        
        
        
    def Plot(self,DataFields,IdxSlice=None,DimSlice=None,DimSplit=None,EnforceDataExist=False,DataType=None,Replot=True):
        if not Replot:
            if DataFields is not None and Datafields!=[]:
                self.ResetDataPlot()
            else:
                raise IOError('Cannot reset DataPlot when no data fields are given')
        
        if DataFields is not None and Datafields!=[]: 
            self.AddDataPlot(DataFields,IdxSlice,DimSlice,DimSplit,EnforceDataExist,Data)
        
        self.Plotter()
        
    def Plot(self,DataFields,**kwargs)
        PlotSettings
        
            
    def SetPlotSettings(self,**kwargs):
        if not hasattr(self,'Plotsettings'):
            self.PlotSettings=UBoxPlotSettings()
        for (k,v) in kwargs.items():
             if hasattr(self.PlotSettings,k):
                 set(self.PlotSettings,k,v)
    
    def Plot(self,DataFields,IdxSlice=None,DimSlice=None,DimSplit=None,EnforceDataExist=False,DataType=None,Replot=True):
        if not Replot:
            if DataFields is not None and Datafields!=[]:
                self.ResetDataPlot()
            else:
                raise IOError('Cannot reset DataPlot when no data fields are given')
        
        if DataFields is not None and Datafields!=[]: 
            self.AddDataPlot(DataFields,IdxSlice,DimSlice,DimSplit,EnforceDataExist,Data)
        
        
class UBoxPlotTest():
    def __init__(self,Verbose=False):
        self.DataPlot={}
    #Plot('Te')
    
    def Plot(self,DataFields=None,Replot=True,**kwargs):
        
        if DataFields is not None and Datafields!=[]: 
            self.AddDataPlot(DataFields,**kwargs)
            
        self.ShowPlot()
            
        if not Replot:
            if DataFields is not None and Datafields!=[]:
                self.ResetDataPlot()
            else:
                raise IOError('Cannot reset DataPlot when no data fields are given')
        
               
    def AddDataPlot(self,DataFields=[],**kwargs):
        if not hasattr(self,'DataPlot'):
            self.DataPlot={}
        Data=self.ParseData(DataFields,**kwargs)
        for (Name,Dic) in Data.Items():
            self.DataPlot[Name]=UBoxPlotter(Dic=D,self.GetGrid(),**kwargs)
            
    def ShowPlot(self,**kwargs):
        Nplot=len((list(self.DataPlot.keys()))
        fig, ax =self.FigLayout(Nplot)
         plt.subplots()
        for (Name,Plotter) in self.DataPlot.items():
            print('Plotting "{}" ...')
            Plotter.Plot()
    @staticmethod       
    def SetNxNy(Nplot)
        Np=[1,2,3,4,5,6,7,8,9]
        Nx   =[1,1,1,2,2,2,3,3,3]
        Ny   =[1,2,3,2,2,2,3,3,3]
        return (Nx[Np.index(Nplot)],Ny[Np.index(Nplot)])
    
    def FigLayout(self,Nplot):
        
        (Nx,Ny)=self.GetNxNy(Nplot)
        # fig, axs = plt.subplots(Nx, Ny, sharex='col', sharey='row',
        #                 gridspec_kw={'hspace': 0, 'wspace': 0})
        fig, axs = plt.subplots(Nx, Ny)
        return fig,ax
    
            
    
        
   
        
        
     
                
#%%

    #plt.show(block=True)
        
    
def PlotMesh2(ax=None,iso=False,Cell=None):
    plt.ion()         
    if ax is None:
        fig,ax = plt.subplots()

    if (iso):
        ax.set_aspect('equal', 'datalim')
    else:
        ax.set_aspect('auto', 'datalim')

    
    for iy in np.arange(0,com.ny+2):
        for ix in np.arange(0,com.nx+2):
            ax.plot(com.rm[ix,iy,[1,2,4,3,1]],
                     com.zm[ix,iy,[1,2,4,3,1]], 
                     color="b")
    

    
    #ax.figure.show()     
    ax.xaxis.label('R [m]')
    ax.yaxis.ylabel('Z [m]')
    ax.figure.suptitle('UEDGE mesh')
    ax.grid(True)
    plt.show()
    
    return