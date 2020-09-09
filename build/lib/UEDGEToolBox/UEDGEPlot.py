"""
Created on Thu Feb 20 16:29:38 2020

@author: jguterl
"""


import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
import numpy as np
from uedge import *
from uedge.UEDGEMesh import UEDGEMesh
from mpldatacursor import datacursor
#decorator to set ax or new fig is request
# def AutoFig(f):
#     def wrapper_do_twice(*args, **kwargs):
#         if kwargs.get('ax') is None:
#             ax=plt.gca()
#         if kwargs.get('NewFig') is True:
#             fig,ax
#         func(*args, **kwargs)
#         return func(*args, **kwargs)
#     return wrapper_do_twice
class UEDGEData():
    
    def NIndex(DataFieldIndex):
        if DataFieldIndex=='' or DataFieldIndex is None:
            return 0
        else:
            return DataFieldIndex.count(',')+1
        
    def ParseDataField(DataField:str)->(str,list):
        '''
        Example: ParseDataField('ni[1,4:6]') returns ('ni',[1,4,5,6])

        Args:
            DataField (str): Name of the field to be retrieved (e.g. ni, te,ti) with indexes of third dimension between brackets []

        Returns:
            (DataFieldName,DataFieldIndex) (str,list(int)): Name of the field (e.g. te), indexes of third dimensions if any; otherwise None

        '''
        # Input data for 
        
        S=DataField.split('[')
        Name=S[0]
        if len(S)>1:
            S=S[1]
            if S.count(']')<1:
                print('Incorrect DataField:{}. Must be "Field" or "Field[0:3]"'.format(DataField))
                return (None,None)
            S=S.split(']')[0]
            S=S.split(',')
            Index=[]
            for s in S:
                if s.count(':')>0:
                    s1=s.split(':')[0]
                    if s1=='':
                        s1=0
                    s2=s.split(':')[1]
                    if s2=='':
                        s2='-1'
                        Index.extend([int(s1),int(s2)])
                    else:    
                        Index.extend(range(int(s1),int(s2)))
                else:
                    
                    Index.extend([int(s)])
            
        else:
            Index=''
        return (Name,Index)
    
    
    def GetLineCoordinate(Grid,Type,ix=None,iy=None,Verbose=True):
        if Type.lower()=='r':
            DataArray=Grid['rm']
            ExtraIndex=[0]
        elif Type.lower()=='z':
            DataArray=Grid['zm']
            ExtraIndex=[0]
        elif Type.lower()=='psi':
            DataArray=Grid['psi']
            ExtraIndex=[0]
        elif Type.lower()=='psin':
            if Grid.get('simagxs') is not None and Grid.get('sibdrys') is not None and abs(Grid.get('simagxs')-Grid.get('sibdrys'))>0:
                        
                DataArray=(Grid['psi']-simagxs) / (sibdrys-simagxs)
                ExtraIndex=[0]
            else:
                print('Cannot normalied values of psi with sibdrys and simagxs ... Check that values are available... Return values of psi instead of psin')
                DataArray=Grid['psi']
                ExtraIndex=[0]
                
            
        else:
            print('Unknown Type={}. Type must "r" or "z" or "psi" or "psin"'.format(Type))
            return None
        
        (SubDataArray,ExtraIdx)=ExtractDataArray(DataArray,ix,iy,ExtraIndex=[0],Verbose)
        return SubDataArray
        
    def ExtractDataArray(DataArray,ix=None,iy=None,ExtraIndex='',Verbose=True)->(list,list):
        if len(DataArray.shape)<2:
            print('Cannot extract data from array of dimension <2')
            return (None,None)
        if len(DataArray.shape)>3:
            print('Cannot extract data from array of dimension >3')
            return (None,None)
        
        SubDataArray=[]
        ExtraIdx=[]
        ExtraDim=len(DataArray.shape)-2
        
        # Setup indexes to slice along 0,1 axis
        if ix is not None:
            if type(ix)==np.ndarray:
                idx=ix
            elif type(ix)==list or type(ix)==int or type(ix)==range:
                idx=np.array(ix)
            else:
                idx=None
        else:
            idx=np.arange(0,DataArray.shape[0])
           
        if iy is not None:
            if type(iy)==np.ndarray:
                idy=iy
            elif type(iy)==list or type(iy)==int or type(iy)==range:
               idy=np.array(iy)
            else:
                idy=None
        else:
            idy=np.arange(0,DataArray.shape[1])
            
        if idx is None:
            print('Wrong input for ix')
            return (None,None)
        if idy is None:
            print('Wrong input for iy')
            return (None,None)
        
        
        if Verbose:
            print('idx:',idx)
            print('idy:',idy)
         
        if ExtraDim>0: #array have more than 2 dimensions (e.g. n[:,:,0:6])
            if ExtraIndex=='':    
                ExtraIdx=range(0,DataArray.shape[2])
            else:
                
                for i,Idx in enumerate(ExtraIndex):
                    if Idx==-1:
                        if ExtraIndex[i-1]+1<DataArray.shape[2]:
                            ExtraIdx.extend(list(range(ExtraIndex[i-1]+1,DataArray.shape[2])))
                    else:
                        ExtraIdx.extend([Idx])
                        
            if Verbose: print('ExtraIdx=',ExtraIdx)            
            
            for EIdx in ExtraIdx:
                if len(idx.shape)>0:
                    SubDataArray.append(DataArray[idx[:,None],idy,EIdx])
                else:
                    SubDataArray.append(DataArray[idx,idy,EIdx])


        else:   
            if len(idx.shape)>0:
                    SubDataArray.append(DataArray[idx[:,None],idy])
            else:
                    SubDataArray.append(DataArray[idx,idy])
                    
        
                    
        return (SubDataArray,ExtraIdx)
