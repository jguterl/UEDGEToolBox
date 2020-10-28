#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 00:57:10 2020

@author: jguterl
"""
import numpy as np
import os
from UEDGEToolBox.Utils.Misc import GetListPackage,ClassInstanceMethod 
from UEDGEToolBox.Utils.Misc import GetTimeStamp
from colorama import  Back, Style
class UBoxInput():
    
    @ClassInstanceMethod     
    def ParseInputFile(self,FilePath:str,ExtraCommand:list=[],ShowLines:bool=False,Vars:dict={},DicG=globals()):
        try: 
            for pkg in GetListPackage():
                exec('from uedge import '+pkg,globals(),locals())
    
            # parsing file
            self.InputFilePath=FilePath
            self.InputFileLines=[]
            f=open(FilePath,'r')
            lines=f.read()
            f.close()
            Lines=lines.splitlines()
            count=1
            Dic=globals()
            DicLocal=locals().update(Vars)
            if Dic.get('UBox') is None:
                Dic['UBox']=self
            for L in Lines:
                if not L.strip().startswith('#'):
                    if ShowLines:
                        print('{} : {}'.format(count,L))
                    exec(L,Dic,locals())
                    self.InputLines.append(L)
                count=count+1
            for L in ExtraCommand:
                if ShowLines:
                        print('ExtraCommand: {}'.format(count,L))
                exec(L,Dic,locals())
                self.InputLines.append(L)
        except Exception as e:
            print('\n {color}>>>>>> Last line executed: {}{reset}\n'.format(L,color=Back.RED,reset=Style.RESET_ALL))
            raise e
        DicG.update(locals())
        
    @ClassInstanceMethod        
    def WriteInputFile(self,FileName=None, Folder='SaveDir'):
        
        if Folder is not None and FileName is not None:
            FilePath = os.path.join(self.Source(Folder=Folder), '{}_{}.py'.format(FileName, GetTimeStamp()))
        elif Folder is None and FileName is not None:
            FilePath = os.path.abspath(FileName)
        else:
            FilePath = None
        User=self.GetTag().get('User')
        Project=self.GetTag().get('Project').get('Name')
        if FilePath is None:
            print('No input file written')
        else:
            print('Writing input file {} ...'.format(FilePath))
            with open(FilePath,'w') as f:
                f.write('# InputFile generated from: {}\n'.format(self.InputFilePath))
                f.write('# User: {}\n'.format(User))
                f.write('# Project: {}\n'.format(Project))
                for L in self.InputFileLines:
                    f.write('{}\n'.format(L))
                
        return             
        
        
        