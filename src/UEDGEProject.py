#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 21:23:28 2020

@author: jguterl
"""
import configparser,easygui
from datetime import date,datetime
from uedge.UEDGESettings import UEDGESettings,Settings
from uedge.UEDGESettings import *
import os
def ReadConfigFile(FileName):
    if FileName is None:
        return None
    config = configparser.ConfigParser()
    try:
        config.read(FileName)
        return config
    except: 
        print('Cannot read the configuration file for UEDGE projects:' + FileName +'....')
        return None
            
def WriteConfigFile(Config,FileName):
    if FileName is None:
        return None
    try:
        with open(FileName, 'w') as f:
            Config.write(f)
            return True
    except: 
        print('Cannot write the configuration file for UEDGE projects:' + FileName +'....')
        return None
#%%       
class UEDGEProjectsConfigFile():
    def __init__(self,ProjectsConfigFile=None):
        
        self.ProjectsConfigFile=ProjectsConfigFile
        self.ProjectsConfig=self.GetProjectsConfig()
        
        
    def GetProjectsConfig(self):
       print('### Looking for the UEDGE projects configuration file:{}'.format(self.ProjectsConfigFile))
       
       if self.ProjectsConfigFile is None or not os.path.exists(self.ProjectsConfigFile):
           print ('Cannot find the configuration file for UEDGE projects:"{}"'.format(self.ProjectsConfigFile))
           
           if QueryYesNo('Do you want to set a  configuration file for UEDGE projects?'):
               self.CreateProjectsConfigFile()
           else:
               print('No configuration file set for UEDGE projects... Type "SetProjectsConfigFile" to create or load one')
               return None

       print('### Reading UEDGE projects configuration from:{} ...'.format(self.ProjectsConfigFile))
       return ReadConfigFile(self.ProjectsConfigFile)
            
            
    # def SetProjectsConfigFile(self):
    #     print('Please select a config file for UEDGE projects')
    #     self.ProjectsConfigFile=easygui.fileopenbox(title='Select config file for UEDGE projects',default=os.path.expanduser("~"))
    #     if self.ProjectsConfigFile is  None:
    #         print('No configuration file set for UEDGE projects... Type "LoadProjectConfig" to create or load one')    
    #         return None
        
        
    def SetProjectsConfigFile(self):
        
               self.ProjectsConfigFile=easygui.filesavebox(title='Set a config file for UEDGE projects',default=os.path.join(os.path.expanduser("~"),'.UedgeProjects'))
               if self.ProjectsConfigFile is  None:
                   print('No configuration file set for UEDGE projects... Type "SetProjectsConfigFile" to create or load one')
                   return None
               Config=ReadConfigFile(self.ProjectsConfigFile)
               if Config is None:
                   Config = configparser.ConfigParser()
                   Config['CurrentProject']='DEFAULT'
               WriteConfigFile(Config,self.ProjectsConfigFile)
              
#%%
class UEDGEProjects(UEDGEProjectsConfigFile):
    
    def __init__(self,ProjectsConfigFile=None):
        super().__init__(ProjectsConfigFile)
        self.ProjectsConfigFile
        self.ProjectsConfig=self.GetProjectsConfig()
        self.DisplayProjects()
        self.CurrentProject=self.ProjectsConfig[list(self.ProjectsConfig.keys())[0]]
        
        
    def DisplayProjects(self):
        print('\n***** UEDGE Projects available ********')
        if self.ProjectsConfig is not None:
            ListProject=list(self.ProjectsConfig.keys())
            ListProject.remove('DEFAULT')
            
            for i,k in enumerate(ListProject):
                    if self.ProjectsConfig[k].get('Description') is not None:
                        d=self.ProjectsConfig[k].get('Description')
                    else:
                        d=None
                    print(' [{}]: {} || {}'.format(i,k,d))
                
        print('\n***************************************\n')
                  
    #print('')
    #Message='Enter a number to look details of project or press r (return) or q (exit)\n >>>: '
    
    
    def CreateProject(self):
        #Get the config data for UEDGE projects
        
        if self.ProjectsConfig is None:
             print('Cannot get projects config... Aborting the project creation. Type "CreateProject()"') 
             
        Project=self.SetupProject()
        
        if Project is not None:
            self.ProjectsConfig[Project['Name']]=Project
            WriteConfigFile(self.ProjectsConfig,self.ProjectsConfigFile)
            self.ProjectsConfig['CurrentProject']=Project
        
        self.DisplayProjects()    
        
    def LoadProjects():
        self.ProjectConfigFile=GetProjectConfigFile(self.ProjectConfigFile)
   

    def SetupProject(self):
        
        Project={}
        Project['Name']=input('Enter the name of the project: ')
        if Project['Name']=='':
            print("Name of the project cannot be empty... Aborting project creation... Type 'CreateProject' to create new project")
            return None
        if Project['Name'] in list(self.ProjectsConfig.keys()):
            print("A project named {} already exists .... Aborting project creation... Type 'CreateProject' to create new project".format(Project['Name']))
            return None
        if Project['Name']=='CurrentProject':
            print("A project cannot be named 'CurrentProject'  .... Aborting project creation... Type 'CreateProject' to create new project")
            return None
        
        Project['Description']=input('Enter a short description of the project: ')
        print('Select a rootfolder for the project ...')
        RootPath=easygui.diropenbox(title='Select a rootfolder for the project',default='.')
        if RootPath is None:
            print("No folder selected for the project... Aborting project creation... Type 'CreateProject' to create new project")
       
        Project['Path']=os.path.os.path.abspath(RootPath+'/'+Project['Name'])
        # Check that this project does not exist already
        if os.path.exists(Project['Path']):
             print("Project already exist at: {}. Aborting project creation. Type 'CreateProject' to create new project".format(Project['Path']))
             return None
         
        Project['RunDir']=Project['Path']+'/RunDir'
        Project['SaveDir']=Project['Path']+'/SaveDir'
        Project['InputDir']=Project['Path']+'/InputDir'
        Project['GridDir']=Project['Path']+'/GridDir'
        Project['User']=Settings.UserName
        
        today = date.today()
        now = datetime.now()
        Project['Date_Time'] = today.strftime("%d%b%Y")+'_'+now.strftime("%H-%M-%S")
        
        ShowProject(Project)
        
                
        
        if QueryYesNo('Confirming the creation of the project?'):
           for k in ['Path','InputDir','RunDir','GridDir','SaveDir'] :
               try: 
                   os.mkdir(Project[k])
               except:
                   print('Cannot create the folder {}. Aborting creation of the project'.format(Project[k]))
                   return None
           # Creating a readme file: 
               with open(Project[k]+'/Readme.txt','w+') as f:
                   f.write('****** UEDGE PROJECT: {} ******\n\n'.format(Project['Name']))
                   f.write('Description: {} \n\n'.format(Project['Description']))
                   f.write('************************************** \n')
                   for k,v in Project.items():
                       if k!='Name' and k!='Description': 
                           f.write('{}: {} \n'.format(k,v))

        else:
            print("Creation of project aborted... Type 'CreateProject' to create new project")
            return None
        
        
        return Project
           
            
       
def ShowProject(Project):
                print('###### Project settings:')
                for k,v in Project.items():
                    print('     {:<20}:{}'.format(k,v))
    
    
      #%%      
    # def  RegisterProject():
    
    # def SetProjectConfigFile(self):
    #     self.ProjectConfigFile=
    #     return 
    
    # def SwitchProject():
        
    # def ExistingProjects():


    # def DeleteProject():
    # def ChangeGridDir():
    # def ChangeInputDir()
    # def ChangeSaveDir():
    # def CopyProject():
    # def MoveProject():
    # def RenameProject():