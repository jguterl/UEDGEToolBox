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
    def WriteInputFile(self,FileName=None, Folder='SaveDir',ExtraHeader=[]):
        TimeStamp=GetTimeStamp()
        if FileName is None:
            FileName='InputFile'
            FilePath = os.path.join(self.Source(Folder=Folder,EnforceExistence=False), '{}_{}.py'.format(FileName, TimeStamp))
        else:
            FilePath = os.path.splitext(self.Source(FileName,Folder=Folder,EnforceExistence=False))[0]+'_{}.py'.format(TimeStamp)
        if type(ExtraHeader)==str:
            ExtraHeader=[ExtraHeader]
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
                f.write('# TimeStamp: {}\n'.format(TimeStamp))
                for L in ExtraHeader:
                    f.write("# {} \n".format(L))
                for L in self.InputLines:
                    f.write('{}\n'.format(L))
                
        return             
        
        
        