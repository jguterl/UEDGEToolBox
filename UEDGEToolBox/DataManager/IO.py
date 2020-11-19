#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 10:34:18 2020

@author: jguterl
"""
from UEDGEToolBox.Utils.Misc import GetListPackage, ClassInstanceMethod,SetClassArgs   
from UEDGEToolBox.DataManager.DataSet import UBoxDataSet
from UEDGEToolBox.DataManager.IOFormat import UBoxNumpy,UBoxHdf5

import os,deepdish
import numpy as np
try:
    from uedge import *
except:
    pass
class UBoxLoader():
    """Helper for UBoxIO."""
    Verbose=False
    @SetClassArgs
    def __init__(self):
        pass
        
    @ClassInstanceMethod 
    def UEDGEArrayLoader(self,Pkg,VarName,VarValue,EnforceDim=True):
        try:
            Dic=locals()
            Dic['Value']=VarValue
            exec("D={}.{}".format(Pkg,VarName),globals(),Dic)
            if (Dic['D'].shape!=VarValue.shape):
                Str='Dimensions {} of variable {} different from dimensions {} of the variable in UEDGE package {}'.format(VarValue.shape,VarName,Dic['D'].shape,Pkg)
                if EnforceDim:
                    raise ValueError(Str)
                if self.Verbose: print(Str)
                Mismatch=True
            else:
                if self.Verbose: print('Variable {} match dimensions in UEDGE package {}'.format(VarName,Pkg))
                Mismatch=False
                
            if Mismatch:
                Str='['+",".join(['0:{}'.format(VarValue.shape[i]) for i in range(len(VarValue.shape))])+"]"
                #if Verbose: print('exec to fix mismatch:','{}.{}{}=v'.format(Pkg,k,Str))
                exec('{}.{}{}=Value'.format(Pkg,VarName,Str),globals(),Dic)    
            else:
                exec('{}.{}=Value'.format(Pkg,VarName),globals(),Dic)
            return None
        except Exception as e:
            if self.Verbose: print('Cannot load array "{}" into UEDGE package {}: {}'.format(VarName,Pkg,repr(e)))
            return e
        
    @ClassInstanceMethod     
    def UEDGELoader(self,Pkg,VarName,VarValue,EnforceDim=True,PrintStatus=True):
        Error=None
        if type(VarValue)==np.ndarray:  
            Error=self.UEDGEArrayLoader(Pkg,VarName,VarValue,EnforceDim)     
        else: 
            try: 
               Dic=locals()
               Dic['Value']=VarValue
               exec('{}.{}=Value'.format(Pkg,VarName),globals(),Dic)
            except Exception as e:
                Error=e
                Str='Cannot load scalar "{}" into UEDGE package {}: {}'.format(VarName,Pkg,repr(Error))
                if self.Verbose:print(Str)
        if type(VarValue)==np.ndarray:
            Type='scalar'
        else:
            Type='array'
        if PrintStatus:
            if Error is None:
                print("Loading {} '{}' into '{}' : {}".format(Type,VarName,Pkg,'Success'))
            else:
                print("Loading {} '{}' into '{}' : {} ({})".format(Type,VarName,Pkg,'Failure',Error))
        if Error is None:
            return '{}.{}'.format(Pkg,VarName)
        else:
            return ''
    @ClassInstanceMethod     
    def DicLoader(self,DicName,VarName,VarValue,CreateDic=True,PrintStatus=True):
        Error=None
        if not hasattr(self,DicName):
            if CreateDic:
                setattr(self,DicName,{})
            else:
                Error='Cannot find dictionary {} in current object.'.format(DicName)
        
        if hasattr(self,DicName):
            if type(getattr(self,DicName))==dict:
                getattr(self,DicName).update({VarName:VarValue})
            else:
                Error='Attribute {} is not a dictionary in current object.'.format(DicName)
        
        if PrintStatus:
            if Error is None:
                print("Loading '{}' into '{}' : {}".format(VarName,DicName,'Success'))
            else:
                print("Loading '{}' into '{}' : {} ({})".format(VarName,DicName,'Failure',Error))
        
        if Error is None:
            return '{}.{}'.format(DicName,VarName)
        else:
            return ''
  

        

                    
class UBoxIO(UBoxDataSet,UBoxLoader):
    """Class to save and load UEDGE data."""
    Verbose=False
    _DefaultFormat='numpy'
    _AvailableFormat={'numpy':UBoxNumpy,'hdf5':UBoxHdf5}
    VarList=[];
    ListPkg=GetListPackage()
    InputLines=[]
    @SetClassArgs
    def __init__(self):
        pass
          
            
    @ClassInstanceMethod 
    def ShowFormat(self):
        """Display available format to save and load UEDGE data."""
        print('Available format to save and load data are:')
        for k,v in self._AvailableFormat.items():
            print(" >>>> {:<10} (*{:<4})".format(k,v.Ext))
            
    @ClassInstanceMethod  
    def GetFormat(self,FileName:str or None,RaiseError=True):
        """Return format for loading/saving data based on a file Name. If no filename given, return default format."""
        if self.Verbose: print('Getting format from {}'.format(FileName))
        if FileName is not None:
            Extension=os.path.splitext(FileName)[1]
            Ext=dict((v.Ext,k) for (k,v) in self._AvailableFormat.items())
            if Ext.get(Extension) is None:
                if RaiseError:
                    raise ValueError('The extension for the fileName "{}" must be in the following list:" {}'.format(FileName,list(Ext.keys())))
                else:
                    return self._DefaultFormat 
            else:
                return Ext.get(Extension)
        else:
            return self._DefaultFormat

    
    @ClassInstanceMethod 
    def SetFormat(self,FileName:str):
        """Return format and filename for loading/saving data. Add extension to filename if no extension present."""
        if FileName is None:
            raise ValueError('FileName cannot be None')
                             
        FN, FileExtension = os.path.splitext(FileName)
        if FileExtension =='':
                FileName=FileName+self._AvailableFormat[self._DefaultFormat].Ext
                return (self._DefaultFormat,FileName)
        else:
            return (self.GetFormat(FileName),FileName)
        

           
    @ClassInstanceMethod                   
    def GetIOWorker(self,Format='numpy'):
        """Return a class with ReadData/WriteData methods for a given type of file (e.g. numpy)."""
        if self._AvailableFormat.get(Format) is not None:
            return self._AvailableFormat[Format] 
        else:
            raise KeyError('Unknown format. Format must be: {}'.format(list(self._AvailableFormat.keys())))
       
         
    @ClassInstanceMethod        
    def ImportData(self,Data:dict,DataSet=['all'],DataType='UEDGE',EnforceDim:bool=True,PrintStatus=True,ReturnList=False,ExtData=False)->list:
        """Import data from a dictionary into either UEDGE package or into a dictionary as attribute of an object."""
        if type(Data)!=dict:
            raise ValueError('Data must be a dictionary'
                             )
        if type(DataSet)==str or tuple:
            DataSet=[DataSet]
        if type(DataType)==str:
            DataType=[DataType for D in DataSet]
        if self.Verbose:
            print('Data available for import:',list(Data.keys()))   
        
        if len(DataSet)!=len(DataType):
            raise ValueError('DataSet and DataType must be lists of identical length.\n DataSet={}\nDataType={}'.format(DataSet,DataType))
        # Filter data to be loaded into UEDGE packages.DataPkg is empty is Loader is None
        DataPkg={}
        for Set,Type in zip(DataSet,DataType):
            if self.Verbose: print('Filtering dataSet:{} for DataType:{}'.format(Set,Type))
            DataOut=self.SelectData(Data,Set,Type)
            if self.Verbose: print('List of variables to be imported:',list(DataOut.keys()))
            DataPkg.update(DataOut)
        
        ListVarLoaded=self.LoadDataToPackage(DataPkg,EnforceDim,PrintStatus,ExtData)
        ListVarLoaded=[k for k in ListVarLoaded if k!='']
        if ReturnList:
            return ListVarLoaded
    
    @ClassInstanceMethod                 
    def LoadDataToPackage(self,Data:dict,EnforceDim=True,PrintStatus=True,ExtData=False):
        ListUEDGEPkg=GetListPackage()
        ListVarLoaded=[]
        CreateDic=True
        for VarName,VarValue in Data.items():    
            (Pkg,VarName)=self.SplitVarName(VarName)
            if Pkg is None:
                if self.Verbose:
                    print('No package given for variable "{}".Cannot load it...'.format(VarName))
            elif Pkg in ListUEDGEPkg and not ExtData:
                ListVarLoaded.append(self.UEDGELoader(Pkg,VarName,VarValue,EnforceDim,PrintStatus))
            elif Pkg in ListUEDGEPkg and ExtData:
                ListVarLoaded.append(self.DicLoader('DataUEDGE',VarName,VarValue,CreateDic,PrintStatus))
            else:
                ListVarLoaded.append(self.DicLoader(Pkg,VarName,VarValue,CreateDic,PrintStatus))
        ListVarLoaded=[L for L in ListVarLoaded if L!='']
        
        return ListVarLoaded

    @ClassInstanceMethod
    def SaveData(self,FileName,DataSet='regular',DataType='UEDGE',Tag={}):
        """Save a dataset from a datatype in a file."""     
        if type(DataType)==str:
            DataType=[DataType]
            DataSet=[DataSet]
            
        if len(DataSet)<1 or len(DataType)<1:
            raise ValueError('DataSet and DataType attributes cannot be empty.')
        if len(DataSet)!=len(DataType):
            raise ValueError('DataSet and DataType must be lists of identical length.')
        
        Data={}
        for Set,Type in zip(DataSet,DataType):   
            if type(Set)==dict:
                Data.update(Set)
            else:
                if Type!='UEDGE':
                    if not hasattr(self,Type) or type(getattr(self,Type))!=dict :
                        continue
                    if Set=='all':
                        Set=tuple(getattr(self,Type).keys())
                    
                        
                if self.Verbose: print('Set:',Set,Type)        
                Data.update(self.CollectDataSet(Set,DataType=Type))  
            
        (Format,FileName)=self.SetFormat(FileName)
        self.GetIOWorker(Format).WriteData(FileName,Data,Tag)
    
    @ClassInstanceMethod   
    def LoadData(self,FileName):
        """Return a dictionary of data read from a file."""
        
        if FileName is not None and os.path.exists(FileName):
            Format=self.GetFormat(FileName)
            (Data,Tag)=self.GetIOWorker(Format).ReadData(FileName)
            return (Data,Tag)
        else:
            print("Cannot open the file {}...".format(FileName))
            return ({},{})
        
    @ClassInstanceMethod   
    def LookUpData(self,FileName):
        """Plot variable names and pkg from a file."""
        if FileName is not None and os.path.exists(FileName):
            Format=self.GetFormat(FileName)
            (Data,Tag)=self.GetIOWorker(Format).ReadData(FileName)
            return (Data,Tag)
        else:
            print("Cannot open the file {}...".format(FileName))
            return ({},{})
        
    @ClassInstanceMethod   
    def ExtractData(self,FileName,DataType='UEDGE'):
        """Plot variable names and pkg from a file."""
        (Data,Tag)=self.LoadData(FileName)
        if DataType is None:
            return Data
        else:
            return Data.get(DataType)
        
    @ClassInstanceMethod
    def ExtractTag(self,FileName):
        """Plot variable names and pkg from a file."""
        (Data,Tag)=self.LoadData(FileName)
        return Tag
    
    
    @ClassInstanceMethod    
    def DisplayTag(self,FileName):
        (Data,Tag)=self.LoadData(FileName)
        print(' ****** Tag: {} *******'.format(FileName))
        for k,v in Tag.items():
            print('{} : {}'.format(k,v))
        


