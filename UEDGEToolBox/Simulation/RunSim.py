#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from UEDGEToolBox.Simulation.Sim import UBoxSim
from UEDGEToolBox.Utils.Misc import LsFolder
from UEDGEToolBox.Utils.Doc import UBoxDoc
from UEDGEToolBox.DataManager.Grid import UBoxGrid
from uedge import bbb
from uedge import *
import sys,os
from colorama import  Back, Style


class UBoxRunSettings():
                 
            
       @staticmethod
       def DefaultNumerics():
            Dic={}
            Dic['dtreal']=1e-8
            Dic['t_stop']=10
            Dic['ftol_min']=1e-10
            Dic['ftol_dt']=1e-10
            Dic['ftol']=1e-8
            Dic['itermx']=7
            Dic['rlx']=0.9
            Dic['incpset']=7
            Dic['isbcwdt']=1
            return Dic
        
       def SetDefaultNumerics(self):
           self.SetPackageParams(self.DefaultNumerics())
        
       def OverrideObjectParams(self,**kwargs):
        """

        Args:
            **kwargs (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        for k,v in kwargs.items():
            if self.__dict__.get(k) is not None:
                self.__dict__[k]=v
       
       def SetPackageParams(self,Dic:dict):
        """
        Args:
            Verbose (TYPE, optional): DESCRIPTION. Defaults to False.

        Returns:
            None.
        """
        for A,V in Dic.items():
            if V is not None:
                if not hasattr(self,'Doc') or self.Doc is None:
                    self.Doc=UBoxDoc()
                Result=self.Doc.Search(A.split('[')[0],Exact=True,Silent=True)
                if len(Result)>0:
                    Pkg=Result[0]['Package']
                    comm='{}.{}={}'.format(Pkg,A,V)
                    if self.Verbose: print(comm)
                    try:
                        exec(comm,globals(),globals())
                    except:
                        print('Cannot set {}.{} = {} '.format(Pkg,A,V))
                else:
                    print('No package found for {}'.format(A))
                
                    
       def SetUEDGEParams(self,**kwargs):
        """

        Args:
            Verbose (TYPE, optional): DESCRIPTION. Defaults to False.

        Returns:
            None.

        """
        for k,v in kwargs:
            pass
            
            #self.UEDGELoader(Pkg,k,VarValue,True,False)
            
        # self.OverrideObjectParams(**kwargs)
        # Params=dict((k,v) for (k,v) in kwargs.items() if not k in self.ListRunSettings)
        # self.SetPackageParams(Params)
        
class UBoxRun(UBoxSim,UBoxRunSettings):
    """ Main class to run an UEDGE simulation.

    This class contains methods to run, save and restore UEDGE simulation.
    An instance of this class "Sim" is automatically created when the module uedge is imported.
    This class is derived from UEDGESimBase, which containes the method Run() which is the equilent of rdrundt/rdcondt and Show

    Methods:

    Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
    


    # def __new__(cls, Parent=None):
    #     if Parent is not None:
    #         Parent.__class__ = UBoxSim
    #         return Parent

    def __init__(self,Parent=None,Verbose=False,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.SetPackageParams(self.DefaultNumerics())
        self.Verbose=Verbose
        print('UBoxRun initialized')
        
    def DisplayGrid(self,FileName=None,Project=None,Folder='GridDir'):
        """ """
            
        Ext='*'
        
        if hasattr(self,'CurrentProject') and Project is None:
            Project=self.CurrentProject

        if FileName is None:
            FileName=LsFolder(self.Source(None,None,Folder,Project),Ext=Ext)
        if FileName is None:
            print("Cannot read the file {}... Exiting".format(FileName))
            return

        FilePath=self.Source(FileName,None,Folder,Project)
        if self.Verbose:
            print("Loading data from file:{}".format(FilePath))
        # Looking for file
        if FilePath is not None and os.path.isfile(FilePath):
            UGrid=UBoxGrid()
            UGrid.ImportGrid(FilePath)
            UGrid.PlotGrid(Title=FilePath) 
        else:
            print("Cannot read the file {}... Exiting".format(FilePath))


    


    
    
    

    





   
        
    
    # def RunRamp(self,Data:dict,Istart=0,dtreal_start=1e-8,tstop=10):
    #     """
    
    
    #     Args:
    #         Data (dict): DESCRIPTION.
    #         Istart (TYPE, optional): DESCRIPTION. Defaults to 0.
    #         dtreal_start (TYPE, optional): DESCRIPTION. Defaults to 1e-8.
    #         tstop (TYPE, optional): DESCRIPTION. Defaults to 10.
    
    #     Returns:
    #         None.
    
    #     """
    
    #     #Check if all data arrays have the same length
    #     List=[v.shape for (k,v) in Data.items()]
    #     if not all(L == List[0] for L in List):
    #         print('Arrays of different size... Cannot proceed...')
    #         return
    #     Istop=List[0][0]
    #     if Istart>=Istop:
    #         print('Istart={} >= Istop={}: cannot proceed...'.format(Istart,Istop))
    #     irun=Istart
    #     # Loop over data
    
    
    #     while irun <Istop:
    
    #         # 1) Set data in uedge packages
    #         Params=dict((k,v[irun]) for (k,v) in Data.items())
    #         ListParams=['{}:{}'.format(k,v) for k,v in Params.items()]
    #         self.SetPackageParams(Params)
    
    #         # 2) Run until completion
    #         self.PrintInfo('RAMP i={}/{} : '.format(irun,Istop)+','.join(ListParams),color=Back.MAGENTA)
    #         Status=self.Cont(dt_tot=0,dtreal=dtreal_start,t_stop=tstop)
    #         if Status=='tstop':
    #             ListValueParams=['{:2.2e}'.format(v) for k,v in Params.items()]
    #             self.Save('final_state_ramp_'+'_'.join(ListValueParams))
    #             self.SaveLog('logramp','{}:{}::'.format(self.Tag['Date'],self.Tag['Time'])+';'.join(ListParams))
    #             irun+=1
    #         else:
    #             print('Exiting ramp... Need to add a routine to restart after dtkill')
    #             return

def TogglePlasma():
    bbb.isnion[0]=Toggle(bbb.isnion[0])
    bbb.isupon[0]=Toggle(bbb.isupon[0])
    bbb.istion=Toggle(bbb.istion)
    bbb.isteon=Toggle(bbb.isteon)

def TurnOffPlasma():
    bbb.isnion[0]=0
    bbb.isupon[0]=0
    bbb.istion=0
    bbb.isteon=0

def TurnOnPlasma():
    bbb.isnion[0]=1
    bbb.isupon[0]=1
    bbb.istion=1
    bbb.isteon=1

def Toggle(State):
    if State ==0:
        return 1
    elif State == 1:
        return 0
    else:
        raise ValueError('Cannot toggle request variable in state:{}'.format(State))





#---------------------------------------------------------------------------------------------------------------


eV=1.602176634e-19     #%%




    