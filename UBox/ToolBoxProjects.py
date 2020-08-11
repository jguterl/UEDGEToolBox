#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 00:23:14 2020

@author: jguterl
"""

import shutil,os,easygui,sys

from ruamel.yaml import YAML, yaml_object
from ToolBoxUtils import *
import platform,inspect
import configparser
import getpass
#from .UEDGEToolBox import LsFolder
import errno
import shutil
import numpy as np
import ruamel.yaml

yaml = YAML()

@yaml_object(yaml)
class Project():
    ListDir=['InputDir','SaveDir','RunDir','GridDir']
    yaml_tag = u'!project'
    def __init__(self,Name,RootPath,Owner,Description,Parent,Create=True):
        self.RootPath=os.path.abspath(RootPath)
        self.Description=Description
        self.Name=Name
        self.Owner=Owner
        self.Parent=Parent
        self.IsCurrent=False
        if Create:
            self.CreateFolder()
            self.CreateReadmeFile()
            print("Project '{}' created with folder '{}' ...".format(self.Name,self.GetPath()))
        else:
            print("Project '{}' created...".format(self.Name))
    # We define manually the import/export functions to save/load a project with yaml so we cn ignore the attribute "Parent" 
    
    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,u'{.RootPath}-{.Description}-{.Name}-{.Owner}-{.IsCurrent}'.format(node, node,node,node,node))

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(*node.value.split('-'))  
    
    def Copy(self,NewName):
        return Project(NewName,self.RootPath,self.Owner,self.Description,self.Parent,Create=False)
        
    def CreateFolder(self):
        os.mkdir(self.GetPath())
        for k in self.__class__.ListDir:
            os.mkdir(self.GetDir(k))
            
    def CreateReadmeFile(self):
         with open(self.GetPath()+'/Readme.txt','w+') as f:
                    f.write('****** UEDGE PROJECT ******\n')
                    f.write('****** Username: {}; email: {}; affiliation: {}\n'.format(self.Owner['UserName'],self.Owner['Email'],self.Owner['Affiliation']))
                    f.write('************************************** \n')
                    f.write('****** Description: \n\n\n\n\n\n\n')
        
    def GetPath(self,Name=None,RootPath=None):
        
        if Name is None:
            Name=self.Name
        if RootPath is None:
            RootPath=self.RootPath


        return os.path.abspath(RootPath+'/'+Name)
        
    def GetDir(self,Dir):
        return os.path.abspath(self.GetPath()+'/'+Dir)
    
    def CopyFolder(self,Path):
        shutil.copytree(self.GetPath(),Path,ignore=None)
        
    def MoveFolder(self,Path):
        shutil.movetree(self.GetPath(),Path)
    
    
    def Rename(self,NewName):
        if self.Parent.ProjectExist(NewName,self.GetPath(NewName)):
            print('Project or folder "{}" already exist. Cannot rename the project ...'.format(self.GetPath(NewName)))
            
        else:
                shutil.move(self.GetPath(),self.GetPath(NewName))
                self.Name=NewName
                self.Register()
                
    
    def Register(self):
        self.Parent.SaveProjects()
    
    def Show(self):
        print("Project     : {}".format(self.Name))
        print("RootPath    : {}".format(self.RootPath))
        print("Description : {}".format(self.Description))
        print("Owner       : {}".format(self.Owner))
    
    def Summary(self):
        return "{:30s} | {:80s} | {:80s}".format(self.Name,self.Description,self.RootPath)
        
    
    
    def Move(self,NewRootPath):
        if self.Parent.ProjectExist(self.Name,self.GetPath(self.Name,NewRootPath)):
            print('Project {} or folder "{}" already exist. Cannot move the project ...'.format(self.GetPath(self.Name,NewRootPath)))
        else:
            shutil.move(self.GetPath(),self.GetPath(self.Name,NewRootPath))
            self.RootPath=NewRootPath
            self.Register()
            
####################################################################################################

class ToolBoxProjects():
    
    def __init__(self):
        
        self.ConfigFile=os.path.join(os.path.expanduser("~"),'.UedgeToolBoxSettings')
        self.Config=None
        
        self.Projects={}
        self.ProjectsFile=None
        self.UserName=''
        self.Email=''
        self.Affiliation=''
        self.PlatForm=GetPlatform()
        self.RootPathProjects=os.path.abspath('.')
        self._CurrentProject=None
        
        self.LoadConfigFile()
        self.LoadConfig()
        self.LoadProjects()
        
    def SetConfigFile(self):
        print('Please select a config file for UEDGE Settings')
        self.ConfigFile=easygui.fileopenbox(title='Select config file for UEDGE Settings',default='.')
        if self.ConfigFile is  None:
            print('No configuration file set for UEDGE Settings... Type "Settings.SetConfigFile" to create or load one')    
            return None
        
    def Show(self):
        print('\n******** UEDGEToolBox Settings ********')
        print('Username:',self.UserName)
        print('Affiliation:',self.Affiliation)
        print('Email:',self.Email)
        print('RootPathProjects:',self.RootPathProjects)
        print('ProjectsFile:',self.ProjectsFile)
        print('*****************************************\n')
    
    def LoadConfigFile(self):
        self.Config=ReadConfigFile(self.ConfigFile)
    
        if self.Config is None:
            if QueryYesNo('Do you want to create a new configuration file for the UEDGEToolPack?'):
                if CreateConfigFile(self.ConfigFile):
                    self.Config=ReadConfigFile(self.ConfigFile)  
        
        if self.Config is None:
            print('No configuration loaded for UEDGEToolBox....')
            print('Run ToolBox.CreateNewConfigFile() if you wish to use UEDGEToolBox.')
            return False
        else:
            print('UEDGEToolPack configuration loaded from {}'.format(self.ConfigFile))
    
    def LoadConfig(self):
    
        self.UserName=self.Config['ToolBox']['UserName']
        self.Email=self.Config['ToolBox']['Email']
        self.Affiliation=self.Config['ToolBox']['Affiliation']
        self.RootPathProjects=self.Config['ToolBox']['RootPathProjects']
        self.SetProjectsFile(self.Config['ToolBox'].get('ProjectsFile'))
        
        
    def SaveConfig(self):
    
        self.Config['ToolBox']['UserName']=self.UserName
        self.Config['ToolBox']['Email']=self.Email
        self.Config['ToolBox']['Affiliation']= self.Affiliation
        self.Config['ToolBox']['RootPathProjects']= self.RootPathProjects
        self.Config['ToolBox']['ProjectsFile']=self.ProjectsFile
        WriteConfigFile(self.Config,self.ConfigFile)
            
        
    def SetProjectsFile(self,FileName=None):
        if FileName is None:
            print('Please select a  file for the UEDGEToolBox projects')
            FileName=easygui.filesavebox(title='Please select a file for the UEDGEToolBox projects',default='.UEDGEToolBoxProjects.yml',filetypes=['*.yml'])
        if FileName is None:
            print('No  file set for the UEDGEToolBox projects...')
            return
        if not os.path.exists(FileName):
            with open(FileName,"w") as f:
                pass
            
        self.ProjectsFile=FileName
        self.Config['ToolBox']['ProjectsFile']=self.ProjectsFile
        self.SaveConfig()
        
    def SetRootPathProjects(self,Folder=None):
        if Folder is None:
            print('Please select a  folder for the UEDGEToolBox projects')
            Folder=easygui.diropenbox(title='Please select a folder for the UEDGEToolBox projects',default='.')
            
        if Folder is None:
            print('No  folder set for the UEDGEToolBox projects...')
            
        else:
            self.RootPathProjects=os.path.abspath(Folder)
            self.Config['ToolBox']['RootPathProjects']=self.RootPathProjects
            self.SaveConfig()    
        
    @property
    def Owner(self):
        return {'UserName':self.UserName,'Email':self.Email,'Affiliation':self.Affiliation}
            
    @property
    def CurrentProject(self):  
         return self._CurrentProject

    @CurrentProject.setter 
    def CurrentProject(self, Name):
         if Name is None:
             self._CurrentProject = None
         if self.Projects.get(Name) is not None:
             self._CurrentProject = self.Projects.get(Name)
             print('Current Project is "{}"'.format(Name))
         else:
             print('Project {} does not exist ...'.format(Name))
        
        
    # This is the default path for the config file of the UEDGEToolPack. 
    
    def GetPathProject(self,Name,RootPath):
        return os.path.abspath(RootPath+'/'+Name)
    
    def DeleteProject(self,Name):
        if self.Projects.get(Name) is not None:
            self.Projects.pop(Name)
            if self.CurrentProject.Name==Name:
                if len(list(self.Projects.keys()))>0:
                    self.SetCurrentProject(list(self.Projects.keys())[-1])
                else:
                    self.SetCurrentProject(None)
            self.SaveProjects()
        else:
            print('Project {} does not exist ...'.format(Name))
    
    def CopyProject(self,OldName,NewName):
        if self.Projects.get(OldName) is not None:
            P=self.Projects[OldName]
        else:
            print('Cannot find project {} ....'.format(OldName))
            return
        
        if self.ProjectExist(NewName,P.GetPath(NewName)):
            print('Project "{}" or folder "{}" already exist. Cannot copy the project ...'.format(NewName,P.GetPath(NewName)))
        else:
                
                self.Projects[NewName]=P.Copy(NewName)
                P.CopyFolder(self.Projects[NewName].GetPath())
                self.SetCurrentProject(NewName)
                self.SaveProjects()    
        
    def _ClearCurrentProject(self):
        for p in self.Projects.keys():
            self.Projects[p].IsCurrent=False
            
    def GetCurrentProject(self):
            self.CurrentProject=None
            for k,v in self.Projects.items():
                if v.IsCurrent:
                    self.CurrentProject=Name
                    self._ClearCurrentProject()
                    self.CurrentProject.IsCurrent=True
                    break
                          
    def SetCurrentProject(self,Name):
        if Name is None:
            self.CurrentProject=None
            return
        if self.Projects.get(Name) is not None:
            self.CurrentProject=Name
            self._ClearCurrentProject()
            self.CurrentProject.IsCurrent=True
            self.SaveProjects()
        else:
            print('Cannot find project {} ....'.format(Name))
    def ShowCurrentProject(self):
        if self.CurrentProject is None:
            print('No current project. To create a new one, type AddProject()')
        else:
            self.CurrentProject.Show()
        
    def ShowProjects(self):
        print(' ************** Projects ****************')
        for i,(k,v) in enumerate(self.Projects.items()):
            if self.CurrentProject is not None and k==self.CurrentProject.Name:
                Str='*'
            else:
                Str=''
            print('[{:2d}{:1s}] {}'.format(i,Str,v.Summary()))
        print(' ****************************************')   
        
    def ProjectExist(self,Name,Path):
        if self.Projects.get(Name) is not None:
            return True
        if os.path.exists(Path):
            return True
        return False
    
    def SaveProjects(self,ProjectsFile=None):
        if ProjectsFile is None:
            ProjectsFile=self.ProjectsFile
            
        with open(ProjectsFile,'w') as f :
            ruamel.yaml.dump(self.Projects,f)
    
    def LoadProjects(self,ProjectsFile=None):
        if ProjectsFile is None:
            ProjectsFile=self.ProjectsFile
        
        if not os.path.exists(ProjectsFile):
            print('Projects file {} does not exist. Cannot load projects. Type SetProjectsFile() to create one.'.format(ProjectsFile))
            return
            
            
        
        with open(ProjectsFile,'r') as f :
            Projects=ruamel.yaml.load(f,Loader=ruamel.yaml.Loader)
            if Projects is not None:
                self.Projects=Projects
                for P in self.Projects.keys():
                    self.Projects[P].Parent=self
        self.GetCurrentProject()            
        print('List of projects loaded from {} ...'.format(ProjectsFile))
        self.ShowCurrentProject()
            
        
        
    
        
        #ProjectsConfig=configparser.ConfigParser()
        
        #ProjectsConfig.update(self.Projects)
        #WriteConfigFile(ProjectsConfig,ProjectsConfigFile)
        
    # def LoadProjects(self):
    #     ProjectsConfig=ReadConfigFile(ProjectsConfigFile)
    #     self.Projects={}
    #     for k,v in ProjectsConfig:
    #         self.Projects[k]=    
    def CreateProject(self,Name,RootPath=None,Description=None,Owner=None):
        
        if Owner is None:
            Owner=self.Owner
        if RootPath is None:
            RootPath=self.RootPathProjects
        if Description is None:
            Description='none'
            
        if self.ProjectExist(Name,self.GetPathProject(Name,RootPath)):
            print('Project {} or folder {} already exist.Cannot create project ...'.format(Name,self.GetPathProject(Name,RootPath)))
            return
        else:
            print('')
            print('Project Name       :',Name)
            print('Project RootPath   :',RootPath)
            print('Project Description:',Description)
            print('Project Owner      :',Owner)
            print('')
            if QueryYesNo('Confirming the creation of the project?'):
               self.Projects[Name]=Project(Name,RootPath,Owner,Description,self)
               self.CurrentProject=Name
               self.SaveProjects()             
    
            else:
                print("Creation of project aborted...")      
            
    def AddProject(self):
        Name=input('Enter the name of the project: ')
        if Name=='':
            print("Name of the project cannot be empty... Aborting project creation... Type 'CreateProject' to create new project")
            return
        
        print('RootPath:{}'.format(os.path.abspath(self.RootPathProjects)))
        if not QueryYesNo('Confirming the roothpath?'):
            RootPathProjects=easygui.diropenbox(title='Select a rootfolder',default=self.RootPathProjects)
            if RootPathProjects is not None:
                self.SetRootPathProjects(RootPathProjects)
                print('RootPathProjects set to {}'.format(self.RootPathProjects))
        RootPath=os.path.abspath(self.RootPathProjects)
        if not os.path.exists(RootPath):
            os.mkdir(RootPath)
            return None
        
        if self.ProjectExist(Name,self.GetPathProject(Name,RootPath)):
            print('Project {} or folder {} already exist.Cannot create project ...'.format(Name,self.GetPathProject(Name,RootPath)))
            return
         
        Description=input('Enter a brief description of the project: ')
        Owner={'UserName':self.UserName,'Affiliation':self.Affiliation,'Email':self.Email}

        self.CreateProject(Name,RootPath,Description,Owner)
        
def GetRootPathProjects(Folder=None):
        if Folder is None:
            print('Please select a  folder for the UEDGEToolBox projects')
            Folder=easygui.diropenbox(title='Please select a folder for the UEDGEToolBox projects',default='.')
        if Folder is None:
            print('No  folder set for the UEDGEToolBox projects... Setting it to current working directory')
            Folder='.'
        return os.path.abspath('.')
    
def GetProjectsFile(FileName=None):
        if FileName is None:
            print('Please select a file for the UEDGEToolBox projects')
            FileName=easygui.filesavebox(title='Please select a configuration file for the UEDGEToolBox projects',default='.UEDGEToolBoxProjects.yml', filetypes=['*.yml'])
        if FileName is None:
            print('No  file set for the UEDGEToolBox projects...')
            return os.path.abspath('.UEDGEToolBoxProjects.yml')
        return os.path.abspath(FileName)
                
 
            
def CreateConfigFile(ConfigFile):
    Settings={}
    UserName=input('Enter the username (press enter for default system username): ')
    if UserName is '':
        UserName=getpass.getuser()
        print(UserName)
    Settings['UserName']=UserName
    Settings['Email']=input('Enter the email address:')
    Settings['Affiliation']=input('Enter the institution:')
    Settings['RootPathProjects']=GetRootPathProjects()
    Settings['ProjectsFile']=GetProjectsFile()
    ShowSettings(Settings)
    
    if QueryYesNo('Are these settings correct?'):
        print('Creation of the settings config file:',ConfigFile)
        try:
            Config = configparser.ConfigParser()
            Config['ToolBox']=Settings
            WriteConfigFile(Config,ConfigFile)
            print('Config file {} created...'.format(ConfigFile))
            return True
        except: 
            print('The config file {} cannot be created ... Exiting ...'.format(ConfigFile)) 
            return False
    else:
        print('The config file {} was not created ... Exiting ...'.format(ConfigFile)) 
        return False
    
    
def GetPlatform():
        PF={}
        AllFunctions = inspect.getmembers(platform, inspect.isfunction)
        for (n,f) in AllFunctions:
            if not n.startswith('_'):
                try: 
                    PF[n]=f()
                except:
                    pass
        return PF

        
def ReadConfigFile(FileName):
    if FileName is None or not os.path.exists(FileName):
        print ('Cannot find the configuration file:"{}"'.format(FileName))
        return None
    config = configparser.ConfigParser()
    try:
        config.read(FileName)
        return config
    except: 
        print('Cannot read the configuration file :' + FileName +'....')
        return None
            
def WriteConfigFile(Config,FileName):
    if FileName is None:
        return None
    try:
        with open(FileName, 'w') as f:
            Config.write(f)
            return True
    except: 
        print('Cannot write the configuration file :' + FileName +'....')
        return None 
 
def ShowSettings(Settings):
    print('\n********** UEDGEToolBox settings**********')
    for k,v in Settings.items():
        print('     {:<20}:{}'.format(k,v))
        
a=ToolBoxProjects()
# a.ProjectsFile='test.yml'
# a.CreateProject('uuuuu')
# a.CreateProject('rrrr')
# a.LoadProjects()
# a.CopyProject('rrrr','zzzz')