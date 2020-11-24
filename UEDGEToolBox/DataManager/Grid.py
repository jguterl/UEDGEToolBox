#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: Grid
   :platform: Unix, MacOS
   :synopsis: Read and plot UEDGE grid.

.. moduleauthor:: Jerome Guterl <guterlj@fusion.gat.com>


"""
from matplotlib.collections import LineCollection
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod
import numpy as np
from matplotlib import pyplot as plt
import matplotlib 
import os
import itertools

class UBoxGrid():
    Grid={}
    def __init__(self,FileName=None,Verbose=False):
        self.Grid=None
        if FileName is not None:
            self.ImportGrid(FileName)
        self.Verbose=Verbose
        self.ax=None
        
    def GetGrid(self):
        return self.Grid
    
    @ClassInstanceMethod
    def SetGrid(self,Grid=None):
        print('Setting grid:',Grid)
        if type(Grid)==dict:
            self.Grid=Grid
        elif type(Grid)==str:
            self.ImportGrid(Grid)
        
    
    def ShowCell(self,ixiy,ax=None,Annotate=True):
        if Grid is not None:
            self.PlotCell(ixiy,rm=self.Grid['rm'],zm=self.Grid['zm'],ax=ax,Verbose=self.Verbose,Annotate=Annotate)

    
    @staticmethod        
    def PlotCell(ixiy,rm=None,zm=None,ax=None,Verbose=False,color='r',Annotate=True):
        """
        
        >>> 

        Args:
            ixiy (TYPE): DESCRIPTION.
            rm (TYPE, optional): DESCRIPTION. Defaults to None.
            zm (TYPE, optional): DESCRIPTION. Defaults to None.
            ax (TYPE, optional): DESCRIPTION. Defaults to None.
            Verbose (TYPE, optional): DESCRIPTION. Defaults to False.
            color (TYPE, optional): DESCRIPTION. Defaults to 'r'.
            Annotate (TYPE, optional): DESCRIPTION. Defaults to True.

        Returns:
            None.

        """
        
        from uedge import com
        if ax is not None:
            self.ax=ax
        if not hasattr(self,'ax') or self.ax is None:
            self.ax=plt.gca()
        if type(ixiy)!=list:
            ixiy=[ixiy]
         
        if rm is None:
            rm=com.rm
        if zm is None:
            zm=com.zm
        if Verbose: print(rm.shape)       
        for (ix,iy) in ixiy:
            r=rm[ix,iy,0]
            z=zm[ix,iy,0]
            r0 = [rm[ix, iy, 1], rm[ix, iy, 2],rm[ix, iy, 4], rm[ix, iy, 3], rm[ix, iy, 1]]
            z0 = [zm[ix, iy, 1], zm[ix, iy, 2], zm[ix, iy, 4], zm[ix, iy, 3], zm[ix, iy, 1]]
            self.ax.plot(r0, z0, '-',color=color, label='Grid', linewidth=2)
            if Annotate:
                 annot=self.ax.annotate("ix={},iy={}".format(ix,iy), xy=(r,z), xytext=(-20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
    @ClassInstanceMethod
    def PlotCentroid(self):
        if self.Grid is not None:
            if self.Grid.get('cm') is None:
                self.ComputeCentroid()
            Cm=self.Grid['cm']
        else:
            print("No grid loaded ... Use GetGrid() or SetGrid() to load a grid.")
            return
        if self.ax is None:
            self.PlotGrid()
        self.ax.scatter(Cm[:,:,0].flatten(),Cm[:,:,1].flatten(),marker='+',color='r')            
            
    @ClassInstanceMethod                 
    def ComputeCentroid(self):
        if self.Grid is not None:
            r=self.Grid['rm']
            z=self.Grid['zm']
        else:
            print("No grid loaded ... Use GetGrid() or SetGrid() to load a grid.")
            return
        
        idx=[np.array([1,2,4,3,1])]
        Nx=len(r)
        Ny=len(r[0])
        Cm=np.zeros((Nx,Ny,2))
        for i in range(Nx):
            for j in range(Ny):
                    Poly=np.concatenate((r[i,j,idx],z[i,j,idx])).reshape(2,5).T
                 
                    x=Poly[:,0]
                    y=Poly[:,1]
                    a = x[:-1] * y[1:]
                    b = y[:-1] * x[1:]
                
                    cx = x[:-1] + x[1:]
                    cy = y[:-1] + y[1:]
                    
                    A = np.sum(a - b) / 2.
                    Cx = np.sum(cx * (a - b)) / (6. * A)
                    Cy = np.sum(cy * (a - b)) / (6. * A)
                    Cm[i,j,0]=Cx
                    Cm[i,j,1]=Cy
                    
        self.Grid['cm']=Cm
        
    @ClassInstanceMethod 
    def PlotCenter(self):
        if self.Grid is not None:
            r=self.Grid['rm']
            z=self.Grid['zm']
        else:
            print("No grid loaded ... Use GetGrid() or SetGrid() to load a grid.")
            return

        self.ax.scatter(r[:,:,0].flatten(),z[:,:,0].flatten(),'pb')
    @ClassInstanceMethod 
    def PlotCenterFace(self):
        if self.Grid is not None:
            r=self.Grid['rm']
            z=self.Grid['zm']
            if self.Grid.get('cm') is None:
                self.ComputeCentroid()
            Cm=self.Grid['cm']
        else:
            print("No grid loaded ... Use GetGrid() or SetGrid() to load a grid.")
            return
        idx=np.array([1,2,4,3,1])
        Nx=len(r)
        Ny=len(r[0])
        x=list()
        y=list()
        def line(p1, p2):
            A = (p1[1] - p2[1])
            B = (p2[0] - p1[0])
            C = (p1[0]*p2[1] - p2[0]*p1[1])
            return A, B, -C

        def intersection(L1, L2):
            D  = L1[0] * L2[1] - L1[1] * L2[0]
            Dx = L1[2] * L2[1] - L1[1] * L2[2]
            Dy = L1[0] * L2[2] - L1[2] * L2[0]
            if D != 0:
                x = Dx / D
                y = Dy / D
                return x,y
            else:
                return 0,0
        IntsecN=np.zeros((Nx,Ny,2))
        IntsecE=np.zeros((Nx,Ny,2))
        for i in range(1,Nx-1):
            for j in range(1,Ny-1):
                for k,l in zip(idx[0:-1],idx[1:]):
                    L1=line(Cm[i,j,:],Cm[i,j+1,:])
                    p1=[r[i,j,4],z[i,j,4]]
                    p2=[r[i,j,3],z[i,j,3]]
                    L2=line(p1,p2) 
                    I=intersection(L1,L2)
                    
                    IntsecN[i,j,0]=I[0]
                    IntsecN[i,j,1]=I[1]
                    L1=line(Cm[i,j,:],Cm[i+1,j,:])
                    p1=[r[i,j,4],z[i,j,4]]
                    p2=[r[i,j,2],z[i,j,2]]
                    L2=line(p1,p2) 
                    I=intersection(L1,L2)
                    
                    IntsecE[i,j,0]=I[0]
                    IntsecE[i,j,1]=I[1]
                    
        if self.ax is None:
            self.PlotGrid()            
        self.ax.scatter(IntsecN[:,:,0].flatten(),IntsecN[:,:,1].flatten(),color='b',marker='o')
        self.ax.scatter(IntsecE[:,:,0].flatten(),IntsecE[:,:,1].flatten(),color='b',marker='o')
                
    @ClassInstanceMethod 
    def PlotCentroidFace(self):
        if self.Grid is not None:
            r=self.Grid['rm']
            z=self.Grid['zm']
        else:
            print("No grid loaded ... Use GetGrid() or SetGrid() to load a grid.")
            return
        idx=np.array([1,2,4,3,1])
        Nx=len(r)
        Ny=len(r[0])
        x=list()
        y=list()
        for i in range(Nx):
            for j in range(Ny):
                for k,l in zip(idx[0:-1],idx[1:]):   
                    x.append((r[i,j,k]+r[i,j,l])/2)
                    y.append((z[i,j,k]+z[i,j,l])/2)
        
        if self.ax is None:
            self.PlotGrid()
        self.ax.scatter(x,y,marker='x',color='r')
    @ClassInstanceMethod 
    def PlotGrid(self,Grid=None,edgecolor='black',zshift=[0],**kwargs):
        if type(Grid)!=list:
            Grid=[Grid]
        if type(edgecolor)!=list:
            edgecolor=[edgecolor]
        if type(zshift)!=list:
            zshift=[zshift]
        for G,ec,zs in  itertools.zip_longest(Grid,edgecolor,zshift,fillvalue=None):
            self.PlotterGrid(Grid=G,edgecolor=ec,zshift=zs,**kwargs)
    @ClassInstanceMethod     
    def PlotterGrid(self,r:np.array or None=None,z:np.array or None =None,ax:plt.Axes or None=None,zshift=0,Grid=None,edgecolor:str=None,Title:str='',NewFig=True)->None:
        """Get the foobar.

        This really should have a full function definition, but I am too lazy.

        >>> print get_foobar(10, 20)
        30
        >>> print get_foobar('a', 'b')
        ab

        Isn't that what you want?

        """
    
        self.SetGrid(Grid)
        
        if r is None or z is None:
            if self.Grid is not None:
                r=self.Grid['rm']
                z=self.Grid['zm']
            else:
                print("No grid loaded ... Use GetGrid() or SetGrid() to load a grid.")
                return
                
        z=z+zshift
        
        if ax is not None:
            self.ax=ax
        
        if not hasattr(self,'ax') or self.ax is None:
            if NewFig:
                fig,ax=plt.subplots()
                self.ax=ax
            else:
                self.ax=plt.gca()
                
        axx=self.ax
        def onpick(evt):
            if evt.artist in Pos.keys():
                if old_artist.get('current') is not None:
                    old_artist['current'].set_fill(False)
                    old_artist['current'].set_edgecolor(edgecolor)
                   
                annot.set_visible(False)
                annot.xy = Pos[evt.artist]
                evt.artist.set_facecolor('blue')
                evt.artist.set_edgecolor('red')
                evt.artist.set_fill(True)
                annot.set_text(Dic[evt.artist])
                annot.set_visible(True)
                old_artist['current']=evt.artist
                
            if evt.mouseevent.button == 3:
                annot.set_visible(False)
                
            axx.figure.canvas.draw_idle()
        old_artist={}
        Nx=len(r)
        Ny=len(r[0])
        self.ax.figure.suptitle("{}\n nx={} ny={}".format(Title,Nx,Ny))
        
        idx=[np.array([1,2,4,3,1])]
        Dic={}
        Pos={}
        Obj={}
        for i in range(Nx):
            for j in range(Ny):
                    Data=np.concatenate((r[i,j,idx],z[i,j,idx])).reshape(2,5).T
                    p=matplotlib.patches.Polygon(Data,closed=True,fill=False,edgecolor=edgecolor,label='ix={},iy={}'.format(i,j),picker=2)
                    c=self.ax.add_patch(p) #draw the contours
                    Obj[p]=c
                    Dic[p]='ix={},iy={}'.format(i,j)
                    Pos[p]=(r[i,j,0],z[i,j,0])
                    
        #print('xmin:',[np.where(z>0,z,1e10).min(),z.max()])
        #self.ax.set_ylim([z.min(),z.max()])
        #self.ax.set_xlim([np.where(r>0,r,1e10).min(),r.max()])
        self.ax.set_aspect('equal','datalim')
        annot = self.ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
        self.ax.autoscale_view()
        self.ax.figure.canvas.mpl_connect('pick_event', onpick)
        plt.show()
   
        
    
    # def ShowGrid(self,ax=None,Verbose=False,edgecolor='black',Title=''):
    #     self.Grid=self.GetGrid()
    #     UboxGrid.PlotGrid(self.Grid['rm'],self.Grid['zm'],ax,Verbose,edgecolor,Title)     
         
    @ClassInstanceMethod
    def ImportGrid(self,FileName:str = 'gridue')->None:
        """
        Read UEDGE grid file and import it into the class instance.
        
        :param FileName: Grid file, defaults to 'gridue'
        :type FileName: str, optional

        """
        self.Grid=self.ReadGridFile(FileName)
        
        
    @ClassInstanceMethod
    def SetPsinc(self,psinc=None):
        if psinc is not None:
            self.Grid['psinc']=psinc
        else:
            self.Grid['psinc']=None
            if self.Grid.get('psi') is not None:
                if self.Grid.get('simagxs') is not None:
                    simagxs=self.Grid.get('simagxs')
                    if self.Grid.get('sibdrys') is not None:
                        sibdrys=self.Grid.get('sibdrys')        
                        if simagxs!=sibdrys:
                            self.Grid['psincdiv']=np.squeeze((self.Grid['psi'][0,:,0]-simagxs) / (sibdrys-simagxs))
                            nx=self.Grid['psi'].shape[0]
                            self.Grid['psinc']=np.squeeze((self.Grid['psi'][int(nx/2),:,0]-simagxs) / (sibdrys-simagxs))
        
    @ClassInstanceMethod    
    def ReadGridFile(self,FileName:str = 'gridue')->dict:
        """
        Read UEDGE grid file and return a dictionary containing the grid.
        
        :param FileName: FileName, defaults to 'gridue'
        :type FileName: str, optional
        :return: UEDGE grid stored in dictionary format 
        :rtype: dict

        """
            
            
        try:
            f= open(FileName, mode = 'r')
            
            Values = [x for x in next(f).split()]
            HeaderItems = {'nxm':int, 'nym':int, 'ixpt1':int, 'ixpt2':int, 'iyseptrx1':int,'simagxs':float,'sibdrys':float}
            
            Values=[v(x) for x,v in zip(Values,HeaderItems.values())]
                
            gridue_params=dict(zip(HeaderItems.keys(), Values))
            next(f)
            BodyItems = ['rm', 'zm', 'psi', 'br', 'bz', 'bpol', 'bphi', 'b']
            Str={ i : [] for i in BodyItems }
            k=iter(Str.keys())
            Key=next(k)
            for line in f:
                if 'iogridue' in line or 'ingrid' in line or 'EFIT' in line:
                    continue
                if line=='\n':
                    try:
                        Key=next(k)
                    except:
                        continue
                    #print(Key)
                else:
                    Str[Key].append(line)
            f.close()
            nx=gridue_params['nxm']+2
            ny=gridue_params['nym']+2
            for k,v in Str.items():
                L=(''.join(v).replace('\n','').replace('D','e')).split()
                l=iter(L)
                vv= next(l)
    
                data_=np.zeros((nx,ny,5))
                for n in range(5):
                        for j in range(ny):
                            for i in range(nx):
    
                                data_[i][j][n]=float(vv)
    
                                try:
                                    vv=next(l)
                                except:
                                    continue
                gridue_params[k]=data_
                gridue_params['FileName']=os.path.abspath(FileName)
            return gridue_params
        except Exception as e:
            print(repr(e))
            
    
            

#Grid=UBoxGrid()
# def PlotSeparatrix(ax=None,color='r',linewidth=1,**kwargs):
#     from uedge import com
#     M.PlotFluxSurface(com.rm,com.zm,com.iysptrx,ax,color,linewidth,**kwargs)
    
    
            