#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 15:00:02 2020

@author: jguterl
"""
from UEDGEToolBox import *
Ubox.CreateProject()
Stop
Restart ipython
UBox.CurrentProject.Copy('D3D_SAS') 
UBox.CurrentProject.Description='simulations of closed divertor'
UBox.CurrentProject.AddDefaultInput()

>cp -r Projects/D3DSAS Projects/D3DSAS2

from UEDGEToolBox.ExtData import UBoxExtData  
from UEDGEToolBox.Projects import UBoxProjects 

/home/jguterl/Dropbox/python/UEDGEInputDir/grid/gridue_reduced

def NewPostProcess(self,Str): 
         print('Do something here with data:',Str) 
         self.Plot()

         