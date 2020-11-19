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

   
    


    # def __new__(cls, Parent=None):
    #     if Parent is not None:
    #         Parent.__class__ = UBoxSim
    #         return Pare
    


    
    
    

    





   
        
    
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
# def ThresholdDens():
#     for i in range(com.nisp):bbb.ni[(bbb.ni[:,:,i]<bbb.nzbackg[i]),i]=bbb.nzbackg[i]
#     for i in range(com.ngsp):bbb.ng[(bbb.ng[:,:,i]<bbb.ngbackg[i]),i]=bbb.ngbackg[i]
#     for i in range(com.nisp):bbb.nis[(bbb.nis[:,:,i]<bbb.nzbackg[i]),i]=bbb.nzbackg[i]
#     for i in range(com.ngsp):bbb.ngs[(bbb.ng[:,:,i]<bbb.ngbackg[i]),i]=bbb.ngbackg[i]
def TurnOffPlasma():
    bbb.isnion[0]=0
    bbb.isupon[0]=0
    bbb.istion=0
    bbb.isteon=0

def OnlyCoreOn():
    bbb.isnioffxy=1
    bbb.isngoffxy=1
    bbb.isphioffxy=1
    bbb.istioffxy=1
    bbb.isteoffxy=1
    bbb.isupoffxy=1
    
    bbb.isnioffxy[:,0:com.iysptrx+1,:]=0
    bbb.isupoffxy[:,0:com.iysptrx+1,:]=0
    bbb.isngoffxy[:,0:com.iysptrx+1,:]=0
    bbb.istioffxy[:,0:com.iysptrx+1]=0
    bbb.isteoffxy[:,0:com.iysptrx+1]=0
    bbb.isphioffxy[:,0:com.iysptrx+1]=0
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




    