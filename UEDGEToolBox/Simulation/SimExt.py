#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 21:59:13 2020

@author: jguterl
"""
from UEDGEToolBox.Utils.Misc import GetListPackage
from colorama import  Back, Style

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
    # def RunRamp(self,Data:dict,Istart:int=0,dtreal_start:float=1e-8,tstop:float=10):
    #     """

    #     Args:
    #         Data (dict): ebbb.g. Dic={'ncore[0]':np.linspace(1e19,1e20,10),'pcoree':np.linspace(0.5e6,5e6,10)}
    #         Istart (int, optional): DESCRIPTION. Defaults to 0.
    #         dtreal_start (float, optional): DESCRIPTION. Defaults to 1e-8.
    #         tstop (float, optional): DESCRIPTION. Defaults to 10.

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

    #     BaseCaseName=self.CaseName
    #     while irun <Istop:

    #         # 1) Set data in uedge packages
    #         Params=dict((k,v[irun]) for (k,v) in Data.items())
    #         ListParams=['{}:{}'.format(k,v) for k,v in Params.items()]
    #         StrParams=['{}_{:2.2e}'.format(k.split('[')[0],v) for k,v in Params.items()]

    #         self.CaseName=BaseCaseName+'_'.join(StrParams)
    #         self.SetPackageParams(Params)

    #         # 2) Run until completion
    #         self.PrintInfo('RAMP i={}/{} : '.format(irun,Istop)+','.join(ListParams),color=Back.MAGENTA)
    #         FileName='final_state_ramp_'+'_'.join(ListValueParams)
    #         FilePath=UEDGEToolBox.Source(FileName,Folder='SaveDir',Enforce=False,Verbose=Verbose,CaseName=self.CaseName,CheckExistence=False)
    #         if CheckFileExist(FilePath):
    #             print('File {} exists. Skipping this ramp step...'.format(FilePath))
    #             continue

    #         Status=self.Cont(dt_tot=0,dtreal=dtreal_start,t_stop=tstop)
    #         if Status=='tstop':
    #             ListValueParams=['{:2.2e}'.format(v) for k,v in Params.items()]
    #             self.Save('final_state_ramp_'+'_'.join(ListValueParams))
    #             self.SaveLog('logramp','{}:{}::'.format(self.Tag['Date'],self.Tag['Time'])+';'.join(ListParams))
    #             irun+=1
    #         else:
    #             print('Exiting ramp... Need to add a routine to restart after dtkill')
    #             return 
            
            
            
    def SetParamValue(self,Param,Value):
        for pkg in GetListPackage():
                exec('from uedge import '+pkg,globals(),locals())
        Line='{}={}'.format(Param,Value)
        try:
            exec(Line,globals(),locals())
            return Line
        except Exception as e:
            print('\n {color}>>>>>> Last line executed: {}{reset}\n'.format(L,color=Back.RED,reset=Style.RESET_ALL))
            return ''
        
    def RestartfromNegative(self):
        from uedge import bbb
        self.LoadPlasma('last.npy')
        self.PrintInfo('Converg. fails due to negative densities: time-step reduced by 100',Back.RED)
        bbb.iterm = 1
        bbb.dtreal/=10
          
    def RunRamp(self,RampVariable:str,RampValues:list or np.array,iter_start=0,FileName=None,dtreal:float=5e-8,t_stop:float=10,ForceRun=False,LoadLast=True,ThresholdDens=False,**kwargs):
        """

        Args:
            Data (dict): ebbb.g. Dic={'ncore[0]':np.linspace(1e19,1e20,10),'pcoree':np.linspace(0.5e6,5e6,10)}
            Istart (int, optional): DESCRIPTION. Defaults to 0.
            dtreal_start (float, optional): DESCRIPTION. Defaults to 5e-8.
            tstop (float, optional): DESCRIPTION. Defaults to 10.

        Returns:
            None.

        """
        
        #self.Restore(FileName)
        BaseCaseName = self.CaseName
        print('Starting ramp from Input: {}'.format(FileName))
        print('BaseCaseName: {}'.format(BaseCaseName))
        print('Starting ramp for {} with values:{}'.format(RampVariable,RampValues))
        Niter=len(RampValues)
        self.InputLines.append('')
        for i,V in enumerate(RampValues[iter_start:]):
            StrParams=['{}_{:2.3e}'.format(RampVariable.split('[')[0].split('.')[-1],V)]
            self.CaseName = BaseCaseName+'_'+'_'.join(StrParams)
            self.PrintInfo('Ramp iteration i={}/{} : {}={} : {}'.format(i+1,Niter,RampVariable,V,self.CaseName),color=Back.MAGENTA)
            
            self.InputLines[-1] = self.SetParamValue(RampVariable,V)
            FileName = 'final_state_ramp.npy'
            FilePath=self.Source(FileName,Folder='SaveDir',EnforceExistence=False,CreateFolder=True)
            
            
            if self.Load(FilePath) and not ForceRun:
                print('Final state exists and loaded. Skipping this ramp iteration...')
                continue
            else:
                RampInfo=["RampVariable:{}\n".format(RampVariable),"RampValues:{}".format(RampValues)," CurrentRampValue: {}".format(V)]
                self.WriteInputFile(ExtraHeader=RampInfo)
                LoadLastSuccess = False
                if LoadLast:
                    LoadLastSuccess=self.Load('last.npy')
                if ThresholdDens:
                    from uedge import com
                    from uedge import bbb
                    for i in range(com.nisp):bbb.ni[(bbb.ni[:,:,i]<bbb.nzbackg[i]),i]=bbb.nzbackg[i]
                    for i in range(com.ngsp):bbb.ng[(bbb.ng[:,:,i]<bbb.ngbackg[i]),i]=bbb.ngbackg[i]
                    for i in range(com.nisp):bbb.nis[(bbb.nis[:,:,i]<bbb.nzbackg[i]),i]=bbb.nzbackg[i]
                    for i in range(com.ngsp):bbb.ngs[(bbb.ng[:,:,i]<bbb.ngbackg[i]),i]=bbb.ngbackg[i]
                if LoadLastSuccess:
                    Status=self.Cont(**kwargs)
                else:
                    Status=self.Cont(dt_tot=0.0,dtreal=dtreal,t_stop=t_stop,**kwargs)
                if Status=='tstop':
                    self.Save('final_state_ramp')
                else:
                    print('Exiting ramp... Need to add a routine to restart after dtkill')
                    return
    
    

    def ThresholdDens(self,factor=1,factorg=1):
        from uedge import com
        from uedge import bbb
        for i in range(com.nisp):bbb.ni[(bbb.ni[:,:,i]<bbb.nzbackg[i]*factor),i]=bbb.nzbackg[i]*factor
        for i in range(com.ngsp):bbb.ng[(bbb.ng[:,:,i]<bbb.ngbackg[i]*factorg),i]=bbb.ngbackg[i]*factorg
        for i in range(com.nisp):bbb.nis[(bbb.nis[:,:,i]<bbb.nzbackg[i])*factor,i]=bbb.nzbackg[i]*factor
        for i in range(com.ngsp):bbb.ngs[(bbb.ng[:,:,i]<bbb.ngbackg[i]*factorg),i]=bbb.ngbackg[i]*factorg
        self.Init()