class UEDGEPlot1DBase():
    def __init__(self):
        self.eV=1.602176634e-19
    def PlotSeparatrix(self,rm,zm,iysptrx,ax=None,color='r',linewidth=1,**kwargs):
       sepx=np.concatenate((rm[:,iysptrx,3],np.array([rm[-1,iysptrx,4]])))
       sepy=np.concatenate((zm[:,iysptrx,3],np.array([zm[-1,iysptrx,4]])))
       
       if ax is None:
           ax=plt.gca()
       ax.plot(sepx,sepy,color=color,linewidth=linewidth,**kwargs)
       
    def PlotData1D(data,x=None,Color=None,LineStyle='-',Marker=None,ax=None):
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
    
    # high-level plotting function for UEDGE
    
    
    
    
    
        

        
        
        
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
        
        
        selif XType.lower()=='psi' or :elf.Grid['rm']
        
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
    
    
    
    
    


        
    
            
class UEDGEPlot2DBase():
    def __init__(self):
        self.eV=1.602176634e-19
        
    def PlotSeparatrix(self,rm,zm,iysptrx,ax=None,color='r',linewidth=1,**kwargs):
       sepx=np.concatenate((rm[:,iysptrx,3],np.array([rm[-1,iysptrx,4]])))
       sepy=np.concatenate((zm[:,iysptrx,3],np.array([zm[-1,iysptrx,4]])))
       
       if ax is None:
           ax=plt.gca()
       ax.plot(sepx,sepy,color=color,linewidth=linewidth,**kwargs)
       
    @staticmethod    
    def PlotData2DBase(r,z,data,ax=None,ColorMap='jet',DataLim=None,DataScale='linear',Verbose=False):
        """Plot UEDGE grid."""
        if ColorMap not in matplotlib.pyplot.colormaps():
            print('ColorMap {} not defined in matplotlib...')
            print('ColorMap must be chosen in the following list:')
            print(matplotlib.pyplot.colormaps())
            return
        
        if ax is None:
            ax=plt.gca()
        
        
        def onpick(evt):
            if isinstance(evt.artist,matplotlib.collections.PatchCollection):
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
            #ax.figure.canvas.draw_idle()
    
        Nx=len(r)
        Ny=len(r[0])
        data=data.reshape(Nx*Ny)
        if DataLim is None:
            DataLim=(min(data),max(data))
        if Verbose:
            print('DataLim:',DataLim)
            
        
        patches=[]
        if ax is None:
            ax=plt.gca()
            
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
        if Verbose:
            print('DataLim=',DataLim)
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
            return
        Collec.set_array(data)
        Collec.set_cmap(ColorMap)
        Collec.set_norm(norm)
        Collec.set_clim(vmin=DataLim[0],vmax=DataLim[1])
        #cmap = plt.get_cmap('jet')
        #colors = cmap(data)   
        
        
        ax.add_collection(Collec)
        aspect = 20
        pad_fraction = 0.5
        divider = make_axes_locatable(ax)
        width = axes_size.AxesY(ax, aspect=1./aspect)
        pad = axes_size.Fraction(pad_fraction, width)
        cax = divider.append_axes("right", size=width, pad=pad)
        plt.colorbar(Collec,ax=cax,norm=norm)  
            
        ax.set_ylim(z.min(),z.max())
        ax.set_xlim(r.min(),r.max())
        annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
         
        ax.figure.canvas.mpl_connect('pick_event', onpick)   
        ax.set_aspect('equal', 'box')
        

