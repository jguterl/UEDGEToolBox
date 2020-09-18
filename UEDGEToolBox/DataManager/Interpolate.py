#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 16:28:18 2020

@author: jguterl
"""
from scipy import interpolate
import numpy as np
class UBoxInterpolate():
    def __init__():
        self.Verbose=False
    @staticmethod
    def Interpolate2D(rold,zold,data,rnew,znew,zshift=0.0,rshift=0.0,method='linear',**kwargs):
        if rold.shape!=data.shape or zold.shape!=data.shape:
            raise ValueError('Mismatch in shape of data and grid:{}:{}/{}'.format(data.shape,rold.shape,zold.shape))
        else:
            zold=zold+zshift
            rold=rold+rshift
            oldpoints = np.array( [rold.flatten(), zold.flatten()] ).T
            newpoints = np.array( [rnew.flatten(), znew.flatten()] ).T
            
            values = data.flatten()
            return interpolate.griddata(oldpoints, values, newpoints, method='linear', rescale=False).reshape(rnew.shape)
    
    def Interpolate2DData(self,Data,OldGrid,NewGrid,VarList=[],**kwargs):
        r=OldGrid['rm'][:,:,0]
        z=OldGrid['zm'][:,:,0]
        rnew=NewGrid['rm'][:,:,0]
        znew=NewGrid['zm'][:,:,0]
        if VarList==[]:
            VarList=list(Data.keys())
            
        if self.Verbose: print('old shape:{}; new shape={}'.format(r.shape,rnew.shape))
        for (K,data) in Data.items():
            if self.Verbose: print('{}.shape={}'.format(K,data.shape))
            if K in VarList:
                if len(data.shape)>2:
                    dataout=np.zeros((rnew.shape[0],rnew.shape[1],data.shape[2]))
                    for i in range(data.shape[2]):
                        out=self.Interpolate2D(r,z,np.squeeze(data[:,:,i]),rnew,znew,**kwargs)
                        dataout[:,:,i]=out[:,:]
                    Data[K]=dataout
                else:
                    Data[K]=self.Interpolate2D(r,z,data,rnew,znew,**kwargs)
                        
        return Data
    
    def InterpolateData(self,OldData,OldGrid,NewGrid,DataType='UEDGE',**kwargs):
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
                
        return self.Interpolate2DData(OldData,OldGrid,NewGrid,**kwargs)
    
    
    
    def LoadInterpolate(self,FileName,OldGrid,NewGrid,Format='numpy',LoadList=[],ExcludeList=[],CheckDim=True,Loader='plasma',InterpolateData='plasma'):
        D=UBoxData(FileName,Format='numpy',LoadList=[],ExcludeList=[])
        VarList=self.SelectVars(Mode=InterpolateData)
        if self.Verbose:
            print('Variables to be interpolated:',VarList)
        
        if self.Verbose: 
            print('OldGrid',OldGrid)
        
        if OldGrid=='loaded':
            OldGrid=D.Grid
        elif type(OldGrid)==str:
            OldGrid=UBoxGrid().ReadGrid(OldGrid)
        
        if type(OldGrid)!=dict:
            print('OldGrid must be of type grid')
        if not OldGrid:
            print('OldGrid is empty')
            return (D.Data,D.Tag)
        D.Data=self.Interpolate2DData(D.Data,OldGrid,NewGrid,VarList)
        Enforce=True
        D.Data=self.ImportData(D.Data,LoadList,ExcludeList,CheckDim,Enforce,Loader)
        
        return (D.Data,D.Tag)     
    
    
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