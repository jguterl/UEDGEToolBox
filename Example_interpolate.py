#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 22:48:20 2020

@author: jguterl
"""
from UEDGEToolBox.DataManager.ExtData import UBoxExtData
from UEDGEToolBox.DataManager.Interpolate import UBoxInterpolate

from UEDGEToolBox.Plot.PlotTest import UBoxPlotTest
from UEDGEToolBox.DataManager.Grid import UBoxGrid



#Compare two grids
NewGrid='/home/jguterl/Dropbox/python/Grids/base_174270_2500'
OldGrid='/home/jguterl/Dropbox/python/Grids/gridue_d3d_174270_2500'
OldData='/home/jguterl/Dropbox/python/Grids/svpfb_nf_2019_nc57_ln4.npy'
UBoxGrid.PlotGrid([OldGrid,NewGrid],edgecolor=['b'],zshift=[-1.6])

OldD=UBoxInterpolate.ExtractData(OldData,'UEDGE')
NewData=UBoxInterpolate.InterpolateData(OldData,OldGrid,NewGrid,DataType=None,zshift=-1.6)
UBoxPlotTest.Plot('bbb.nis',DataType=[NewData,OldData],Grid=NewGrid)
UBoxInterpolate.SaveData('svpfb_nf_2019_nc57_ln4_newgrid.npy',NewData)



OldCoeff='/home/jguterl/Dropbox/python/Grids/transport_coeff.npy'
NewCoeff=UBoxInterpolate.InterpolateData(OldCoeff,OldGrid,NewGrid,DataType='UEDGE',zshift=-1.6,ExcludeList=['bbb.difni'])
UBoxInterpolate.SaveData('svpfb_nf_2019_nc57_ln4_transportcoeff_newgrid.npy',NewCoeff)
UBoxPlotTest.ResetPlot()

UBoxPlotTest.Plot('bbb.kye_use',DataType=OldC,Grid=OldGrid)
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