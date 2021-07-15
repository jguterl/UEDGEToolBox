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
from UEDGEToolBox.Utils.Doc import UBoxDoc
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
        self.ExcludeList=['ExcludeList','ListPkg','IO']+self.ListPkg
        self.SetDefault()


    def SetDefault(self):
           self.UBoxRunDefaults={'Jmax':5,'Imax':3000, 'mult_dt_fwd':3.4,'mult_dt_bwd':3,'ISave':10,'SaveSim':True}
           self.UBoxRunDefaults['dt_ftol_threshold']=5e-11
           self.UBoxRunDefaults['dt_ContCallOff_min']=5e-2
           self.UBoxRunDefaults['dt_ContCallOff_max']=5e-3
           self.UBoxRunDefaults['CorrectTemp']= 1.602176634e-19
           self.UBoxRunDefaults['Adjustftol']=False
           self.UBoxRunDefaults['ContCall']=True
           self.bbbRunDefault={}
           self.bbbRunDefault['dt_tot']=0
           self.bbbRunDefault['dtreal']=5e-8
           self.bbbRunDefault['t_stop']=10
           self.bbbRunDefault['ftol_min']=1e-10
           self.bbbRunDefault['ftol_dt']=1e-9
           self.bbbRunDefault['itermx']=25
           self.bbbRunDefault['rlx']=0.9
           self.bbbRunDefault['incpset']=10
           self.bbbRunDefault['isbcwdt']=1

           self.SetPackageParams(self.bbbRunDefault)
           self.SetPackageParams(self.UBoxRunDefaults,self,AddAttr=True)

    def SetUEDGEParams(self,Dic:dict):
        Dic=dict((k,v) for k,v in Dic.items() if k in list(self.bbbRunDefault.keys()))
        self.SetPackageParams(Dic)

    def SetPackageParams(self,Dic:dict,Pkg=None,AddAttr=False):
        """
        Args:
            Verbose (TYPE, optional): DESCRIPTION. Defaults to False.

        Returns:
            None.
        """
        if Pkg is None:
            if not hasattr(self,'Doc') or self.Doc is None:
                self.Doc = UBoxDoc()
            for A,V in Dic.items():
                if V is not None:
                    Result=self.Doc.Search(A.split('[')[0],Exact=True,Silent=True)
                    if len(Result)>0:
                        Pkg=Result[0]['Package']
                        comm='{}.{}={}'.format(Pkg,A,V)
                        if self.Verbose: print('Setting {}'.format(comm))
                        try:
                            exec(comm,globals(),globals())
                        except:
                            print('Cannot set {}.{} = {} '.format(Pkg,A,V))
                    else:
                        print('No package found for {}'.format(A))
        else:
            for A,V in Dic.items():
                    if AddAttr or hasattr(Pkg,A):
                        if self.Verbose:
                            print('Setting {}.{}={}'.format(Pkg,A,V))
                        setattr(Pkg,A,V)

    @staticmethod
    def InitPlasma():
        bbb.ngs=1e18; bbb.ng=1e18
        bbb.nis=1e18; bbb.ni=1e18
        bbb.ups=0.0;  bbb.up=0.0
        bbb.tes=1*bbb.ev;   bbb.te=1*bbb.ev
        bbb.tis=1*bbb.ev;   bbb.ti=1*bbb.ev
        bbb.tgs=1*bbb.ev;   bbb.tg=1*bbb.ev
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
        self.Save('last',DataSet=DataSet,DataType='UEDGE',OverWrite=True)

    def GetFinalStateFileName(self,WithDate=False):
        if WithDate:
            return self.SetFormat('final_state_{}'.format(GetTimeStamp()))[1]
        else:
            return self.SetFormat('final_state')[1]



    def SaveFinalState(self,DataSet='regular'):
        self.Save(self.GetFinalStateFileName(),DataSet=DataSet,DataType='UEDGE',OverWrite=True)
        self.Save(self.GetFinalStateFileName(WithDate=True),DataSet=DataSet,DataType='UEDGE',OverWrite=True)
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
        try:
            from uedge import __version__
        except:
            __version__=None
        try:
            from uedge import GitHash
        except:
            GitHash=None

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
        ftol_dt=bbb.ftol_dt*self.AdjustFtolTime(bbb.dtreal,self.dt_ftol_threshold)
        if ftol_dt!=bbb.ftol_dt:
            self.PrintInfo('Increasing ftol_dt: ftol_dt={} | bbb.ftol_dt={}'.format(ftol_dt,bbb.ftol_dt))
        return max(min(ftol_dt, 0.01*fnrm_old),bbb.ftol_min)

    @staticmethod
    def AdjustFtolTime(dt,dt0=1e-11,p=2.5):
        if type(dt)!=np.ndarray:
            if dt>dt0:
                return 1.0
            else:
                return  (dt0/dt)**p
        else:
                f=(dt0/dt)**p
                f[(dt>dt0)]=1.0
                return f

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
        if self.Adjustftol:
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

    def SetContCall(self):
        if bbb.dtreal>=self.dt_ContCallOff_min and bbb.dtreal<=self.dt_ContCallOff_max:
            self.ContCall=False
        else:
            if self.dt_ContCallOff_min<self.dt_ContCallOff_max:
                self.ContCall=True












