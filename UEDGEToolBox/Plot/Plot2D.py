#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 00:22:26 2020

@author: jguterl
"""
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod,SetClassArgs
from mpl_toolkits.axes_grid1 import make_axes_locatable
from UEDGEToolBox.Plot.PlotUtils import UBoxPlotUtils
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

class UBoxPlot2D(UBoxPlotUtils):
    ax=None
    def __init__(self):
        pass

    @staticmethod
    def CheckShape2DData(r,z,data):
        return not (r.shape[0]!=z.shape[0] or r.shape[1]!=z.shape[1] or data.shape[0]!=r.shape[0] or data.shape[1]!=r.shape[1])
    
    @ClassInstanceMethod     
    def PlotterSeparatrix2D(self,Grid=None,color='r',label='separatrix',linewidth=1,ax=None,**kwargs):
        Grid=self.GetGridPlot(Grid)
        
        if Grid is not None:
            r=Grid.get('rm')
            z=Grid.get('zm')
            iysptrx=Grid.get('iysptrx')-1 #shift array for python
                       
        if z is None or r is None or iysptrx is None:
            print('Something went wrong when processing the grid... Cannot plot separatrix')
            return
        
        self.PlotDataSeparatrix2D(r,z,iysptrx,color,label,linewidth,**kwargs)
            
    @ClassInstanceMethod         
    def PlotDataSeparatrix2D(self,rm,zm,iysptrx,color='r',label='separatrix',linewidth=1,ax=None,**kwargs):
       sepx=np.concatenate((rm[:,iysptrx,3],np.array([rm[-1,iysptrx,4]])))
       sepy=np.concatenate((zm[:,iysptrx,3],np.array([zm[-1,iysptrx,4]])))
       
       
       ax=self.GetAx(ax)
       ax.plot(sepx,sepy,color=color,linewidth=linewidth,label=label,**kwargs)
       
    @ClassInstanceMethod 
    def CreatePatchCollection(self,r,z,data,Label,DataLim,DataScale,ColorMap):
        if not self.CheckShape2DData(r,z,data):
            print('Mismatch between shapes of r,z and data:{},{} and {}'.format(r.shape,z.shape,data.shape))
            return (None,{},{},{})
        
        Nx=len(r)
        Ny=len(r[0])
        data=data.reshape(Nx*Ny)
        
        
        if DataLim is None:
            DataLim=(min(data),max(data))
        patches=[]    
        idx=[np.array([1,2,4,3,1])]
        Dic={}
        Pos={}
        Obj={}
        for i in range(Nx):
            for j in range(Ny):
                    Data=np.concatenate((r[i,j,idx],z[i,j,idx])).reshape(2,5).T
                    p=matplotlib.patches.Polygon(Data,closed=True,edgecolor=None,label='ix={},iy={}'.format(i,j),picker=5)        
                    patches.append(p)
                    
                    Obj[p]=p        
                    Dic[p]='ix={},iy={}'.format(i,j)
                    Pos[p]=(r[i,j,0],z[i,j,0])
    
        Collec=matplotlib.collections.PatchCollection(patches)
        Collec.set_picker(True)
        if DataScale=='log':
            norm=matplotlib.colors.LogNorm(vmin=DataLim[0],vmax=DataLim[1])
        elif DataScale=='symlog':
            norm=matplotlib.colors.SymLogNorm(vmin=DataLim[0],vmax=DataLim[1])
        elif DataScale=='linear':
            norm=matplotlib.colors.Normalize(vmin=DataLim[0],vmax=DataLim[1])
        else:
            print('Unknow DataScale. Must be log|symlog|linear')
            return (None,{},{},{})
        Collec.set_array(data)
        Collec.set_cmap(ColorMap)
        Collec.set_norm(norm)
        Collec.set_clim(vmin=DataLim[0],vmax=DataLim[1])
        if Label is not None:
            Collec.set_label(Label)
        return (Collec,Dic,Pos,Obj)
    
    
            
    
    @ClassInstanceMethod 
    def PlotData2D(self,r,z,data,Label=None,ColorMap='jet',DataLim=None,DataScale='linear',ScaleFactor=1.0,ColorBar=True,**kwargs):
        """Plot UEDGE grid."""
        if ColorMap not in matplotlib.pyplot.colormaps():
            print('ColorMap {} not defined in matplotlib...')
            print('ColorMap must be chosen in the following list:')
            print(matplotlib.pyplot.colormaps())
            return
        #print(kwargs.get('ax'))
        ax=self.GetAx(**kwargs)
        #cax=self.GetCAx(**kwargs)
        #print(kwargs.get('ax'))
        data=ScaleFactor*data  
        (Collec,Dic,Pos,Obj)=self.CreatePatchCollection(r,z,data,Label,DataLim,DataScale,ColorMap)
        
        if Collec is not None:
            
            def onpick(evt):
                if evt.artist==Collec:
                    print(evt.artist.get_array()[evt.ind[0]])
                if evt.artist in Pos.keys():  
                    annot.set_visible(False)
                    annot.xy = Pos[evt.artist]
                    evt.artist.set_facecolor='blue'
                    evt.artist.set_fill=True
                    annot.set_text(Dic[evt.artist])
                    annot.set_visible(True)
                if evt.mouseevent.button == 3:
                    annot.set_visible(False)    

            #print(kwargs.get('ax'))
            PlotHandle=ax.add_collection(Collec)
        
            ax.set_ylim(z.min(),z.max())
            ax.set_xlim(r.min(),r.max())
            annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)
            ax.set_aspect('equal') 
            ax.figure.canvas.mpl_connect('pick_event', onpick)
            if ColorBar:
                self.AddColorBar(Collec,ax,**kwargs)
                
            return PlotHandle 
        else:
            return None
            
    @ClassInstanceMethod     
    def AddColorBar(self,Collec,ax,LocationColorBar='right',SizeColorBar='5%',PadColorBar=0.3,**kwargs):
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(LocationColorBar, SizeColorBar, PadColorBar)
        ax.figure.colorbar(Collec,cax=cax)
        
    @ClassInstanceMethod 
    def SetAx(self):
        ax.set_aspect('equal', 'box')