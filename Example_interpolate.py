#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 22:48:20 2020

@author: jguterl
"""
from UEDGEToolBox.DataManager.ExtData import UBoxExtData
from UEDGEToolBox.DataManager.DataParser import UBoxDataParser
from UEDGEToolBox.DataManager.Interpolate import UBoxInterpolate

from UEDGEToolBox.Plot.PlotTest import UBoxPlotTest
from UEDGEToolBox.DataManager.Grid import UBoxGrid

#Compare two grids
NewGrid='/home/guterlj/simulations/UEDGE/NFBaseline/GridDir/base_174270_2500_balance'
OldGrid='/home/guterlj/simulations/UEDGE/NFBaseline/GridDir/gridue_d3d_174270_2500'
OldData='/home/guterlj/simulations/UEDGE/d3d_174270_2500/bas/svpfb_nf_2019_nc57_ln4_V784.npy'
UBoxGrid.PlotGrid([OldGrid,NewGrid],edgecolor=['b'],zshift=[-1.6])

OldD=UBoxInterpolate.ExtractData(OldData,None)
NewData=UBoxInterpolate.InterpolateData(OldData,OldGrid,NewGrid,DataType=None,zshift=-1.6)
UBoxPlotTest.ResetPlot()
UBoxPlotTest.AddPlot('bbb.tes',DataType=OldD,Grid=OldGrid)
UBoxPlotTest.Plot('bbb.tes',DataType=NewData,Grid=NewGrid,Refresh=False,Nrow=2)

UBoxInterpolate.SaveData('/home/guterlj/simulations/UEDGE/NFBaseline/svpfb_nf_2019_nc57_ln4_V784_base_174270_2500_balance.npy',NewData)
#%%
OldCoeff='/home/jguterl/Dropbox/python/Grids/transport_coeff.npy'
OldC=UBoxInterpolate.ExtractData(OldCoeff,'UEDGE')
NewCoeff=UBoxInterpolate.InterpolateData(OldCoeff,OldGrid,NewGrid,DataType='UEDGE',zshift=-1.6,ExcludeList=['bbb.difni'])
UBoxInterpolate.SaveData('/home/jguterl/Dropbox/python/Grids/svpfb_nf_2019_nc57_ln4_transportcoeff_newgrid.npy',NewCoeff)

UBoxPlotTest.ResetPlot()
UBoxPlotTest.AddPlot(['bbb.kye_use','bbb.kyi_use'],DataType=OldC,Grid=OldGrid,Verbose=True,zshift=-1.6)
UBoxPlotTest.Plot(['bbb.kye_use','bbb.kyi_use'],DataType=NewCoeff,Grid=NewGrid,Refresh=False,Nrow=2)

#%%
Data=np.loadtxt('/home/jguterl/Dropbox/python/Grids/psi_table_174270_2500.dat')
iy=Data[:,0]
OldPsic=Data[:,-1]
OldPsic=np.insert(OldPsic,-1,1.16)
OldPsic=np.insert(OldPsic,1,0.9904)
NewG=UBoxGrid(NewGrid)
NewG.SetPsin()
NewPsic=NewG.Grid['psinc']
def Interp1DTranspCoeff(OldC,OldPsic,NewPsic,idx=20):
    Dic={}
    for k,v in OldC.items():
        if len(v.shape)==3:
            Data=UBoxDataParser._SplitDataArray(v,2)
            Data=[np.squeeze(D[idx,:]) for D in Data]
            Name=[k+'_'+str(i) for i,d in enumerate(Data)]
        elif len(v.shape)==2:
            Data=[np.squeeze(v[idx,:])]
            Name=[k]
        else:
            Data=[v]
            Name=[k]
        for kk,vv in zip(Name,Data):
            print(kk)
            print(vv)
            Dic[kk]=UBoxInterpolate.Interpolate1D(OldPsic,vv,NewPsic,Verbose=True)
    return Dic

Transp1Dcoeff=Interp1DTranspCoeff(OldC,OldPsic,NewPsic,20)
UBoxInterpolate.SaveData('/home/jguterl/Dropbox/python/Grids/svpfb_nf_2019_nc57_ln4_1Dtransportcoeff_newgrid.npy',Transp1Dcoeff)


        
        
    if dif_use=OldC['bbb.dif_use'][20,1:-1,0]
dif_use=
# NewGrid_=ReadGridFile(NewGrid)
# OldGrid_=ReadGridFile(OldGrid)
# rold=OldGrid_['rm'][:,:,0]
# zold=OldGrid_['zm'][:,:,0]
# rnew=NewGrid_['rm'][:,:,0]
# znew=NewGrid_['zm'][:,:,0]
# Data=UBox.LoadData(OldData)[0]['bbb.tes']
# zshift=-1.6
# zold=zold+zshift
# oldpoints = np.array( [rold.flatten(), zold.flatten()] ).T
# newpoints = np.array( [rnew.flatten(), znew.flatten()] ).T
# values = Data.flatten()
# NewData=interpolate.griddata(oldpoints, values, newpoints, method='linear', rescale=False)
# NewData=NewData.reshape((70,38))

# UBoxPlot2D.PlotData2D(NewGrid_['rm'],NewGrid_['zm'],NewData)
# UBoxPlot2D.PlotData2D(OldGrid_['rm'],OldGrid_['zm'],Data)