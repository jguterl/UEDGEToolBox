#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:18:16 2020

@author: guterlj
"""

from pdb2py.readpdb import ReadPDBFile
from UEDGEToolBox.DataManager.IO import UBoxIO

def PDB2npy(PDBFileName,SaveFileName=None):
    Dic=ReadPDBFile(PDBFileName)
    #assume variable  name format: XXX_bbb 
    Out=dict(('bbb.'+k.split('_')[0],v.T) for k,v in Dic.items())
    Tag={'Description':'Converted from PDB file {}'.format(PDBFileName)}
    if SaveFileName is None:
        SaveFileName=PDBFileName
    UBoxIO.SaveData(SaveFileName,DataSet=Out,Tag=Tag)
    
def BatchPDB2npy(Folder,Filter='*',Verbose=True):
     List=[L for L in glob.glob(os.path.join(Folder,Filter)) if os.path.splitext(L)[1]!='.npy']
     if Verbose:
         print('Reading and Converting PDB files into npy. List of PDB files')
         print(List)
     for L in List:
         PDB2npy(L)