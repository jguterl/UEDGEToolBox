#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 20:25:20 2020

@author: jguterl
"""
import os,sys
try:
    from uedge import bbb # just for compliance with python IDE rules. Do not do anything
except:
    pass

from colorama import  Back, Style,Fore
from datetime import date,datetime
#from UEDGEToolBox.DataManager.Grid import UBoxGrid
from UEDGEToolBox.Utils.Misc import BrowserFolder,QueryYesNo,GetTimeStamp
#from UEDGEToolBox.ProjectManager.Projects import UBoxSingleProject
from UEDGEToolBox.Simulation.Simulations import UBoxSimUtils
from UEDGEToolBox.Simulation.Input import UBoxInput
from UEDGEToolBox.DataManager.IO import UBoxIO
from UEDGEToolBox.Plot.PlotTest import UBoxPlotTest
import numpy as np
class UBoxSim(UBoxSimUtils,UBoxIO,UBoxInput,UBoxPlotTest):
    CaseName=None
    Verbose=False
    CurrentProject=None
    
    def __init__(self):
        super().__init__()
        self.CaseName=None
        self.Description='None'
        ListBefore=list(self.__dict__.keys())
        self.mult_dt_fwd=3.4
        self.mult_dt_bwd=3
        self._iSave=1
        self.ISave=10
        self.Imax=500
        self.Jmax=5
        self.SaveSim=True
        ListAfter=list(self.__dict__.keys())
        self.ListRunSettings=[k for k in ListAfter if k not in ListBefore]
         
    def Read(self,FileName=None,Initialize=False,Filter:str='*',OverWrite:dict={},ShowLines=False,Vars={},DicG=globals(),**kwargs)->None:
        """
        Parse and execute sequentialy a python script input file (*.py).

        If FileName is None, display a list of python script files present in Folder that the user can select from the console.
        Default folder is Inputdir from CurrentProject.
        After parsing and execution of the input file, UEDGE main engine is initialized if Initialize=True (see :method: Initialize()).
        Assignements in the input file can be overriden

        Note: ReadInput can be used recursevely in an input file.

        See Also:
            :method: Initialize()

        Args:
            FileName (str or None, optional): python script input file. Defaults to None.
            Folder (str, optional): Folder containing python script input file if FileName not found or not provided. Defaults to 'InputDir' from CurrentProject.
            Verbose (bool, optional): Display lines parsed and executed from the input file. Defaults to True.
            Initialize (bool, optional): DESCRIPTION. Defaults to False.
            Filter (str, optional): If FileName is None, display python script files in InputFile matching Filter . Defaults to '*'.
            ExternalVariables (dict, optional): Dictionary of variables and their values that will be overwritten when parsing and executing the input file. Defaults to {}.


        """
        # Explore Folder
        Folder='InputDir'
        
        #if hasattr(self,'CaseName'):
            #CaseName=self.CaseName
        #else:
        CaseName=None
            
        if hasattr(self,'CurrentProject'):
            Project=self.CurrentProject
        else:
            Project=None  
        
      
        if FileName is None:
            FilePath=BrowserFolder(self.Source(None,CaseName=CaseName,Folder=Folder,Project=Project),Filter=Filter,Ext='*.py',LoadMode=True)
        else:
            FilePath=self.Source(FileName,CaseName=CaseName,Folder=Folder,Project=Project)
            if FilePath is None:
                FilePath=self.Source(FileName,CaseName=CaseName,Folder='InputDir',Project=Project)
            if FilePath is None:
                FilePath=self.Source(FileName)
                
        if FilePath is None:
            raise IOError('No file read ...')
                
        # Looking for file
        
        print('Reading file {} '.format(FilePath))
        self.CurrentInputFile=FilePath
        
        self.ParseInputFile(FilePath,OverWrite,ShowLines,Vars,DicG)
        if Initialize:
            self.Initialize()
        return True
            
            
    def Cont(self,**kwargs):
        return self.Run(Restart=True,**kwargs)
    
    def Run(self,Restart=False,**kwargs):
        if Restart:
            bbb.restart=1
        else:
            bbb.restart=0
        for k,v in kwargs.items():
            if hasattr(self,k):
                setattr(self,k,v)
        return self.RunTime(**kwargs)

        
    
            
    def Save(self,FileName,Folder='SaveDir',DataSet=['regular','all'],DataType=['UEDGE','ProcessData'],ExtraTag={},OverWrite=False):
        """
        Save UEDGE simulation data
        See Save method of UEDGEIO class

        Args:
            FileName (TYPE): DESCRIPTION.
            CaseName (TYPE, optional): DESCRIPTION. Defaults to 'auto'.
            Folder (TYPE, optional): DESCRIPTION. Defaults to 'SaveDir'.
            Mode (TYPE, optional): DESCRIPTION. Defaults to 'regular'.
            ExtraVars (TYPE, optional): DESCRIPTION. Defaults to [].
            GlobalVars (TYPE, optional): DESCRIPTION. Defaults to [].
            Tag (TYPE, optional): DESCRIPTION. Defaults to {}.
            Format (TYPE, optional): DESCRIPTION. Defaults to None.
            ForceOverWrite (TYPE, optional): DESCRIPTION. Defaults to False.

        Returns:
            None.

        """
    
            
        if not self.SaveSim:
            return 
        
        
        Folder='SaveDir'
        
        if hasattr(self,'CaseName'):
            CaseName=self.CaseName
        else:
            CaseName=None
            
        if hasattr(self,'CurrentProject'):
            Project=self.CurrentProject
        else:
            Project=None    
        
        self.Tag=self.GetTag()
        self.Tag.update(ExtraTag)
        FilePath=self.Source(FileName,CaseName,Folder,Project,CreateFolder=True,EnforceExistence=False)
        
        if self.Verbose:
            print("Saving data in file:{}".format(FilePath))
        # Looking for file
        if os.path.exists(FilePath):
            if not OverWrite and not QueryYesNo('File {} exists. Do you want to overwrite it?'.format(FilePath)):
                print("No data saved in file:{}".format(FilePath))
                return
            
        self.SaveData(FilePath,DataSet,DataType,self.Tag)   
        

    # def SaveLog(self,FileName,Str,Tag={},Folder='SaveDir'):
    #     self.Tag=GenerateTag(self)
    #     self.Tag.update(Tag)
    #     FilePath=Source(FileName,Folder=Folder,Enforce=False,Verbose=self.Verbose,CaseName=self.CaseName,CheckExistence=False,CreateFolder=True)
    #     self.IO.SaveLog(FilePath,Str,self.Tag)
    def Load(self,FileName=None,DataSet=['all'],DataType=['UEDGE'],Ext='*.npy',EnforceDim=True,PrintStatus=False,Folder='SaveDir'):
        """
        Wrapper method to load UEDGE simulation data
        See Load method of UEDGEIO class
        Args:
            FileName (TYPE): DESCRIPTION.
            CaseName (TYPE, optional): DESCRIPTION. Defaults to None.
            Folder (TYPE, optional): DESCRIPTION. Defaults to 'SaveDir'.
            LoadList (TYPE, optional): DESCRIPTION. Defaults to [].
            ExcludeList (TYPE, optional): DESCRIPTION. Defaults to [].
            Format (TYPE, optional): DESCRIPTION. Defaults to 'numpy'.
            CheckCompat (TYPE, optional): DESCRIPTION. Defaults to True.
            Verbose (TYPE, optional): DESCRIPTION. Defaults to False.

        Returns:
            None.

        """
        
        
        if hasattr(self,'CaseName'):
            CaseName=self.CaseName
        else:
            CaseName=None
            
        if hasattr(self,'CurrentProject'):
            Project=self.CurrentProject
        else:
            Project=None    
            
        
        if FileName is None:
            FileName=BrowserFolder(self.Source(None,CaseName,Folder,Project),Ext=Ext)
        if FileName is None:
            raise IOError("Cannot read the file {}... Exiting".format(FileName))
           

        FilePath=self.Source(FileName,CaseName,Folder,Project)
        print("Loading data from file:{}".format(FilePath))
        # Looking for file
        if FilePath is not None and os.path.isfile(FilePath):
            (Data,Tag)=self.LoadData(FilePath)
            ListLoadedVar=self.ImportData(Data,DataSet,DataType,EnforceDim,PrintStatus,ReturnList=True)
            print('Loaded variables:',ListLoadedVar)
            return True
        else:
            print("Cannot read the file '{}'... Exiting".format(FileName))
            return False

        self.Init()
        bbb.restart=1
        
        
    def Restore(self,FileName:str or None=None,DataSet=['all',''],DataType=['UEDGE','DataStore'],EnforceDim=True,PrintStatus=False,OverWrite:dict={},ShowLines=False):
        """Read an input file, initalize UEDGE main engine and load plasma state variables into UEDGE from last.npy file in Folder SaveDir/Casename."""
        self.Read(FileName,Initialize=False,OverWrite=OverWrite,ShowLines=ShowLines)
        self.Load('last.npy',DataSet,DataType,EnforceDim,PrintStatus)
        bbb.restart=1
        self.Init()
        
        
    def RestoreLast(self,DataSet=['all',''],DataType=['UEDGE','DataStore'],EnforceDim=True,PrintStatus=False):
        """Read an input file, initalize UEDGE main engine and load plasma state variables into UEDGE from last.npy file in Folder SaveDir/Casename."""
        self.Load('last.npy',DataSet,DataType,EnforceDim,PrintStatus)
        bbb.restart=1
        bbb.newgeo=1
        self.Init()
        bbb.newgeo=0 
        
    def RestoreFinal(self,DataSet=['all'],DataType=['UEDGE'],EnforceDim=True,PrintStatus=False):
        """Read an input file, initalize UEDGE main engine and load plasma state variables into UEDGE from last.npy file in Folder SaveDir/Casename."""
        self.Load('final_state.npy',DataSet,DataType,EnforceDim,PrintStatus)
        bbb.restart=1
        bbb.newgeo=1
        self.Init()
        bbb.newgeo=0  
        
    def Initialize(self,ftol=1e20,restart=0,dtreal=1e10,SetDefaultNumerics=True):
        """
        Initialize UEDGE simulation

        Args:
            ftol (TYPE, optional): tolerance for nksol solver. Defaults to 1e20.
            restart (TYPE, optional): Restart status for exmain() (0|1). Defaults to 0.
            dtreal (TYPE, optional): timestep for nksol solver. Defaults to 1e10.
        """
        dtreal_bkp=bbb.dtreal
        ftol_bkp=bbb.ftol
        bbb.dtreal=dtreal
        bbb.ftol=ftol
        
        
        if (bbb.iterm == 1 and bbb.ijactot>1):
           self.PrintInfo("Initial successful time-step exists",Back.GREEN)
           #if SetDefaultNumerics: self.SetDefaultNumerics()
           bbb.dtreal=dtreal_bkp
           bbb.ftol=ftol_bkp
           return
        else:
           self.PrintInfo("Taking initial step with Jacobian:",Back.CYAN)
           bbb.icntnunk = 0
           
           ResetNewGeo=bbb.newgeo
           bbb.newgeo=1
           try:
            resetpandf=com.OMPParallelPandf1
            com.OMPParallelPandf1=0
           except:
               pass
           bbb.exmain()
           try:
             com.OMPParallelPandf1=resetpandf
           except:
               pass
           sys.stdout.flush()
           bbb.newgeo=ResetNewGeo
           
        if (bbb.iterm != 1):
            self.PrintInfo("Error: converge an initial time-step first",Back.RED)
            bbb.exmain_aborted=1
            bbb.dtreal=dtreal_bkp
            bbb.ftol=ftol_bkp
            #if SetDefaultNumerics: self.SetDefaultNumerics()
            return
        else:
           self.PrintInfo("First initial time-step has converged",Back.GREEN)
           #if SetDefaultNumerics: self.SetDefaultNumerics()
           bbb.dtreal=dtreal_bkp
           bbb.ftol=ftol_bkp
           return  
       
        
    def Init(self):
        """
        Initialize UEDGE simulation

        Args:
            ftol (TYPE, optional): tolerance for nksol solver. Defaults to 1e20.
            restart (TYPE, optional): Restart status for exmain() (0|1). Defaults to 0.
            dtreal (TYPE, optional): timestep for nksol solver. Defaults to 1e10.
        """
        bbb.ueinit()
        
    def Itrouble(self,OtherTrouble=False):
        ''' Function that displays information on the problematic equation '''
        from numpy import mod,argmax
        from uedge import bbb
        # Set scaling factor
        scalfac = bbb.sfscal
        ydmax = max(abs(bbb.yldot*scalfac))
        if (bbb.svrpkg[0].decode('UTF-8').strip() != "nksol"): scalfac = 1/(bbb.yl + 1.e-30)  # for time-dep calc.

        # Find the fortran index of the troublemaking equation
        itrouble=argmax(abs(bbb.yldot[0:bbb.neq]*scalfac[0:bbb.neq]))+1
        
        self.WhichEq(itrouble)
        if OtherTrouble:
            itroublenext=np.flip(np.argsort(abs(bbb.yldot[0:bbb.neq]*scalfac[0:bbb.neq])))[0:5]+1
            print("----------------- Next trouble makers -------------------")
            for i in itroublenext:
                self.WhichEq(i)
        



    def WhichEq(self,itrouble):
        ''' Function that displays information on the problematic equation '''
        from uedge import bbb
        from numpy import mod
        

        
        # Print equation information
        
        iv_t = mod(itrouble-1,bbb.numvar) + 1 # Use basis indexing for equation number
        
        # Verbose troublemaker equation
        if abs(bbb.idxte-itrouble).min()==0:
            Str='Electron energy equation [iv_t={}]'.format(iv_t)
        elif abs(bbb.idxti-itrouble).min()==0:
            Str='Ion energy equation [iv_t={}]'.format(iv_t)
        elif abs(bbb.idxphi-itrouble).min()==0:
            Str='Potential equation  [iv_t={}]'.format(iv_t)
        elif abs(bbb.idxu-itrouble).min()==0:
            for species in range(bbb.idxu.shape[2]):
                if abs(bbb.idxu[:,:,species]-itrouble).min()==0:
                    Str='Ion momentum equation of species Fortran:{} | python:{} [iv_t={}]'.format(species+1,species, iv_t)
        elif abs(bbb.idxn-itrouble).min()==0:
            for species in range(bbb.idxn.shape[2]):
                if abs(bbb.idxn[:,:,species]-itrouble).min()==0:
                    Str='Ion density equation of species Fortran:{} | python:{} [iv_t={}]'.format(species+1, species,iv_t)
        elif abs(bbb.idxg-itrouble).min()==0:
            for species in range(bbb.idxg.shape[2]):
                if abs(bbb.idxg[:,:,species]-itrouble).min()==0:
                    Str='Gas density equation of species Fortran:{} | python:{} [iv_t={}]'.format(species+1,species, iv_t)
        elif abs(bbb.idxtg-itrouble).min()==0:
            for species in range(bbb.idxtg.shape[2]):
                if abs(bbb.idxtg[:,:,species]-itrouble).min()==0:
                    Str='Gas temperature equation of species Fortran:{} | python:{} [iv_t={}]'.format(species+1,species, iv_t)
        # Display additional information about troublemaker cell
        idx=bbb.igyl[itrouble-1,]
        print(">>>> Troublemaker equation is: \n           {style}{color}{} at ix={}; iy={}{reset}\n".format(Str,idx[0],idx[1],style=Style.BRIGHT,color=Fore.GREEN,reset=Style.RESET_ALL))
        print(">>>> Trouble making equation for Fortran:iv={} | for python:iv={}".format(itrouble,itrouble-1))
        print(">>>> Timestep for troublemaker equation: {}".format(bbb.dtuse[itrouble-1]))
        print(">>>> yl for troublemaker equation:{}\n".format(bbb.yl[itrouble-1]))
        print(">>>> yldot={} and sfscal={} for trouble making equation".format(bbb.yldot[itrouble-1],bbb.sfscal[itrouble-1]))
        print(">>>> Number of equations solved per cell:numvar = {}".format(bbb.numvar))
        
        
    def Restart(self,**kwargs):
        self.Restore(**kwargs)
        return self.Cont()
    
    def RunTime(self,**kwargs):
        """

        Args:
            Verbose (TYPE, optional): DESCRIPTION. Defaults to False.

        Returns:
            Status='mainloop'|'tstop'|'dtkill'|'aborted'

        """

        bbb.exmain_aborted=0
        self.PrintInfo('----Starting Main Loop ----')
        while bbb.exmain_aborted==0:


            
# Main loop-----------------------------------------------
            for imain in range(self.Imax):
                
                self.Status='mainloop'
               
                bbb.icntnunk = 0
                self.Controlftol()
                bbb.ftol = self.Updateftol()
                
                

                self.PrintTimeStepModif(imain)

                
                self.PrintCurrentIteration(imain)
                try:
                    bbb.exmain() # take a single step at the present bbb.dtreal
                except Exception as e:
                    self.PrintError(e,imain)
                    self.Status='error'
                    return self.Status
                bbb.newgeo=0
                sys.stdout.flush()

                if bbb.exmain_aborted==1:
                    break

                if (bbb.iterm == 1 and bbb.exmain_aborted!=1):
                    self.AutoSave()
                    self.SaveLast() # Save data in file SaveDir/CaseName/last.npy
                    bbb.dt_tot += bbb.dtreal
                    self.dt_tot=bbb.dt_tot
                    #self.TimeEvolution()

                    if bbb.dt_tot>=bbb.t_stop:
                            bbb.exmain_aborted=1
                            self.SaveFinalState()
                            self.Status='tstop'
                            return self.Status

                    if (bbb.ijactot>1):
# Second loop -----------------------------------------------------------------------------------
                        bbb.icntnunk = 1
                        bbb.isdtsfscal = 0
                        
                        for ii2 in range(self.Jmax): #take ii2max steps at the present time-step
                            if bbb.exmain_aborted==1:
                                break
                            bbb.ftol = self.Updateftol()
                            self.PrintCurrentIteration(imain,ii2)
                            try:
                                bbb.exmain() # take a single step at the present bbb.dtreal
                            except Exception as e:
                                self.PrintError(e,imain,ii2)
                                self.Status='error'
                                return self.Status
                            sys.stdout.flush()
    
                            if bbb.iterm == 1 and bbb.exmain_aborted!=1:
                                self.SaveLast() # Save data in file SaveDir/CaseName/last.npy
                                bbb.dt_tot += bbb.dtreal
                                self.dt_tot=bbb.dt_tot
                                #self.TimeEvolution()
                            else:
                                break
    
                            if bbb.dt_tot>=bbb.t_stop:
                                self.PrintInfo('SUCCESS: dt_tot >= t_stop')
                                self.SaveFinalState()
                                self.Status='tstop'
                                return self.Status
    # End Second loop -----------------------------------------------------------------------------------

                if bbb.exmain_aborted==1:
                    break

# Handle success/error ------------------------------------------------------------------------------
                if (bbb.iterm == 1):
                    bbb.dtreal *= self.mult_dt_fwd
                    self.dtreal=bbb.dtreal

                else:    #print bad eqn, cut dtreal by 3
                    self.Itrouble()

                    self.PrintInfo('Converg. fails for bbb.dtreal; reduce time-step by 3',Back.RED)
                    bbb.dtreal /= self.mult_dt_bwd
                    self.dtreal=bbb.dtreal
#                    if bbb.iterm==2 and bbb.dtreal<self.dtLowThreshold:


                    bbb.iterm = 1

                    if (bbb.dtreal < bbb.dt_kill):
                        self.PrintInfo('FAILURE: time-step < dt_kill',Back.RED)
                        bbb.exmain_aborted=1
                        self.Status='dtkill'
                        return self.Status
# End of main loop -------------------------------------------------------- --------------------------------
        if bbb.exmain_aborted==1: self.Status='aborted'
        return self.Status