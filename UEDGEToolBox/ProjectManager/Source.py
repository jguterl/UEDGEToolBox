#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 01:12:10 2020

@author: jguterl
"""
import os
from UEDGEToolBox.ProjectManager.Projects import UBoxSingleProject 
from UEDGEToolBox.Utils.Misc import SetClassArgs  

class UBoxSource():
    Verbose=False
    InputLines=[]
    ShowLines=False
    
    @SetClassArgs
    def __init__(self,Verbose=False):
        pass
    
    @staticmethod
    def GetPath(Project,Folder:str):
        if Project is None:
            return os.path.abs(Folder)
        else:
            if hasattr(Project,'GetDir'):
                return Project.GetDir(Folder)
            else:
                return os.path.abspath(Folder)
                
    def Source(self,FileName=None,CaseName=None,Folder=None,Project=None,EnforceExistence=True,CreateFolder=False):
        if Folder in UBoxSingleProject.ListDir:
            if Project is None:
                if hasattr(self,'CurrentProject'):
                    Project=self.CurrentProject
            
            if Project is not None:
                ObjectDir=self.GetPath(Project,Folder)
            else:
                ObjectDir=os.path.abspath(Folder)
                
            if CaseName is not None:
                ObjectDir=os.path.join(ObjectDir,CaseName)
            
            
        elif Folder is None:
            ObjectDir=None
        else:
            ObjectDir=Folder
        
        if FileName is None:
            return ObjectDir
        
        
        if ObjectDir is not None:
            if not os.path.exists(ObjectDir) and CreateFolder:
                os.mkdir(ObjectDir)
            FilePath=os.path.join(os.path.abspath(os.path.expanduser(ObjectDir)),os.path.expanduser(FileName))
        else:
            FilePath=os.path.abspath(os.path.expanduser(FileName))

        FilePath=os.path.expanduser(FilePath)
        if self.Verbose: print('FilePath:',FilePath)
        if not os.path.exists(FilePath) and EnforceExistence:
            print('Cannot find the file {}'.format(FilePath))
            return None
        else:
            return FilePath
        
        
