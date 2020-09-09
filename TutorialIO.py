#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 00:20:01 2020

@author: jguterl
"""
import numpy as np
from UEDGEToolBox.DataManager.IO import UBoxIO
Data={'UEDGE':{'te':np.zeros((10,6)),'ni':np.zeros((10,6)),'ABC':np.zeros((10,6))},'DataStore':{'MyData':1}}
SelectedData=UBoxIO.SelectData(Data,DataSet='all',DataType='UEDGE')
print(list(SelectedData.keys()))
SelectedData=UBoxIO.SelectData(Data,DataSet='all',DataType='DataStore')
print(list(SelectedData.keys()))

Data2={'te':np.zeros((10,6)),'ni':np.zeros((10,6)),'ABC':np.zeros((10,6))}}
SelectedData2=UBoxIO.SelectData(Data2,DataSet='all',DataType='UEDGE')
print(list(SelectedData2.keys()))


SelectedData3=UBoxIO.SelectData(Data,DataSet=('te',),DataType='UEDGE')
print(list(SelectedData3.keys()))

SelectedData3=UBoxIO.SelectData(Data,DataSet=['regular',('te',)],DataType='UEDGE')
print(list(SelectedData3.keys()))