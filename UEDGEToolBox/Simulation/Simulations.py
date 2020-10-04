#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 15:52:13 2020

@author: jguterl
"""

import types,math
#import matplotlib.pyplot as plt
import numpy as np
import os, sys, string, re
from pathlib import Path
try:
    from uedge import bbb # just for compliance with python IDE rules. Do not do anything
except:
    pass
from colorama import  Back, Style
from datetime import date,datetime
from UEDGEToolBox.DataManager.Grid import UBoxGrid
from UEDGEToolBox.Utils.Misc import LsFolder,GetListPackage,GetPlatform,GetTimeStamp,ClassInstanceMethod,SetClassArgs
from UEDGEToolBox.ProjectManager.Projects import UBoxSingleProject
from UEDGEToolBox.DataManager.DataSet import UBoxDataSet,UBoxDataFilter
from UEDGEToolBox.ProjectManager.Source import UBoxSource
#from UEDGEToolBox.Plot import *
#from UEDGEToolBox.Projects import *
#from UEDGEToolBox.IO import *

        
class UBoxSimUtils(UBoxGrid,UBoxSource,UBoxDataSet):
    def __init__(self,  Verbose=False,*args, **kwargs):
        # Import Uedge packages as attribute of the class instance
        # WARNING: this is not a deep copy!!!
        super().__init__()
        self.InputLines=[]
        self.ListPkg=GetListPackage()
        self.Verbose=Verbose
        print('Loaded Packages:',self.ListPkg)
        # for pkg in self.ListPkg:
        #     exec('self.' + pkg + '=' + pkg,globals(),locals())
        #self.IO=UBoxIO(self.Verbose)
        self.ExcludeList=['ExcludeList','ListPkg','IO']+self.ListPkg
        self.CorrectTemp= 1.602176634e-19
        #self.SetVersion()
    @staticmethod
    def InitPlasma():
        bbb.ngs=1e14; bbb.ng=1e14
        bbb.nis=1e20; bbb.ni=1e20 
        bbb.ups=0.0;  bbb.up=0.0
        bbb.tes=bbb.ev;   bbb.te=bbb.ev
        bbb.tis=bbb.ev;   bbb.ti=bbb.ev
        bbb.phis=0;bbb.phi=0
    def PrintTimeStepModif(self,i):
        self.PrintInfo('New time-step = {:.4E}'.format(bbb.dtreal),color=Back.MAGENTA)
    
    def PrintError(self,E,i,j=None):
        if j is None:
            self.PrintInfo('{cn}: Exmain failure i={i}/{imax}              dtreal={dt:.4E}'.format(cn=self.CaseName,i=i,imax=self.Imax, dt=bbb.dtreal),color=Back.RED)       
        else:
            self.PrintInfo('{cn}: Exmain failure i={i}/{imax} j={j}/{jmax} dtreal={dt:.4E}'.format(cn=self.CaseName,i=i,imax=self.Imax,j=j,jmax=self.Jmax,dt=bbb.dtreal),color=Back.RED)
        print("Exception: {}".format(E))
    
    def PrintCurrentIteration(self,i,j=None):
        if j is None:
            self.PrintInfo('{cn}: Main loop i={i}/{imax}       dtreal={dt:.4E}'.format(cn=self.CaseName,i=i,imax=self.Imax, dt=bbb.dtreal),color=Back.BLUE)
        else:
            self.PrintInfo('{cn}: Subloop   i={i}/{imax} j={j}/{jmax} dtreal={dt:.4E}'.format(cn=self.CaseName,i=i,imax=self.Imax,j=j,jmax=self.Jmax,dt=bbb.dtreal),color=Back.YELLOW)

    def PrintInfo(self,Str,color=Back.CYAN,Extra=False):
        if Extra: print("*---------------------------------------------------------*")
        print("{color}{}{reset}".format(Str,color=color,reset=Style.RESET_ALL))
        if Extra: print("*---------------------------------------------------------*")
        
    def SaveLast(self,DataSet='regular'):
        self.Save('last.npy',DataSet=DataSet,DataType='UEDGE',OverWrite=True)
    
    def SaveFinalState(self,DataSet='regular'):
        self.Save('final_state.npy',DataSet=DataSet,DataType='UEDGE',OverWrite=True)
        
    def AutoSave(self,DataSet='regular'):
        self._iSave+=1
        if self._iSave>self.ISave:
            self._iSave=1
            self.Save('save_{}'.format(GetTimeStamp()),DataSet=DataSet,DataType='UEDGE')  
            
    def GetTag(self)->dict:
        """
        Generate a dictionary containing settings of a UBox instance.
    
        Args:
            UBoxObject (UBoxSimulation, optional): Simulation instance. Defaults to None.
    
        Return:
            Dictionary with 
    
        """
        from uedge import __version__,GitHash
        today = date.today()
        now = datetime.now()
        Tag={}
        Tag['Date'] = today.strftime("%d%b%Y")
        Tag['Time'] = now.strftime("%H-%M-%S")
        Tag['GitHash']=GitHash
        Tag['Version'] = __version__
        
        if hasattr(self,'UserName'):
            Tag['User']=self.UserName
        else:
            Tag['User']='unknown'
            
        if not hasattr(self,'PlatForm') or getattr(self,'PlatForm') is None:
            self.PlatForm=GetPlatform()
        Tag['PythonVersion']=self.PlatForm['python_version']
        Tag['Machine']=self.PlatForm['machine']
        Tag['Processor']=self.PlatForm['processor']
        Tag['PlatForm']=self.PlatForm['platform']
        
        if hasattr(self,'CurrentProject') and self.CurrentProject is not None:
            Tag['Project']=self.CurrentProject.toDict()
        else:
            Tag['Project']={}
        if hasattr(self,'Description'):    
            Tag['CaseName']=self.CaseName
        else:
            Tag['CaseName']=''
        if hasattr(self,'Description'):
            Tag['Description']=self.Description
        else:
            Tag['Description']=''
    
        return Tag
                                   
    
    @ClassInstanceMethod    
    def GetData(self,Field:str,DataType:str='UEDGE',CorrectTempUnit=True):
        """Get data values from data dictionary stored in the instance."""
        Out=self.CollectData(Field,DataType,RemovePackage=True)
        if self.Verbose:print('GetData:',Out)      
        Out=Out.get(Field)  
        if Out is not None and Out.size==1 and Out.dtype.char=='S':
            Out=Out[0].decode().strip()
            
        F=Field.lower()
        if Field.count('.')>0:
            F=F.split('.')[1]    
        if Out is not None and CorrectTempUnit and any([F==L for L in ['tes','tis','tgs','te','ti','tg']]):
            if not hasattr(self,'CorrectTemp'):
                self.CorrectTemp= 1.602176634e-19
            Out=Out/self.CorrectTemp    
    
        return Out
    
    @ClassInstanceMethod
    def GetDataField(self,Field:str or list,DataType:str='UEDGE'):
        """Get data values from data dictionary stored in the instance."""
        if DataType is None:
            DataType='UEDGE'
            
        if type(Field)==str:
            return self.GetData(Field,DataType)
        elif type(Field)==list: 
            return [self.GetData(k,DataType) for k in Field]
        else:
            raise IOError('Field must be a string or a list of strings')
    # # def GetDataField(self,Field):
    # #     if type(Field)!=str:
    # #         raise ValueError('Field must be a string')
    # #     return self.CollectUEDGEData(Field).get(Field)
    
    # # def GetData(self,Field):
    # #     if type(Field)==str:
    # #         Field=(Field,)
    # #     if type(Field)==list:
    # #         Field=tuple(Field)
            
    #     Dic=self.CollectUEDGEData(Field)
    #     return dict((self.RemovePkg(k),v) for k,v in Dic.items())
    
    
        
    # def GetData(self,Field,Package='bbb'):
    #     """

    #     Args:
    #         Field (TYPE): DESCRIPTION.
    #         Package (TYPE, optional): DESCRIPTION. Defaults to 'bbb'.

    #     Returns:
    #         TYPE: DESCRIPTION.

    #     """
    #     self.GetPackage
    #     # UEDGE packages are reloaded in the local namespace of the method.
    #     #However, no new instances of UEDGE packages are created.
    #     # Instances in the local namespace are the same instances that were previously loaded
    #     for pkg in self.ListPkg:
    #         exec('from uedge import '+pkg)

    #     Out=locals()
    #     comm='{}={}.{}'.format(Field.lower(),Package,Field.lower())
    #     if self.Verbose: print('Retrieving data:',comm)
    #     try:
    #         exec(comm,globals(),Out)
    #     except:
    #         print('Cannot set {}={}.{} '.format(Field,Package,Field))
    #     if Out.get(Field) is None:
    #         print('Cound not get data for {}'.format(Field))

    #     return Out.get(Field.lower())

    # def SetData(self):
    #     for pkg in self.ListPkg:
    #         exec('from uedge import '+pkg)
    #     Out=locals()
    #     comm='{}={}.{}'.format(Field.lower(),'bbb',Field.lower())
    #     if self.Verbose: print('Setting data:',comm)
    #     try:
    #         exec(comm,globals(),Out)
    #     except:
    #         print('Cannot set {}={}.{} '.format(Field,'bbb',Field))
    #     if Out.get(Field) is None:
    #         print('Cound not get data for {}'.format(Field))

    #     self.Data=Out

    def GetGrid(self):
        self.SetGrid()
        return self.Grid

    def SetGrid(self,Grid=None):
        if Grid is None:
            Dic=self.CollectDataSet(DataSet='grid',DataType='UEDGE')['UEDGE']
            self.Grid=dict((self.RemovePkg(k),v) for k,v in Dic.items())
        else:
            self.Grid=Grid
        if hasattr(self,'SetPsinc'):
                   self.SetPsinc()
        
        






   


    # @classmethod
    # def GetClassAttr(cls,Verbose=False):
    #     """


    #     Args:
    #         cls (TYPE): DESCRIPTION.
    #         Verbose (TYPE, optional): DESCRIPTION. Defaults to False.

    #     Returns:
    #         Attr (TYPE): DESCRIPTION.

    #     """

    #     Attr = dict((k,v) for k,v in cls.__dict__.items() if '__' not in k and not isinstance(v,types.FunctionType) and not isinstance(v,classmethod))
    #     if Verbose: print(Attr)
    #     return Attr

    # def GetInstanceAttr(self,Verbose=False):
    #     Attr = dict((k,v) for k,v in self.__dict__.items() if '__' not in k and not isinstance(v,types.FunctionType) and not isinstance(v,classmethod))
    #     if Verbose: print(Attr)
    #     return Attr

    # @classmethod
    # def ShowClass(cls,Verbose=False):
    #     Attr = dict((k,v) for k,v in cls.__dict__.items() if '__' not in k and not isinstance(v,types.FunctionType) and not isinstance(v,classmethod))
    #     if Verbose: print(Attr)
    #     for A,V in Attr.items():
    #         comm='print("{}","=",)'.format(A,V)
    #         print('{}={}'.format(A,V))

    def Show(self,Verbose=False):
        print('Internal UEDGE parameters:')
        for A,V in self.GetInstanceAttr().items():
            Result=SearchSilent(A)
            if len(Result)>0:
                Pkg=Result[0]['Package']
                print(' - {}.{}={}'.format(Pkg,A,V))
            else:
                print(' - XXX.{}={}'.format(A,V))
        print('\n Run parameters:')
        for A,V in self.__class__.GetClassAttr().items():
            print(' - {}={}'.format(A,V))

    

    

    

    # def OverrideClassParams(self,**kwargs):
    #     #Override class attribute
    #     Dic=self.__class__.GetClassAttr()
    #     for k,v in kwargs.items():
    #         if k in Dic:
    #             self.__class__.__dict__[k]=v





    def SetCaseName(self,CaseName):
        self.CaseName=CaseName
        try:
            from uedge import bbb
            bbb.CaseName=CaseName
        except:
            pass

    def GetCaseName(self):
        try:
            return bbb.CaseName[0].decode().rstrip()
        except:
            return None

    def SetDescription(self,Str):
        self.Description=Str

    def GetDescription(self):
        return self.Description

    def GetVersion(self):
        return uedge.__version__
    
    def GetGitHash(self):
        return uedge.GitHash
    
    def SetVersion(self):
        try:
            bbb.uedge_ver=uedge.__version__
        except:
            print('Cannot set Uedge version')
    @staticmethod
    def Pandf():
        bbb.pandf1 (-1, -1, 0, bbb.neq, 1., bbb.yl, bbb.yldot)
        
    def Updateftol(self):
        bbb.ylodt = bbb.yl
        bbb.pandf1 (-1, -1, 0, bbb.neq, 1., bbb.yl, bbb.yldot)
        fnrm_old=math.sqrt(sum((bbb.yldot[0:bbb.neq-1]*bbb.sfscal[0:bbb.neq-1])**2))
        return max(min(bbb.ftol_dt, 0.01*fnrm_old),bbb.ftol_min)
    
    @staticmethod
    def Resetftol():
        bbb.ftol_min=1e-10
        bbb.ftol_dt=1e-10
        print("Reset ftol: bbb.ftol_dt={};bbb.ftol_min={}".format(bbb.ftol_min,bbb.ftol_dt))
    
    @staticmethod
    def Setftol(ftol):
        bbb.ftol_min=ftol
        bbb.ftol_dt=ftol
        print("Set ftol to {}".format(ftol)) 
    
    @staticmethod
    def Changeftol(factor):
        bbb.ftol_min*=factor
        bbb.ftol_dt*=factor
        print("Change ftol by a factor {}: bbb.ftol_dt={};bbb.ftol_min={}".format(factor,bbb.ftol_min,bbb.ftol_dt)) 
    
    def Controlftol(self,dtreal_threshold=5e-10,Mult=10):
        if not hasattr(self,'CftolCount'):
            self.CftolCount=0
        if not hasattr(self,'CftolMult'):
            self.CftolMult=Mult
        if not hasattr(self,'dtreal_bkp'):
            self.dtreal_bkp=bbb.dtreal
        if not hasattr(self,'dtreal_threshold'):
            self.dtreal_threshold=dtreal_threshold    
        if bbb.dtreal<self.dtreal_threshold:
            print('CftolCount:',self.CftolCount)
            if bbb.dtreal<self.dtreal_bkp:
                self.Changeftol(self.CftolMult)
                self.CftolCount+=1
            else:
                if self.CftolCount>0:
                    self.Changeftol(1/self.CftolMult)
                    self.CftolCount-=1         
        else:
            if self.CftolCount>0:
                    self.Changeftol(1/self.CftolMult)
                    self.CftolCount-=1
        
        self.dtreal_bkp=bbb.dtreal    
    
        



    


