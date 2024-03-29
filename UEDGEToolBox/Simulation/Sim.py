#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 20:25:20 2020

@author: jguterl
"""
import os
import sys
try:
    from uedge import bbb  # just for compliance with python IDE rules. Do not do anything
except Exception:
    pass

from colorama import Back, Style, Fore
from UEDGEToolBox.Utils.Misc import BrowserFolder, QueryYesNo
from UEDGEToolBox.Simulation.SimUtils import UBoxSimUtils
from UEDGEToolBox.Simulation.SimExt import UBoxSimExt
from UEDGEToolBox.Simulation.Input import UBoxInput
from UEDGEToolBox.DataManager.IO import UBoxIO
from UEDGEToolBox.Simulation.livedata import UBoxLiveData
from UEDGEToolBox.Simulation.liveplot import  UBoxLivePlot
from UEDGEToolBox.Plot.Plot import UBoxPlot
import numpy as np


class UBoxSim(UBoxSimUtils,UBoxLivePlot,UBoxLiveData, UBoxIO, UBoxInput, UBoxPlot,UBoxSimExt):
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
    CaseName = None
    Verbose = False
    CurrentProject = None

    def __init__(self,*args,**kwargs):
        print('UBOXSim init ----------------------------------------------')

        #super(UBoxLivePlot,self).__init__(*args,**kwargs)
        self.livedata = {}
        self.niter_collect = 0
        self.iter_collect = 0
        self.iter_data = 0
        self.data_collected = False
        self.livedata_vars = ['ni','ng','te','ti','up']
        self.storage = 10000
        self.liveplot = False
        self.ax_dens = None
        self.ax_flx = None
        self.plot_list = ['Gdes_l','Gdes_r','inflx']
        self.plot_dens_list = ['dens']
        self.plt_obj_flx = {}
        self.plt_obj_dens = {}
        self.plot_dens_ylim = [1e9,1e25]
        self.plot_flx_ylim = [1e15,1e22]
        self.plot_flx_xlim = []
        self.iter = 0
        self.save_last = True


        super().__init__()

        self.CaseName = None
        self.Description = 'None'
        # ListBefore=list(self.__dict__.keys())
        self._iSave = 1
        self._imain = 0

        # ListAfter=list(self.__dict__.keys())
        #self.ListRunSettings=[k for k in ListAfter if k not in ListBefore]

    def Read(self, FileName=None, Filter: str = '*', ExtraCommand: list = [], ShowLines=False, Vars={}, DicG=globals(), **kwargs) -> None:
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
        Folder = 'InputDir'

        # if hasattr(self,'CaseName'):
        # CaseName=self.CaseName
        # else:
        CaseName = None

        if hasattr(self, 'CurrentProject'):
            Project = self.CurrentProject
        else:
            Project = None

        if FileName is None:
            FilePath = BrowserFolder(self.Source(None, CaseName=CaseName, Folder=Folder, Project=Project), Filter=Filter, Ext='*.py', LoadMode=True)
        else:
            FilePath = self.Source(FileName, CaseName=CaseName, Folder=Folder, Project=Project)
            if FilePath is None:
                FilePath = self.Source(FileName, CaseName=CaseName, Folder='InputDir', Project=Project)
            if FilePath is None:
                FilePath = self.Source(FileName)

        if FilePath is None:
            raise IOError('No file read ...')

        # Looking for file

        print('Reading file {} '.format(FilePath))
        self.CurrentInputFile = FilePath

        self.ParseInputFile(FilePath, ExtraCommand, ShowLines, Vars, DicG)
        return True

    def Cont(self, **kwargs):
        return self.Run(Restart=True, **kwargs)
# WARNING: restart must be turned to 1 to actually updates state variables in UEDGE...
    def Run(self, Restart=True, **kwargs):
        if Restart:
            bbb.restart = 1
        else:
            bbb.restart = 0
        return self.RunTime(**kwargs)

    def Save(self, FileName, Folder='SaveDir', DataSet=['regular', 'all'], DataType=['UEDGE', 'ProcessData'], ExtraTag={}, OverWrite=False):
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

        Folder = 'SaveDir'

        if hasattr(self, 'CaseName'):
            CaseName = self.CaseName
        else:
            CaseName = None

        if hasattr(self, 'CurrentProject'):
            Project = self.CurrentProject
        else:
            Project = None

        self.Tag = self.GetTag()
        self.Tag.update(ExtraTag)
        FilePath = self.Source(FileName, CaseName, Folder, Project, CreateFolder=True, EnforceExistence=False)

        if self.Verbose:
            print("Saving data in file:{}".format(FilePath))
        # Looking for file
        if os.path.exists(FilePath):
            if not OverWrite and not QueryYesNo('File {} exists. Do you want to overwrite it?'.format(FilePath)):
                print("No data saved in file:{}".format(FilePath))
                return

        self.SaveData(FilePath, DataSet, DataType, self.Tag)

    # def SaveLog(self,FileName,Str,Tag={},Folder='SaveDir'):
    #     self.Tag=GenerateTag(self)
    #     self.Tag.update(Tag)
    #     FilePath=Source(FileName,Folder=Folder,Enforce=False,Verbose=self.Verbose,CaseName=self.CaseName,CheckExistence=False,CreateFolder=True)
    #     self.IO.SaveLog(FilePath,Str,self.Tag)
    def LoadPlasma(self, FileName=None, **kwargs):
        return self.Load(FileName=FileName, DataSet=['plasmavarss', 'plasmavars'], DataType='UEDGE', **kwargs)

    def LoadPlasmaFinal(self, CaseName=None, **kwargs):
        return self.Load(FileName=self.GetFinalStateFileName(), DataSet=['plasmavarss', 'plasmavars'], DataType='UEDGE', CaseName=CaseName, **kwargs)

    def Load(self, FileName=None, DataSet=['all'], DataType=['UEDGE'], Ext='*.npy', EnforceDim=True, PrintStatus=False, Folder='SaveDir', Init=True, CaseName=None):
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

        if CaseName is None:
            if hasattr(self, 'CaseName'):
                CaseName = self.CaseName

        if hasattr(self, 'CurrentProject'):
            Project = self.CurrentProject
        else:
            Project = None

        if FileName is None:
            FileName = BrowserFolder(self.Source(None, CaseName, Folder, Project), Ext=Ext)
        if FileName is None:
            raise IOError("Cannot read the file {}... Exiting".format(FileName))

        FilePath = self.Source(FileName, CaseName, Folder, Project)
        print("Loading data from file:{}".format(FilePath))
        # Looking for file
        if FilePath is not None and os.path.isfile(FilePath):
            (Data, Tag) = self.LoadData(FilePath)
            ListLoadedVar = self.ImportData(Data, DataSet, DataType, EnforceDim, PrintStatus, ReturnList=True)
            print('Loaded variables:', ListLoadedVar)
            if Init:
                self.Init()
                bbb.restart = 1
            return True
        else:
            print("Cannot read the file '{}'... Exiting".format(FileName))
            return False

    def Restore(self, FileName: str or None = None, DataSet=['all'], DataType=['UEDGE'], EnforceDim=True, PrintStatus=False, ExtraCommand: dict = [], ShowLines=False, **kwargs):
        """Read an input file, initalize UEDGE main engine and load plasma state variables into UEDGE from last.npy file in Folder SaveDir/Casename."""
        self.Read(FileName, Initialize=False, ExtraCommand=ExtraCommand, ShowLines=ShowLines)
        Status = self.Load('last.npy', DataSet, DataType, EnforceDim, PrintStatus)
        if Status:
            bbb.restart = 1
            return True
        else:
            return False

    def RestoreLast(self, DataSet=['all', ''], DataType=['UEDGE', 'DataStore'], EnforceDim=True, PrintStatus=False):
        """Read an input file, initalize UEDGE main engine and load plasma state variables into UEDGE from last.npy file in Folder SaveDir/Casename."""
        self.Load('last.npy', DataSet, DataType, EnforceDim, PrintStatus)
        bbb.restart = 1
        bbb.newgeo = 1
        self.Init()
        bbb.newgeo = 0

    def RestoreFinal(self, DataSet=['all'], DataType=['UEDGE'], EnforceDim=True, PrintStatus=False):
        """Read an input file, initalize UEDGE main engine and load plasma state variables into UEDGE from last.npy file in Folder SaveDir/Casename."""
        self.Load('final_state.npy', DataSet, DataType, EnforceDim, PrintStatus)
        bbb.restart = 1
        bbb.newgeo = 1
        self.Init()
        bbb.newgeo = 0

    def Initialize(self, ftol=1e20, restart=0, dtreal=1e10, SetDefaultNumerics=True):
        """
        Initialize UEDGE simulation

        Args:
            ftol (TYPE, optional): tolerance for nksol solver. Defaults to 1e20.
            restart (TYPE, optional): Restart status for exmain() (0|1). Defaults to 0.
            dtreal (TYPE, optional): timestep for nksol solver. Defaults to 1e10.
        """
        dtreal_bkp = bbb.dtreal
        ftol_bkp = bbb.ftol
        bbb.dtreal = dtreal
        bbb.ftol = ftol

        if (bbb.iterm == 1 and bbb.ijactot > 1):
            self.PrintInfo("Initial successful time-step exists", Back.GREEN)
            #if SetDefaultNumerics: self.SetDefaultNumerics()
            bbb.dtreal = dtreal_bkp
            bbb.ftol = ftol_bkp
            return
        else:
            self.PrintInfo("Taking initial step with Jacobian:", Back.CYAN)
            bbb.icntnunk = 0

            ResetNewGeo = bbb.newgeo
            bbb.newgeo = 1
            try:
                resetpandf = com.OMPParallelPandf1
                com.OMPParallelPandf1 = 0
            except:
                pass
            bbb.exmain()
            try:
                com.OMPParallelPandf1 = resetpandf
            except:
                pass
            sys.stdout.flush()
            bbb.newgeo = ResetNewGeo

        if (bbb.iterm != 1):
            self.PrintInfo("Error: converge an initial time-step first", Back.RED)
            bbb.exmain_aborted = 1
            bbb.dtreal = dtreal_bkp
            bbb.ftol = ftol_bkp
            #if SetDefaultNumerics: self.SetDefaultNumerics()
            return
        else:
            self.PrintInfo("First initial time-step has converged", Back.GREEN)
            #if SetDefaultNumerics: self.SetDefaultNumerics()
            bbb.dtreal = dtreal_bkp
            bbb.ftol = ftol_bkp
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

    def Itrouble(self, OtherTrouble=False):
        ''' Function that displays information on the problematic equation '''
        from numpy import mod, argmax
        from uedge import bbb
        # Set scaling factor
        scalfac = bbb.sfscal
        ydmax = max(abs(bbb.yldot * scalfac))
        if (bbb.svrpkg[0].decode('UTF-8').strip() != "nksol"):
            scalfac = 1 / (bbb.yl + 1.e-30)  # for time-dep calc.

        # Find the fortran index of the troublemaking equation
        itrouble = argmax(abs(bbb.yldot[0:bbb.neq] * scalfac[0:bbb.neq])) + 1

        self.WhichEq(itrouble)
        if OtherTrouble:
            itroublenext = np.flip(np.argsort(abs(bbb.yldot[0:bbb.neq] * scalfac[0:bbb.neq])))[0:5] + 1
            print("----------------- Next trouble makers -------------------")
            for i in itroublenext:
                self.WhichEq(i)

    def WhichEq(self, itrouble):
        ''' Function that displays information on the problematic equation '''
        from uedge import bbb
        from numpy import mod

        # Print equation information

        iv_t = mod(itrouble - 1, bbb.numvar) + 1  # Use basis indexing for equation number

        # Verbose troublemaker equation
        if abs(bbb.idxte - itrouble).min() == 0:
            Str = 'Electron energy equation [iv_t={}]'.format(iv_t)
        elif abs(bbb.idxti - itrouble).min() == 0:
            Str = 'Ion energy equation [iv_t={}]'.format(iv_t)
        elif abs(bbb.idxphi - itrouble).min() == 0:
            Str = 'Potential equation  [iv_t={}]'.format(iv_t)
        elif abs(bbb.idxu - itrouble).min() == 0:
            for species in range(bbb.idxu.shape[2]):
                if abs(bbb.idxu[:, :, species] - itrouble).min() == 0:
                    Str = 'Ion momentum equation of species Fortran:{} | python:{} [iv_t={}]'.format(species + 1, species, iv_t)
        elif abs(bbb.idxn - itrouble).min() == 0:
            for species in range(bbb.idxn.shape[2]):
                if abs(bbb.idxn[:, :, species] - itrouble).min() == 0:
                    Str = 'Ion density equation of species Fortran:{} | python:{} [iv_t={}]'.format(species + 1, species, iv_t)
        elif abs(bbb.idxg - itrouble).min() == 0:
            for species in range(bbb.idxg.shape[2]):
                if abs(bbb.idxg[:, :, species] - itrouble).min() == 0:
                    Str = 'Gas density equation of species Fortran:{} | python:{} [iv_t={}]'.format(species + 1, species, iv_t)
        elif abs(bbb.idxtg - itrouble).min() == 0:
            for species in range(bbb.idxtg.shape[2]):
                if abs(bbb.idxtg[:, :, species] - itrouble).min() == 0:
                    Str = 'Gas temperature equation of species Fortran:{} | python:{} [iv_t={}]'.format(species + 1, species, iv_t)
        # Display additional information about troublemaker cell
        idx = bbb.igyl[itrouble - 1, ]
        print(">>>> Troublemaker equation is: \n           {style}{color}{} at ix={}; iy={}{reset}\n".format(Str, idx[0], idx[1], style=Style.BRIGHT, color=Fore.GREEN, reset=Style.RESET_ALL))
        print(">>>> Trouble making equation for Fortran:iv={} | for python:iv={}".format(itrouble, itrouble - 1))
        print(">>>> Timestep for troublemaker equation: {}".format(bbb.dtuse[itrouble - 1]))
        print(">>>> yl for troublemaker equation:{}\n".format(bbb.yl[itrouble - 1]))
        print(">>>> yldot={} and sfscal={} for trouble making equation".format(bbb.yldot[itrouble - 1], bbb.sfscal[itrouble - 1]))
        print(">>>> Number of equations solved per cell:numvar = {}".format(bbb.numvar))

    def Restart(self, **kwargs):
        self.Restore(**kwargs)
        return self.Cont(**kwargs)

    def RunTime(self, RestartfromNegative=True, **kwargs):
        """

        Args:
            Verbose (TYPE, optional): DESCRIPTION. Defaults to False.

        Returns:
            Status='mainloop'|'tstop'|'dtkill'|'aborted'

        """
        self.SetPackageParams(kwargs, self)
        self.SetUEDGEParams(kwargs)
        bbb.exmain_aborted = 0
        self.PrintInfo('----Starting Main Loop ----')

# Main loop-----------------------------------------------
        for imain in range(self.Imax):
            self._imain = imain
            self.Status = 'mainloop'

            bbb.icntnunk = 0
            self.Controlftol()
            bbb.ftol = self.Updateftol()

            self.ApplyRunTimeModifier(**kwargs)

            self.PrintTimeStepModif(imain)
            self.SetContCall()

            self.PrintCurrentIteration(imain)
            try:
                bbb.exmain()  # take a single step at the present bbb.dtreal
            except Exception as e:
                if bbb.iterm != -100 or not self.RestartfromNegative:
                    self.PrintError(e, imain)
                    self.Status = 'error'
                    return self.Status
            bbb.newgeo = 0
            sys.stdout.flush()

            if bbb.exmain_aborted == 1:
                break

            if ((bbb.iterm == 1 or self.fnrm_old<self.fnrm_threshold) and bbb.exmain_aborted != 1):
                self.AutoSave()
                self.livedata_collector()
                self.plot_live()
                if self.save_last: self.SaveLast()  # Save data in file SaveDir/CaseName/last.npy
                bbb.dt_tot += bbb.dtreal
                self.dt_tot = bbb.dt_tot
                # self.TimeEvolution()

                if bbb.dt_tot >= bbb.t_stop:
                    bbb.exmain_aborted = 1
                    self.SaveFinalState()
                    self.Status = 'tstop'
                    return self.Status

                if (bbb.ijactot > 1):
                    # Second loop -----------------------------------------------------------------------------------
                    if self.ContCall:
                        bbb.icntnunk = 1
                    bbb.isdtsfscal = 0

                    for ii2 in range(self.Jmax):  # take ii2max steps at the present time-step
                        if bbb.exmain_aborted == 1:
                            break
                        bbb.ftol = self.Updateftol()
                        self.ApplyRunTimeModifier(**kwargs)
                        self.PrintCurrentIteration(imain, ii2)
                        try:
                            bbb.exmain()  # take a single step at the present bbb.dtreal
                        except Exception as e:
                            if bbb.iterm == -100 and self.RestartfromNegative:
                                break
                            else:
                                self.PrintError(e, imain, ii2)
                                self.Status = 'error'
                                return self.Status

                        sys.stdout.flush()

                        if (bbb.iterm == 1 or self.fnrm_old<self.fnrm_threshold) and bbb.exmain_aborted != 1:
                            if self.save_last: self.SaveLast()  # Save data in file SaveDir/CaseName/last.npy
                            self.livedata_collector()
                            self.plot_live()
                            bbb.dt_tot += bbb.dtreal
                            self.dt_tot = bbb.dt_tot
                            # self.TimeEvolution()
                        else:
                            break

                        if bbb.dt_tot >= bbb.t_stop:
                            self.PrintInfo('SUCCESS: dt_tot >= t_stop')
                            self.SaveFinalState()
                            self.Status = 'tstop'
                            return self.Status
# End Second loop -----------------------------------------------------------------------------------

            if bbb.exmain_aborted == 1:
                break

# Handle success/error ------------------------------------------------------------------------------
            if (bbb.iterm == 1 or self.fnrm_old<self.fnrm_threshold):
                bbb.dtreal *= self.mult_dt_fwd
                self.dtreal = bbb.dtreal
            elif bbb.iterm == -100:
                self.RestartfromNegative()
            else:  # print bad eqn, cut dtreal by 3
                self.Itrouble()

                self.PrintInfo('Converg. fails for bbb.dtreal; reduce time-step by 3', Back.RED)
                bbb.dtreal /= self.mult_dt_bwd
                self.dtreal = bbb.dtreal
#                    if bbb.iterm==2 and bbb.dtreal<self.dtLowThreshold:

                bbb.iterm = 1

                if (bbb.dtreal < bbb.dt_kill):
                    self.PrintInfo('FAILURE: time-step < dt_kill', Back.RED)
                    bbb.exmain_aborted = 1
                    self.Status = 'dtkill'
                    return self.Status
# End of main loop -------------------------------------------------------- --------------------------------
        if bbb.exmain_aborted == 1:
            self.Status = 'aborted'
        return self.Status

    @staticmethod
    def RobustStart(dt_threshold=1e-7, mult_dt_bwd=1.5, mult_dt_fwd=3.4, itermx=100, ContCall=False):

        def Func(self, **kwargs):
            if self._imain < 10:
                bbb.itermx = itermx

            if dt_threshold < bbb.dtreal:
                self.ContCall = True
                self.Jmax = self.UBoxRunDefaults['Jmax']
                self.mult_dt_bwd = self.UBoxRunDefaults['mult_dt_bwd']
                self.mult_dt_fwd = self.UBoxRunDefaults['mult_dt_fwd']
            else:
                self.ContCall = ContCall
                self.mult_dt_bwd = mult_dt_bwd
                self.mult_dt_fwd = mult_dt_fwd

        return Func

    @staticmethod
    def set_recycp(recycface):
        bbb.recycp = recycface + (1.-np.exp(-ebar/(bbb.bcei*bbb.ti[nx,1]))) * (1.-recycface)
        bbb.albedorb[0,0] = recycface + (1.-np.exp(-ebar/(2.*bbb.ti[nx,1]))) * (1.-recycface)
    @staticmethod
    def get_fluxes(ebar):
        from uedge import bbb, com
        pflux = bbb.fnix[com.nx,1,0]/com.sx[com.nx,1]*np.exp(-ebar/(bbb.bcei*bbb.ti[com.nx,1]))+bbb.ni[com.nx,1,1]*np.sqrt(bbb.ti[com.nx,1]/(2.*np.pi*bbb.mi[0]))*np.exp(-ebar/(2.*bbb.ti[com.nx,1]))
        qflux  = np.sum(bbb.feix[com.nx,:]+bbb.feex[com.nx,:])/np.sum(com.sx[com.nx,:])+bbb.sdrrb[1,0]+bbb.sbindrb[1,0]
        return pflux, qflux

    def ApplyRunTimeModifier(self, Modifier: list or None = None, **kwargs):

        if Modifier is not None:
            if type(Modifier) != list:
                Modifier = [Modifier]
            if self.Verbose:
                print('Modifider:', Modifier)
            for M in Modifier:
                M(self, **kwargs)