#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 22:09:43 2020

@author: jguterl
"""
from ToolBoxUtils import *
import sys,os
import easygui
import platform,inspect
import configparser
import getpass
#from .UEDGEToolBox import LsFolder
import errno
import shutil
import numpy as np



        
class ToolBoxSettings(ToolBoxProject):
    
    def __init__(self):
     
         self.ConfigFile=os.path.join(os.path.expanduser("~"),'.UedgeToolBoxSettings')
         self.LoadConfig()
         
         if self.Config is None:
             print('No configuration loaded for UEDGEToolBox....')
             print('Run ToolBox.CreateNewConfigFile() if you wish to use UEDGEToolBox.')
         else:
             print('UEDGEToolPack configuration loaded from {}'.format(self.ConfigFile))
        
         self.GetProjectsConfigFile()
         self.LoadProjects()  
    
    
    
    def CreateNewConfigFile(self):
        CreateConfigFile(self.ConfigFile)
       
   
           
    def SetConfig():
        pass
    
    def GetProjectsConfig(self):

        if QueryYesNo('Do you want to create a new configuration file for UEDGEToolBox projects?'):  
           self.SetProjectsConfigFile()   
        else:
            return None
    
        print('### Reading UEDGE projects configuration from:{} ...'.format(self.ProjectsConfigFile))
        try: 
            self.ProjectConfig=ReadProjectsConfigFile(self.ProjectConfigFile)
        except:
            self.ProjectConfig=None
            
        
      
    
        
    
    def WriteConfig(self):
        WriteConfigFile(self.Config,self.ConfigFile)
        
    
    
    def LoadProjects(self):
        
        
           
        self.GetProjectsConfig()
        
        self.CurrentProject=self.ProjectsConfig['CurrentProject']
    
    
    
     
    
    
    def CheckUEDGEConfig(self):
        
        if not os.path.exists(self.ConfigFileName):
            print ('Cannot find the config file ' + self.ConfigFileName +'....')
            return None
        config = configparser.ConfigParser()
        try:
            config.read(self.ConfigFileName)
            return config
        except: 
            print('Cannot parse the config file:',self.ConfigFileName)
            return None
    
    

      

       





               



# def CdRunDir():
#     os.chdir(Settings.CurrentProject['RunDir'])
#     print('Current directory:',os.getcwd())
 
# def CdSaveDir():
#     os.chdir(Settings.SaveDir)
#     print('Current directory:',os.getcwd())
    
# def CdInputDir():
#     os.chdir(Settings.InputDir)
#     print('Current:',os.getcwd())
    
def LsFolder(Folder,Filter='*',Ext="*.py",LoadMode=False):
    import glob
    if '.' in Ext:
        ListFile = [f for f in glob.glob(os.path.join(Folder,Ext))] +[f for f in glob.glob(os.path.join(Folder,Filter)) if os.path.isdir(f)]
    else:
        ListFile = [f for f in glob.glob(os.path.join(Folder,Ext))]
    Listfile=list(dict.fromkeys(ListFile).keys())
    ListFile.sort(key=str.casefold)
    print('### Content matching "{}" in {}:'.format(Ext,Folder))
    if ListFile is not None:
        for i,F in enumerate(ListFile):
            print(' [{}]: {}'.format(i,os.path.basename(F))) 
    print('')
    Message='Enter a number to look into a folder or file or press r (return) or q (exit)\n >>>: '
    Input=input(Message)
    while Input!='q' and Input!='r':
        if Input.isnumeric() and ListFile is not None and int(Input) in range(len(ListFile)):
            if os.path.isfile(ListFile[int(Input)]):
                print('File:{}'.format(ListFile[int(Input)]))
                if LoadMode:
                    return ListFile[int(Input)]
                Input=input(Message)
            elif os.path.isdir(ListFile[int(Input)]):
                Input=LsFolder(os.path.join(Folder,ListFile[int(Input)]),Filter,Ext,LoadMode)
                if Input=='r':
                   for i,F in enumerate(ListFile):
                       print(' [{}]: {}'.format(i,os.path.basename(F))) 
                   print('') 
                   Input=input(Message) 
                elif LoadMode  and Input!='q':
                    return Input
        else:
            Input=input(Message)
    if Input=='q' and LoadMode:
        return None
    else:
        return Input
        
    
        
def LsInputDir(Folder=None,Ext='*.py'):
    if Folder is None:
        LsFolder(Settings.InputDir,Ext)
    else:
        LsFolder(os.path.join(Settings.InputDir,Folder),Ext)
        
def LsSaveDir(Folder=None,Ext='*'):
    if Folder is None:
        LsFolder(Settings.SaveDir,Ext)
    else:
        LsFolder(os.path.join(Settings.SaveDir,Folder),Ext)
    
def Config():
    Settings.Config() 
    
def InitConfig():
    CreateUEDGESettingsFile()  
# start into the run folder
# CdRunDir()    