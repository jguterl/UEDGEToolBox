#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 16:55:49 2020

@author: jguterl
"""

from UEDGEToolBox.Utils.Misc import QueryYesNo,GetPlatform
import os,easygui,getpass,yaml
from UEDGEToolBox.DataManager.DataSet import UBoxDataSet,GetDefaultDataSet
    
class UBoxSettings(UBoxDataSet):
    """ """
    # def __new__(cls, *args, **kwargs):
    #     if kwargs.get('Parent') is not None:
    #     # Settings=None
    #     # if Settings is not None:
    #          Parent=kwargs.get('Parent')
    #          Parent.__class__ = UBoxSettings
    #          return Parent
    #     else:
    #         return super(UBoxSettings, cls).__new__(cls,*args, **kwargs)
   
    _YAMLTag = u'!setting'
    
    def __init__(self, Load=True,Debug=False,Dic=None,*args, **kwargs):
         super().__init__(*args, **kwargs)
         self._ConfigField=['UserName','Email','Affiliation','ProjectsFile','RootPathProjects','DataSets']
         self._SettingsFile=os.path.join(os.path.expanduser("~"),'.UBoxSettings.yml')
         self._UserName=''
         self._Email=''
         self._Affiliation=''
         self._RootPathProjects=os.path.abspath('.')
         self._ProjectsFile=None
         if Dic is not None:
            self.__fromDict(Dic)
         else:
             self.PlatForm=GetPlatform()
             if Load:
                 self.__LoadSettings()
         
    def __toDict(self):
        Dic={}
        for k in self._ConfigField:
                Dic[k]=getattr(self,'_'+k)
        return Dic
    
    def __fromDict(self,Dic):
        for k,v in Dic.items():
            if hasattr(self,'_'+k):
                setattr(self,'_'+k,v)     

    @staticmethod
    def to_yaml0(dumper, data):
        return dumper.represent_mapping(data._YAMLTag, data.__toDict())

    @staticmethod
    def from_yaml0(loader, node):
        node_map = loader.construct_mapping(node, deep=True) 
        return UBoxSettings(Dic=node_map)
    
    @property
    def UserName(self):  
         return self._UserName

    @UserName.setter 
    def UserName(self, Name):
        self._UserName = Name
        if QueryYesNo('Do you want to save the UBox settings?'):
            self.SaveSettings()
            
    @property
    def Email(self):  
         return self._Email

    @Email.setter 
    def Email(self, Name):
        self._Email = Name
        if QueryYesNo('Do you want to save the UBox settings?'):
            self.SaveSettings()
            
    @property
    def Affiliation(self):  
         return self._Affiliation

    @Affiliation.setter 
    def Affiliation(self, Name):
        self._Affiliation = Name
        if QueryYesNo('Do you want to save the UBox settings?'):
            self.SaveSettings()
            
    @property
    def RootPathProjects(self):  
         return self._RootPathProjects

    @RootPathProjects.setter 
    def RootPathProjects(self, Name):
        if os.path.exists(Name):
            self._RootPathProjects = Name
        else:
            if QueryYesNo('The folder {} does not exist. Do you want to create it?'):
                os.mkdir(self._RootPathProjects)
        if QueryYesNo('Do you want to save the UBox settings?'):
            self.SaveSettings()
            
    @property
    def ProjectsFile(self):  
         return self._ProjectsFile

    @ProjectsFile.setter 
    def ProjectsFile(self, Name):
        self._ProjectsFile = Name
        if QueryYesNo('Do you want to save the UBox settings?'):
            self.SaveSettings()
            
    
    
    def SaveDataSet(self):
        self.SaveSettings()
        
    def __SetConfigFile(self):
        print('Please select a config file for UEDGE Settings')
        self._SettingsFile=easygui.fileopenbox(title='Select config file for UEDGE Settings',default='.')
        if self._SettingsFile is  None:
            print('No configuration file set for UEDGE Settings... Type "Settings.SetConfigFile" to create or load one')    
            return None
        
    def __ParseField(self,Str):
        Dic={}
        if "{" in Str and "}" in Str:
            exec('tmp={}'.format(Str),Dic)
            return Dic['tmp']
        else:
            return Str
        
    def __ReadSettingsFile(self):
         with open(self._SettingsFile,'r') as f:
            Obj=yaml.safe_load(f)
            if Obj is not None:
                for k in self._ConfigField:
                    if hasattr(Obj,'_'+k) and hasattr(self,'_'+k):
                        setattr(self,'_'+k,getattr(Obj,'_'+k))
                return True
            else:
                return False

    def __LoadSettings(self):
        if not os.path.exists(self._SettingsFile) or not self.__ReadSettingsFile():
            if QueryYesNo('Do you want to create a new configuration file for the UBox?'):
                 if not self.__CreateConfigFile():
                     print('No settings file created for UBox...Run UBox.CreateSettingsFile() to create one')
                     return False
        else:
            print('UBox configuration loaded from {}'.format(self._SettingsFile))
            return True
            

    def Print(self,*args,**kwargs):
        """
        Print function allowing to print with the UBox prefix.
        
        Example
        -------
            >>> UBox.Print('Hello')
            [UBox] Hello
        
        """
        print(*args,**kwargs)
  
    
    # def __WriteConfig(self):
    #     UBoxSettings.__WriteConfigFile(self._Config,self._SettingsFile)  
    

    def __GetRootPathProjects(Folder=None):
        if Folder is None:
            print('Please select a folder for UBox projects')
            Folder=easygui.diropenbox(title='Please select a folder for UBox projects',default=os.path.join('.','Projects'))
        if Folder is None:
            print('No  folder set for the UBox projects... Setting it to current working directory')
            Folder=os.path.abspath('.')
        if not os.path.exists(Folder):
            if QueryYesNo('The folder {} does not exist. Do you want to create it?'.format(Folder)):
                os.mkdir(os.path.abspath(Folder))
            else:
                print('No  folder set for the UBox projects... Setting it to current working directory')
                Folder=os.path.abspath('.')
        return Folder
    
                  
    def __CreateConfigFile(self):
        UserName=input('Enter the username (press enter for default system username): ')
        if UserName == '':
            UserName=getpass.getuser()
            print(UserName)
        self._UserName=UserName
        self._Email=input('Enter the email address:')
        self._Affiliation=input('Enter the institution:')
        self._RootPathProjects=UBoxSettings.__GetRootPathProjects()
        self._ProjectsFile=UBoxSettings.__GetProjectsFile()
        self._DataSets=GetDefaultDataSet()
        self.ShowSettings()
        if QueryYesNo('Are these settings correct?'):
            print('Creation of the settings config file:',self._SettingsFile)
            self.SaveSettings()
            return True
        else:
            print('No settings file created ...'.format(self._SettingsFile)) 
            return False
    
    
        
    # @staticmethod        
    # def __WriteConfigFile(Config,FileName):
    #     if FileName is None:
    #         return None
    #     try:
    #         with open(FileName, 'w') as f:
    #             yaml.safe_dump(self,f)
    #             return True
    #     except: 
    #         print('Cannot write the configuration file :' + FileName +'....')
    #         return None 
        
    
        

    @staticmethod 
    def __GetProjectsFile(FileName=None):
            if FileName is None:
                print('Please select a file for the UBox projects')
                FileName=easygui.filesavebox(title='Please select a configuration file for the UBox projects',default='.UBoxProjects.yml', filetypes=['*.yml'])
            if FileName is None:
                print('No  file set for the UBox projects...')
                return None
            
            if not os.path.exists(FileName):
                with open(FileName,"w") as f:
                    pass
            return os.path.abspath(FileName)
        
    
    def SetRootPathProjects(self,Folder=None):
        if Folder is None:
            print('Please select a  folder for the UBox projects')
            Folder=easygui.diropenbox(title='Please select a folder for the UBox projects',default=os.path.join('.','Projects'))
            
        if Folder is None:
            print('No  folder set for the UBox projects...')
            return
        if not os.path.exists(Folder):
            if QueryYesNo('The folder {} does not exist. Do you want to create it?'.format(Folder)):
                os.mkdir(os.path.abspath(Folder))
            else:
                return
        else:
            self._RootPathProjects=os.path.abspath(Folder)
            self.Config['UBox']['RootPathProjects']=self.RootPathProjects
            self.SaveConfig()   
    
    def CreateSettingsFile(self):
        self.__CreateConfigFile()
        
    def SaveSettings(self):
         with open(self._SettingsFile,'w') as f:
            yaml.safe_dump(self,f)
    
    def ShowSettings(self):
        print('******** UBox Settings *******************')
        print('Username:',self.UserName)
        print('Affiliation:',self.Affiliation)
        print('Email:',self.Email)
        print('RootPathProjects:',self.RootPathProjects)
        print('ProjectsFile:',self.ProjectsFile)
        print('*****************************************\n')
        
        
yaml.add_representer(UBoxSettings, UBoxSettings.to_yaml0, Dumper=yaml.SafeDumper)
yaml.add_constructor(UBoxSettings._YAMLTag, UBoxSettings.from_yaml0, Loader=yaml.SafeLoader)  