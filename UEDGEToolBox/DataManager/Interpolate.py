#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 16:28:18 2020

@author: jguterl
"""
from scipy import interpolate
import numpy as np
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod
from UEDGEToolBox.DataManager.Grid import UBoxGrid
from UEDGEToolBox.DataManager.IO import UBoxIO

class UBoxInterpolate(UBoxGrid,UBoxIO):
    def __init__(self,Verbose=False):
        self.Verbose=Verbose
        
    @staticmethod
    def Interpolate2D(rold,zold,data,rnew,znew,zshift=0.0,rshift=0.0,method='nearest',\
                      fill_value=0,SmoothGuardCells=True,**kwargs):
        if rold.shape!=data.shape or zold.shape!=data.shape:
            raise ValueError('Mismatch in shape of data and grid:{}:{}/{}'.format(data.shape,rold.shape,zold.shape))
        else:
            print('zshift:',zshift)
            zold=zold+zshift
            rold=rold+rshift
            oldpoints = np.array( [rold.flatten(), zold.flatten()] ).T
            newpoints = np.array( [rnew.flatten(), znew.flatten()] ).T
            if SmoothGuardCells:
                data[0,:]=data[1,:]
                data[-1,:]=data[-2,:]
                data[:,0]=data[:,1]
                data[:,-1]=data[:,-2]
                
            values = data.flatten()
            
            NewData=interpolate.griddata(oldpoints, values, newpoints, method=method, fill_value=fill_value, rescale=False).reshape(rnew.shape)
            if SmoothGuardCells:
                NewData[0,:]=NewData[1,:]
                NewData[-1,:]=NewData[-2,:]
                NewData[:,0]=NewData[:,1]
                NewData[:,-1]=NewData[:,-2]
            return NewData


    @staticmethod    
    def Interpolate1D(xold,data,xnew,xshift=0.0,method='nearest',**kwargs):
        # if xold.shape!=data.shape:
        #     print(xold)
        #     print(data)
        #     raise ValueError('Mismatch in shape of x and data:{}:{}'.format(xold.shape,data.shape))
        # else:
        
            xold=xold+xshift
            return np.interp(xnew,xold,data)
        
        
    @ClassInstanceMethod
    def _Interpolate2DData(self,Data,OldGrid,NewGrid,VarList=[],**kwargs):
        r=OldGrid['rm'][:,:,0]
        z=OldGrid['zm'][:,:,0]
        rnew=NewGrid['rm'][:,:,0]
        znew=NewGrid['zm'][:,:,0]
        print('Data.keys():',Data.keys())
        if VarList==[]:
            VarList=list(Data.keys())
        
            
        if self.Verbose: print('old shape:{}; new shape={}'.format(r.shape,rnew.shape))
        for (K,data) in Data.items():
            if self.Verbose: print('{}.shape={}'.format(K,data.shape))
            if K in VarList:
                print('processing:{}'.format(K))
                if len(data.shape)>2:
                    dataout=np.zeros((rnew.shape[0],rnew.shape[1],data.shape[2]))
                    for i in range(data.shape[2]):
                        out=self.Interpolate2D(r,z,np.squeeze(data[:,:,i]),rnew,znew,**kwargs)
                        dataout[:,:,i]=out[:,:]
                    Data[K]=dataout
                else:
                    Data[K]=self.Interpolate2D(r,z,data,rnew,znew,**kwargs)
                        
        return Data
    
    @ClassInstanceMethod
    def Interpolate2DData(self,OldData,OldGrid,NewGrid,DataType='UEDGE',**kwargs):
        if type(OldGrid)==str:
            OldGrid=self.ReadGridFile(OldGrid)
        elif type(OldGrid)!=dict:
            raise IOError('OldGrid must be a filename or a grid dictionary')
            
        if type(NewGrid)==str:
            NewGrid=self.ReadGridFile(NewGrid)
        elif type(NewGrid)!=dict:
            raise IOError('NewGrid must be a filename or a grid dictionary')
        
        if type(OldData)==str:
            (Data,OldTag)=self.LoadData(OldData)
            if DataType is None:
                OldData=Data
            else:
                OldData=Data[DataType]      
        return self._Interpolate2DData(OldData,OldGrid,NewGrid,**kwargs)
    
    @ClassInstanceMethod
    def InterpolateData(self,OldData,OldGrid,NewGrid,DataType='UEDGE',ExcludeList=[],IncludeList=[],**kwargs):
        
        if type(OldGrid)==str:
            OldGrid=self.ReadGridFile(OldGrid)
        elif type(OldGrid)!=dict:
            raise IOError('OldGrid must be a filename or a grid dictionary')
            
        if type(NewGrid)==str:
            NewGrid=self.ReadGridFile(NewGrid)
        elif type(NewGrid)!=dict:
            raise IOError('NewGrid must be a filename or a grid dictionary')
        
        if type(OldData)==str:
            (Data,OldTag)=self.LoadData(OldData)
            if DataType is None:
                OldData=Data
            else:
                OldData=Data.get(DataType)
            if OldData is None:
                    raise ValueError('Unknow datatype in Data. DataType must be an entry of the dictionary Data. Data entries are read with DataType=None')
        if IncludeList==[]:
            IncludeList=list(OldData.keys())
            
        if self.Verbose:
            print('Entry Old Data:',list(OldData.keys()))
                  
        OldData=dict((k,v) for k,v in OldData.items() if k not in ExcludeList and k in IncludeList)
        
        return self.Interpolate2DData(OldData,OldGrid,NewGrid,**kwargs)
    
    @staticmethod
    def CleanUpData(Data,TeMin=0.1,DensMin=1e10):
        TeMin=TeMin*1.6e-19
        for k,v in Data.items():
            if 'te' in k or 'ti' in k:
                v[(v<=TeMin)]=TeMin
            if 'ng' in k or 'ni' in k:
                v[(v<=DensMin)]=DensMin
            
            
                
    
    
    
    # def LoadInterpolate(self,FileName,OldGrid,NewGrid,Format='numpy',LoadList=[],ExcludeList=[],CheckDim=True,Loader='plasma',InterpolateData='plasma'):
    #     D=UBoxData(FileName,Format='numpy',LoadList=[],ExcludeList=[])
    #     VarList=self.SelectVars(Mode=InterpolateData)
    #     if self.Verbose:
    #         print('Variables to be interpolated:',VarList)
        
    #     if self.Verbose: 
    #         print('OldGrid',OldGrid)
        
    #     if OldGrid=='loaded':
    #         OldGrid=D.Grid
    #     elif type(OldGrid)==str:
    #         OldGrid=UBoxGrid().ReadGrid(OldGrid)
        
    #     if type(OldGrid)!=dict:
    #         print('OldGrid must be of type grid')
    #     if not OldGrid:
    #         print('OldGrid is empty')
    #         return (D.Data,D.Tag)
    #     D.Data=self.Interpolate2DData(D.Data,OldGrid,NewGrid,VarList)
    #     Enforce=True
    #     D.Data=self.ImportData(D.Data,LoadList,ExcludeList,CheckDim,Enforce,Loader)
        
    #     return (D.Data,D.Tag)     
    
    
        # def LoadInterp(self,FileName,OldGrid='loaded',NewGrid=None,CaseName=None,Folder='SaveDir',LoadPackage='plasma',InterpolateData='plasma',LoadList=[],ExcludeList=[],Format=None,CheckDim=True,Verbose=False):

        # if Format is None:
        #     Format=self.Format
        # Verbose=Verbose or self.Verbose

        # if NewGrid is None:
        #     NewGrid=self.GetGrid()
        # elif type(NewGrid)==str:
        #         NewGrid=UEDGEMesh().ImportMesh(NewGrid)
        # elif type(NewGrid)!=dict:
        #     print("NewGrid must a Grid or a path toward a grid file")

        # FilePath=Source(FileName,Folder=Folder,Enforce=False,Verbose=Verbose,CaseName=CaseName)
        # if Verbose:
        #     print("Load data in file:{}".format(FilePath))
        # # Looking for file
        # if os.path.isfile(FilePath):
        #     self.IO.Verbose=Verbose
        #     self.IO.LoadInterpolate(FilePath,OldGrid,NewGrid,Format,LoadList,ExcludeList,CheckDim,LoadPackage,InterpolateData)
        #     bbb.restart=1
        # else:
        #     print("The file {} does not exist".format(FilePath))