class UEDGEPlot(UEDGEPlot2DBase,UEDGEMesh):
    eV=1.602176634e-19
    PlasmaVars=['ni','up','te','ti','phi']
    def __init__(self,Verbose=False):
        self.Ncol=2
        self.Verbose=Verbose
        
    def Plot2D(self,DataField=[],Object=[],Grid=None,ColorMap='jet',DataLim=None,DataScale='linear',fig=None):
        Object=[self]+Object
        if DataField==[]:
            DataField=self.__class__.PlasmaVars
        self.__class__.PlotData2D(DataField,Object,Grid,ColorMap,DataLim,DataScale,fig,self.Verbose)
        
    def PlotSingle2D(self,DataField,Grid=None,ax=None,ColorMap='jet',DataLim=None,DataScale='linear',fig=None):
        Grid=self.GetGrid()
        self.__class__.PlotData2DBase(Grid['rm'],Grid['zm'],self.GetData(DataField),ax,ColorMap,DataLim,DataScale,self.Verbose)
                
    @staticmethod
    def PlotData2D(DataField=[],Object=[],Grid=None,ColorMap='jet',DataLim=None,DataScale='linear',fig=None,Verbose=False):
        if Verbose: print('Object:',Object)
        if type(Object)!=list:
            Object=list(Object)
        if len(Object)<1: 
            print('Nothing to plot...')
            return 
        if Verbose: print('Object:',Object)
        if DataField==[]: 
            print('At least one field is required for plotting....')
            return
        
        if not isinstance(DataField,list):
            DataField=list(DataField)
            
        Nrow=len(Object)
        Ncol=len(DataField)
        if Verbose: print('Ncol:',Ncol)
        if Verbose: print('Nrow:',Nrow)
        
        if len(Object)>1:
            FigTitle='Comparison '+'/'.join([o.GetCaseName() for o in Object])
        else:
            FigTitle=Object[0].GetCaseName()
            
        if fig is None:
            fig,ax=plt.subplots(Nrow,Ncol,sharex='all',sharey='all',num=FigTitle)
        else:
            ax=fig.subplots(Nrow,Ncol,sharex='all',sharey='all',num=FigTitle)
        
        if type(ax)!=np.ndarray:
            ax=[ax]
        i=0
        if Verbose: print('Object:',Object)
        for o in Object:
            CaseName=o.GetCaseName()
            if Grid is None:
                Grid=o.GetGrid()  
            for F in DataField:
                if Grid.get('rm') is None or Grid.get('zm') is None:
                    print('No grid available for {}. Skipping...'.format(CaseName))
                else:
                    Data=o.GetData(F)
                    if Verbose: print('Data.shape=',Data.shape)
                    if Verbose: print('rm.shape=',Grid['rm'].shape)
                    if Data is not None:
                        if F.lower()=='te' or F.lower()=='ti':
                            Data=Data/1.602176634e-19
                        if Verbose: print('Plotting ',F)
                        o.__class__.PlotData2DBase(Grid['rm'],Grid['zm'],Data,ax[i],ColorMap,DataLim,DataScale,Verbose)
                        ax[i].set_title('{}:{}'.format(CaseName,F))
                    else:
                        print('Cannot plot {F} for case {}'.format(F,CaseName))
                i=i+1
        plt.show()        
                
                
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