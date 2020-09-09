#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 00:57:10 2020

@author: jguterl
"""
import numpy as np
from UEDGEToolBox.Utils.Misc import GetListPackage,ClassInstanceMethod 
class UBoxInput():
    
    @ClassInstanceMethod     
    def ParseInputFile(self,FilePath:str,OverWrite:dict={},ShowLines:bool=False):
        
        for pkg in GetListPackage():
            exec('from uedge import '+pkg,globals(),locals())

        # parsing file
        f=open(FilePath,'r')
        lines=f.read()
        f.close()
        Lines=lines.splitlines()
        count=1
        for L in Lines:
            if not L.strip().startswith('#'):
                if ShowLines:
                    print('{} : {}'.format(count,L))
                
                exec(L,globals(),locals())
                globals().update(OverWrite)
                if hasattr(self,'InputLines'):
                    self.InputLines.append(L)
            count=count+1