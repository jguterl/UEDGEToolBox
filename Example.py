#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 23:35:29 2020

@author: jguterl
"""
from UEDGEToolBox.RunSim import UBoxRun
from UEDGEToolBox.Launcher import UBoxLauncher


class NewRun(UBoxRun):
    def NewLoad(self,*args,**kwargs):
        print('>>>>>>>>>>>>> New method <<<<<<<<<<<<<')
        
        self.Load(args,kwargs)
        
        
class UBoxNew(UBoxLauncher,NewRun):

        
    