#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 22:48:20 2020

@author: jguterl
"""
from UEDGEToolBox.DataManager.ExtData import UBoxExtData
from UEDGEToolBox.Launcher import *
from UEDGEToolBox.Plot.Plot2D import UBoxPlot2D
from scipy import interpolate
NewGrid='/home/jguterl/Dropbox/python/Grids/base_174270_2500'
OldGrid='/home/jguterl/Dropbox/python/Grids/gridue_d3d_174270_2500'
OldData='/home/jguterl/Dropbox/python/Grids/svpfb_nf_2019_nc57_ln4.npy'
D=UBoxExtData()
D.InterpolateLoad(OldData,OldGrid,NewGrid,zshift=-1.6)
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