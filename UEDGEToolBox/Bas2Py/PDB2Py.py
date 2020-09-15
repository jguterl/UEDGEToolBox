#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:18:16 2020

@author: guterlj
"""

from pdb2py.readpdb import ReadPDBFile
from UEDGEToolBox.DataManager.IO import UBoxIO
import numpy
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod

class UBoxPDB2Py():
    @ClassInstanceMethod
    def PDB2Py(self,PDBFileName,SaveFileName=None,ReturnData=False):
        Dic=ReadPDBFile(PDBFileName)
        #assume variable  name format: XXX_bbb 
        #Out=dict(('bbb.'+k.split('_')[0],self.SwapAxis(v)) for k,v in Dic.items())
        Out=dict(('bbb.'+k.split('_')[0],v.transpose()) for k,v in Dic.items())
        Tag={'Description':'Converted from PDB file {}'.format(PDBFileName)}
        if SaveFileName is None:
            SaveFileName=PDBFileName
        UBoxIO.SaveData(SaveFileName,DataSet=Out,Tag=Tag)
   
        if ReturnData:
            return Out
    @ClassInstanceMethod
    def BatchPDB2Py(self,Folder,Filter='*',Ext='.npy'):
         List=[L for L in glob.glob(os.path.join(Folder,Filter)) if os.path.splitext(L)[1]!=Ext]
         if self.Verbose:
             print('Reading and converting PDB files into npy. List of PDB files')
             print(List)
         for L in List:
             self.PDB2Py(L,L+Ext)
             
    @ClassInstanceMethod
    def SwapAxis(self,DataArray):
        if type(DataArray)==numpy.ndarray:
            Dim=len(DataArray.shape)
            
            if Dim==2:
                DataArray=DataArray.swapaxes(0,1)
            if Dim==3:
                DataArray=DataArray.swapaxes(0,2)
            if Dim>3:
                raise ValueError('Swapping of axis for arrays of dimension >3 not implemented')
   
        return DataArray
    
    