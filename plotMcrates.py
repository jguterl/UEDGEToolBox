#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 15:11:13 2020

@author: jguterl
"""
import numpy as np
import matplotlib.pyplot as plt
def GetMcRates(ne:float or np.ndarray,Te:float or np.ndarray,z:int=6,nz:int=6,zn:int=6,m:float=2,Ti_Te=1,**kwargs):
    from uedge import bbb
    if type(ne)!=np.ndarray:
        if type(ne)!=list:
            ne=[ne]
        ne=np.array(ne)
    if type(Te)!=np.ndarray:
        if type(Te)!=list:
            Te=[Te]
        Te=np.array(Te)    
        
    iz=np.zeros((ne.shape[0],Te.shape[0]))
    rec=np.zeros((ne.shape[0],Te.shape[0]))
    cxr=np.zeros((ne.shape[0],Te.shape[0]))
    for i,ne_ in enumerate(ne):
        for j,Te_ in enumerate(Te):
            Ei_=Te_*Ti_Te*bbb.mp/m
            iz[i,j]=bbb.mcrates_kionz(ne_,Te_*bbb.ev,Ei_*bbb.ev,z,nz,zn)
            rec[i,j]=bbb.mcrates_krecz(ne_,Te_*bbb.ev,Ei_*bbb.ev,z,nz,zn)
            cxr[i,j]=bbb.mcrates_kcxrz(ne_,Te_*bbb.ev,Ei_*bbb.ev,z,nz,zn)
    return (iz,rec,cxr)


def PlotMcRates(ne=10.0**np.arange(8,22,1),Te=np.logspace(-2,2,50),z=6,nz=6,zn=6,**kwargs):
    (iz,rec,cxr)=GetMcRates(ne,Te,z,nz,zn)
    fig,axes=plt.subplots(1,3)
    axes=axes.flatten()
    for i,ne_ in enumerate(ne):
        axes[0].loglog(Te,iz[i,:],label=ne_)
        axes[1].loglog(Te,rec[i,:],label=ne_)
        axes[2].loglog(Te,cxr[i,:],label=ne_)
    plt.legend()
    
    