class UBoxSimExt():
    def WideSave(self):
        self.SaveInputSomewhere()
        self.Save()
    def TimeEvolution(self):
        """
        Allow the evolution of UEDGE settings in time. Set by SetTimeEvolution(). Print a log of values associated with files

        Returns:
            None.

        """
        pass
        #for k,v in self.TimeParameters:

            #bbb.dt_tot    
    def RunRamp(self,Data:dict,Istart:int=0,dtreal_start:float=1e-8,tstop:float=10):
        """

        Args:
            Data (dict): ebbb.g. Dic={'ncore[0]':np.linspace(1e19,1e20,10),'pcoree':np.linspace(0.5e6,5e6,10)}
            Istart (int, optional): DESCRIPTION. Defaults to 0.
            dtreal_start (float, optional): DESCRIPTION. Defaults to 1e-8.
            tstop (float, optional): DESCRIPTION. Defaults to 10.

        Returns:
            None.

        """

        #Check if all data arrays have the same length
        List=[v.shape for (k,v) in Data.items()]
        if not all(L == List[0] for L in List):
            print('Arrays of different size... Cannot proceed...')
            return
        Istop=List[0][0]
        if Istart>=Istop:
            print('Istart={} >= Istop={}: cannot proceed...'.format(Istart,Istop))
        irun=Istart
        # Loop over data

        BaseCaseName=self.CaseName
        while irun <Istop:

            # 1) Set data in uedge packages
            Params=dict((k,v[irun]) for (k,v) in Data.items())
            ListParams=['{}:{}'.format(k,v) for k,v in Params.items()]
            StrParams=['{}_{:2.2e}'.format(k.split('[')[0],v) for k,v in Params.items()]

            self.CaseName=BaseCaseName+'_'.join(StrParams)
            self.SetPackageParams(Params)

            # 2) Run until completion
            self.PrintInfo('RAMP i={}/{} : '.format(irun,Istop)+','.join(ListParams),color=Back.MAGENTA)
            FileName='final_state_ramp_'+'_'.join(ListValueParams)
            FilePath=UEDGEToolBox.Source(FileName,Folder='SaveDir',Enforce=False,Verbose=Verbose,CaseName=self.CaseName,CheckExistence=False)
            if CheckFileExist(FilePath):
                print('File {} exists. Skipping this ramp step...'.format(FilePath))
                continue

            Status=self.Cont(dt_tot=0,dtreal=dtreal_start,t_stop=tstop)
            if Status=='tstop':
                ListValueParams=['{:2.2e}'.format(v) for k,v in Params.items()]
                self.Save('final_state_ramp_'+'_'.join(ListValueParams))
                self.SaveLog('logramp','{}:{}::'.format(self.Tag['Date'],self.Tag['Time'])+';'.join(ListParams))
                irun+=1
            else:
                print('Exiting ramp... Need to add a routine to restart after dtkill')
                return    
