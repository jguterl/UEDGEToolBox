#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 13:57:53 2021

@author: guterlj
"""
import numpy
import numpy as np
from uedge import bbb,com
class UBoxLiveData():
    def __init__(self,*args,**kwargs):
        print('Livedata 12------------------------------')   
        self.livedata = {}
        self.niter_collect =0
        self.iter_collect = 0
        self.iter_data = 0
        self.data_collected = False
        self.livedata_vars = ['ni','ng','te','ti','up']
        self.storage = 10000
        
        
    def init_data(self):
        for k in self.livedata_vars:
            attr = getattr(bbb,k)
            if type(numpy.ndarray):
                self.livedata[k] = np.zeros((self.storage,)+attr.shape)
            else:
                self.livedata[k] = np.zeros((self.storage))
        for k in ['zm']:
           attr = getattr(com,k)
           if type(numpy.ndarray):
               self.livedata[k] = np.zeros(attr.shape)                 
    def livedata_collector(self, force=False):
        self.data_collected = False
        if self.niter_collect>0:
            self.iter_collect += 1
            if self.iter_collect>=self.niter_collect or force:
               print('------- Collecting data ...')
               self.collect_livedata()
               self.iter_collect = 0
               self.data_collected = True
               force=False
            
    
    def collect_livedata(self):
        self.livedata['zm'] = getattr(com,'zm')
        for k in self.livedata_vars:
            self.livedata[k][self.iter_data,:] = getattr(bbb,k)
            
        