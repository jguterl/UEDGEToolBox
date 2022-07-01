#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 00:23:14 2020

@author: jguterl

"""
from UEDGEToolBox.Utils.Misc import UBoxPreFix,QueryYesNo,QueryItem,LsFolder,CopyDir
from UEDGEToolBox.ProjectManager.Settings import UBoxSettings
from UEDGEToolBox.DataManager.Grid import UBoxGrid


import os,easygui,shutil,yaml,glob
#import numpy as np
class UBoxFileHelper():
    def __init__(self):
        self.DefaultInputFolder='/home/jguterl/DefaultInputFolder'
    
    def AddDefaultInput(self):
        #self.__CopyFolderContent(self.DefaultInputFolder,self.GetDir('InputDir'))
        CopyDir(self.DefaultInputFolder,self.GetDir('InputDir'))
        print('Input files copied from {} to {} ...'.format(os.path.abspath(self.DefaultInputFolder),os.path.abspath(self.GetDir('InputDir'))))
        
    def AddGridFile(self,GridFileName,ViewGrid=False):
        GridFileName=os.path.abspath(os.path.expanduser(GridFileName))
        if ViewGrid:
            UBoxGrid(GridFileName).PlotGrid()
            if not QueryYesNo('Add this grid file to {}'.format(self.GetDir('GridDir'))):
                return
        self.__CopyFile(GridFileName,self.GetDir('GridDir'))
        print('Grid file {} copied into {} ...'.format(os.path.abspath(GridFileName),os.path.abspath(self.GetDir('GridDir'))))
            
            
    @staticmethod
    def __CopyFolderContent(SrcFolder,DestFolder):
        SrcFiles = os.listdir(SrcFolder)
        for F in SrcFiles:
            FN = os.path.join(SrcFolder,F)
            if os.path.isfile(FN):
                shutil.copy(FN, DestFolder)
        
    def GetDir(self,*args,**kwargs):
        pass
    
    @staticmethod
    def __CopyFile(File,DestFolder):
        shutil.copy(File, DestFolder)
        
        
class UBoxSingleProject(UBoxFileHelper):
    """UBox project."""
    
    ListDir=['InputDir','SaveDir','RunDir','GridDir']
    Properties=['Name','RootPath','Owner','IsCurrent','Description']
    _YAMLTag = u'!project'
    
    def __init__(self,Name='',RootPath=None,Owner={},Description='',IsCurrent=False,Parent=None,Create=False,Dic=None):
        super().__init__()
        if RootPath is not None:
            self.RootPath=os.path.abspath(RootPath)
        else:
            self.RootPath=None
        if Description is None:
            self.Description=''
        else:    
            self.Description=Description
        self.Name=Name
        self.Owner=Owner
        self.Parent=Parent
        self.IsCurrent=IsCurrent
        self.Verbose=False
        if Dic is not None:
            self.__fromDict(Dic)
        if Create:
            self.__CreateFolder()
            self.__CreateReadmeFile()
            print("Project '{}' created in folder={} ...".format(self.Name,self.GetPath()))
        else:
            if self.Verbose: print("Project '{}' loaded...".format(self.Name))
                
    def __toDict(self):
        Dic={}
        for k in self.__class__.Properties:
                Dic[k]=getattr(self,k)
        return Dic
    
    def toDict(self):
        return self.__toDict()
    
    def __fromDict(self,Dic):
        for k,v in Dic.items():
            if hasattr(self,k):
                setattr(self,k,v)
        
    def __repr__(self):
        return 'Project {}:{}'.format(self.Name,self.RootPath)
        
    @staticmethod
    def to_yaml(dumper, data):
        return dumper.represent_mapping(data._YAMLTag, data.__toDict())

    @staticmethod
    def from_yaml(loader, node):
        node_map = loader.construct_mapping(node, deep=True) 
        return UBoxSingleProject(Dic=node_map)
        
    # We define manually the import/export functions to save/load a project with yaml so we cn ignore the attribute "Parent" 
    @property 
    def InputDir(self):
        return self.GetDir('InputDir')
    
    @property 
    def RunDir(self):
        return self.GetDir('RunDir')
    
    @property 
    def SaveDir(self):
        return self.GetDir('SaveDir')
    
    @property 
    def GridDir(self):
        return self.GetDir('GridDir')
    

    
    def __Copy(self,NewName):
        return UBoxSingleProject(Name=NewName,RootPath=self.RootPath,Owner=self.Owner,Description=self.Description,Parent=self.Parent,Create=False)
        
    def __CreateFolder(self):
        os.mkdir(self.GetPath())
        for k in self.__class__.ListDir:
            os.mkdir(self.GetDir(k))
            
    def __CreateReadmeFile(self):
         with open(self.GetPath()+'/Readme.txt','w+') as f:
                    f.write('****** UEDGE PROJECT ******\n')
                    f.write('****** Username: {}; email: {}; affiliation: {}\n'.format(self.Owner['UserName'],self.Owner['Email'],self.Owner['Affiliation']))
                    f.write('************************************** \n')
                    f.write('****** Description: \n\n\n\n\n\n\n')
    
    def Copy(self,NewName:str)->None:
        """
        Copy the project into a new project. 
        
        :param NewName: Name of the new project
        :type NewName: Str
        :return: None
        :rtype: 

        """
        
 
        if self.Parent.ProjectExist(NewName,self.GetPath(NewName)):
            print('Project "{}" or folder "{}" already exist. Cannot copy the project ...'.format(NewName,self.GetPath(NewName)))
        else:
                
                self.Parent.Projects[NewName]=self.__Copy(NewName)
                self.__CopyFolder(self.Parent.Projects[NewName].GetPath())
                self.Parent.SetCurrentProject(NewName)
                self.Parent.SaveProjects()    
                
    def GetPath(self,Name:str=None,RootPath:str=None)->str:
        """
        Return the path of the project folder.
        
        If no project name or rootpath is provided, name and rootpath are the ones from the instance.
        
        :param Name: project name, defaults to None
        :type Name: str, optional
        :param RootPath: project rootpath, defaults to None
        :type RootPath: str, optional
        :return: path of the project folder.
        :rtype: str

        """   
        if Name is None:
            Name=self.Name
        if RootPath is None:
            RootPath=self.RootPath


        return os.path.abspath(os.path.join(RootPath,Name))
        
    def GetDir(self,Dir:str)->str:
        """
        Return path toward directory. Example: CurrentProject.GetDir('InputDir') returns /path/to/projects/InputDir.
        
        :param Dir: InputDir or GridDir or SaveDir or RunDir
        :type Dir: str
        :return: Path toward directory
        :rtype: str

        """ 
        if Dir=="RootDir":
            return os.path.abspath(self.GetPath())
        else:
            return os.path.abspath(self.GetPath()+'/'+Dir)
    
    def __CopyFolder(self,Path):
        shutil.copytree(self.GetPath(),Path,ignore=None)
        
    def __MoveFolder(self,Path):
        shutil.movetree(self.GetPath(),Path)
    
    
    def Rename(self,NewName):
        if self.Parent.ProjectExist(NewName,self.GetPath(NewName)):
            print('Project or folder "{}" already exist. Cannot rename the project ...'.format(self.GetPath(NewName)))
            
        else:
                shutil.move(self.GetPath(),self.GetPath(NewName))
                self.Name=NewName
                self.Register()
                
    
    def __Register(self):
        
        self.Parent.SaveProjects()
    
    def Show(self)->None:
        """
        Display the properties of the project.
        
        :return: None
        :rtype: None

        """
        print("Project     : {}".format(self.Name))
        print("RootPath    : {}".format(self.RootPath))
        print("Description : {}".format(self.Description))
        print("Owner       : {}".format(self.Owner))
    
    def Summary(self):
            
        return "{:30} | {:40} | {:40}".format(self.Name,self.Description,self.RootPath)
        
    
    
    def __Move(self,NewRootPath):
        if self.Parent.ProjectExist(self.Name,self.GetPath(self.Name,NewRootPath)):
            print('Project {} or folder "{}" already exist. Cannot move the project ...'.format(self.GetPath(self.Name,NewRootPath)))
        else:
            shutil.move(self.GetPath(),self.GetPath(self.Name,NewRootPath))
            self.RootPath=NewRootPath
            self.__Register()
            
            
yaml.add_representer(UBoxSingleProject, UBoxSingleProject.to_yaml, Dumper=yaml.SafeDumper)
yaml.add_constructor(UBoxSingleProject._YAMLTag, UBoxSingleProject.from_yaml, Loader=yaml.SafeLoader)            
        
####################################################################################################

        
#@UBoxPreFix()
class UBoxProjects(UBoxSettings):
    """Manager for UBox projects."""
    
    # def __new__(cls, *args, **kwargs):
    #     if kwargs.get('Parent') is not None:
    #     # Settings=None
    #     # if Settings is not None:
    #          Parent=kwargs.get('Parent')
    #          Parent.__class__ = UBoxProjects
    #          return Parent
    #     else:
    #         return super(UBoxProjects, cls).__new__(cls,*args, **kwargs)
        
    def __init__(self,Parent=None,Verbose=False,LoadParent=True,*args, **kwargs):
        super().__init__(Load=LoadParent,*args, **kwargs)
        self.Verbose=Verbose
        self.Projects={}
        self._CurrentProject=None
        self.LoadProjects()
        
        

    @property
    def Owner(self):
        return {'UserName':self.UserName,'Email':self.Email,'Affiliation':self.Affiliation}
 
    def CurrentProjectGetter(self):
         return self.CurrentProject
     
    @property
    def CurrentProject(self):
         if self._CurrentProject is not None:
            return self._CurrentProject

    @CurrentProject.setter 
    def CurrentProject(self, Name):
         if Name is not None:
            if self.Projects.get(Name) is not None:
                self._CurrentProject = self.Projects.get(Name)
                self.__ClearCurrentProject()
                self.CurrentProject.IsCurrent=True
                self.SaveProjects()
                print('Current Project set to "{}"'.format(Name))
            else:
                print('Project named {} does not exist ...'.format(Name))
        
    
    def __GetPathProject(self,Name,RootPath):
        return os.path.abspath(RootPath+'/'+Name)
    
    def __CreateProject(self,Name,RootPath=None,Description=None,Owner=None, force=False):
        
        if Owner is None:
            Owner=self.Owner
        if RootPath is None:
            RootPath=self.RootPathProjects
        if Description is None:
            Description='none'
            
        if self.ProjectExist(Name,self.__GetPathProject(Name,RootPath)):
            print('Project {} or folder {} already exist.Cannot create project ...'.format(Name,self.__GetPathProject(Name,RootPath)))
            return
        else:
            print('')
            print('Project Name       :',Name)
            print('Project RootPath   :',RootPath)
            print('Project Description:',Description)
            print('Project Owner      :',Owner)
            print('')
            if force or QueryYesNo('Confirming the creation of the project?'):
               self.Projects[Name]=UBoxSingleProject(Name,RootPath,Owner,Description,False,self,Create=True)
               self.CurrentProject=Name
               self.SaveProjects()             
    
            else:
                print("Creation of project aborted...")
                
    def __AddProject(self,Name,RootPath=None,Description=None,Owner=None):
        
        if Name in list(self.Projects.keys()):
            if not QueryYesNo('Project {} already exists in UBox. Overwrite it?'.format(Name)):
                return
            
        self.Projects[Name]=UBoxSingleProject(Name=Name,RootPath=RootPath,Owner=Owner,Description=Description,Parent=self)
        self.CurrentProject=Name
        self.SaveProjects() 
        
        
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
    
    
    def CopyProject(self,OldName:str,NewName:str)->None:
        """
        Copy Project 'OldName' into a new project 'NewName'
        
        :param OldName: Name of the old project
        :type OldName: str
        :param NewName: Name of the new project
        :type NewName: str
        :return: None 
        :rtype: None

        """
        
        
        
        if self.Projects.get(OldName) is not None:
            P=self.Projects[OldName]
        else:
            print('Cannot find project {} ....'.format(OldName))
            return None
        
        P.Copy(NewName)  
        
    def __ClearCurrentProject(self):
        for p in self.Projects.keys():
            self.Projects[p].IsCurrent=False
            
    def __SetCurrentProject(self):
            self.CurrentProject=None
            for k,v in self.Projects.items():
                if v.IsCurrent:
                    self.CurrentProject=k
                    self.__ClearCurrentProject()
                    self.CurrentProject.IsCurrent=True
                    break
                
    def ProjectExist(self,Name:str,Path:str)->bool:
        """
        Check whether a project already exist.Return True if the project exists.
        
        :param Name: Name of the project
        :type Name: str
        :param Path: Path of the project
        :type Path: str
        :return: DESCRIPTION
        :rtype: bool

        """
          
        if self.Projects.get(Name) is not None:
            return True
        if os.path.exists(Path):
            return True
        return False
    
    
            

                 
    def SetCurrentProject(self,Name:str=None)->None:
        """
        Set current project.
        :param Name: Name of the project
        :type Name: str
        :return: None
        :rtype: None

        """
        
        if Name is not None:
            if self.Projects.get(Name) is not None:
                self.CurrentProject=Name
                self.__ClearCurrentProject()
                self.CurrentProject.IsCurrent=True
                self.SaveProjects()
            else:
                print('Cannot find project {} ....'.format(Name))    
        else:
                ListItems=self.ShowProjects(Return=True)
                UserInput=QueryItem(ListItems)
                if UserInput is not None:
                    ProjectName=ListItems[int(UserInput)]
                    self.SetCurrentProject(ProjectName)
                    
                
            
    
    def ShowCurrentProject(self)->None:
        """
        Show the current project.
        
        :return: None
        :rtype: None

        """
        if self.CurrentProject is None:
            print('No current project. To create a new one, type CreateProject()')
        else:
            self.CurrentProject.Show()
        
    def ShowProjects(self,Return=False)->None:
        """
        Show list of project. The current project is indicated by *.
        
        :return: None
        :rtype: None

        """
        print(' ************** Projects ****************')
        for i,(k,v) in enumerate(self.Projects.items()):
            if self.CurrentProject is not None and k==self.CurrentProject.Name:
                Str='*'
            else:
                Str=''
            print('[{:2d}{:1s}] {}'.format(i,Str,v.Summary()))
        print(' ****************************************') 
        if Return:
            return list(self.Projects.keys())
        
    def ScanFolder(self,Folder:str):
        """
        Scan a folder to search and add existing projects.
        
        :param Folder: Name of the folder to scan
        :type Folder: str
        :return: DESCRIPTION
        :rtype: TYPE

        """
        if not os.path.exists(Folder):
            print('Cannot find the folder {} ...'.format(Folder))
            return
        
        ListSubFolder=glob.glob(os.path.join(Folder,'*'))
        
        for S in ListSubFolder:
            #print(S)
            ListSubSubFolder=glob.glob(os.path.join(S,'*'))
            LSS=[]
            for SS in ListSubSubFolder:
                 LSS.append(os.path.basename(SS))
            #print(LSS)
            #print([L in LSS for L in Project.ListDir])
            if all([L in LSS for L in UBoxSingleProject.ListDir]):
                print('Found project {} in {} ... Loading it in UBox'.format(os.path.basename(S),os.path.dirname(S)))
                self.__AddProject(os.path.basename(S),RootPath=os.path.dirname(S),Description=None,Owner=self.Owner)
                
        
    
    def SaveProjects(self,ProjectsFile:str=None)->None:
        """
        Save projects in the the given project yml file. If no file is given, save in UBox.ProjectsFile.
        
        :param ProjectsFile: File where projects will be saved, defaults to None
        :type ProjectsFile: str, optional
        :return: None
        :rtype: None

        """  
        if ProjectsFile is None:
            ProjectsFile=self.ProjectsFile 
        if ProjectsFile is not None:    
            with open(ProjectsFile,'w') as f :
                yaml.safe_dump(self.Projects,f)
    
    def LoadProjects(self,ProjectsFile:str=None)->None:
        """
        Load projects from a project yml file. If no file is given, save in UBox.ProjectsFile.
        
        :param ProjectsFile: File where projects will be saved, defaults to None
        :type ProjectsFile: str, optional
        :return: None
        :rtype: None

        """
        if ProjectsFile is None:
            ProjectsFile=self.ProjectsFile
            
        if self.Verbose:
                    print('Loading projects from ', self.ProjectsFile)
                    
        if ProjectsFile is None or not os.path.exists(ProjectsFile):
            print('Projects file {} does not exist. Cannot load projects. Type SetProjectsFile() to create one.'.format(ProjectsFile))
            return
        
        else:
                
            with open(ProjectsFile,'r') as f:
                Projects=yaml.safe_load(f)
                
            if self.Verbose:
                    print('Loaded Projects:',Projects)
                    
            if Projects is not None:
                self.Projects=Projects
                for P in self.Projects.keys():
                    self.Projects[P].Parent=self 
                if self.Verbose:
                    print('Loaded Projects:',self.Projects)    
                self.__SetCurrentProject() 
                #self.ShowProjects()
                N=len(list(self.Projects.keys()))
            else:
                N=0
                
                
            print('{} projects loaded from {} ...'.format(N,ProjectsFile))
            #self.ShowCurrentProject()
            
 
         
            
    def CreateProject(self, Name=None, force=False)->None:
        """Create a new project."""
        if self.ProjectsFile is None:
            print("Cannot create a new project. A project file must be first set with SetProjectsFile()")
            return
        if Name is None:
            Name=input('Enter the name of the project: ')
            if Name=='':
                print("Name of the project cannot be empty... Aborting project creation... Type 'CreateProject' to create new project")
                return
        print('RootPath:{}'.format(os.path.abspath(self.RootPathProjects)))
        if not force:
            if not QueryYesNo('Confirming the roothpath?'):
                RootPathProjects=easygui.diropenbox(title='Select a rootfolder',default=self.RootPathProjects)
                if RootPathProjects is not None:
                    self.SetRootPathProjects(RootPathProjects)
                    print('RootPathProjects set to {}'.format(self.RootPathProjects))
        RootPath=os.path.abspath(self.RootPathProjects)
        if not os.path.exists(RootPath):
            os.mkdir(RootPath)
            return None
        
        if self.ProjectExist(Name,self.__GetPathProject(Name,RootPath)):
            print('Project {} or folder {} already exist.Cannot create project ...'.format(Name,self.__GetPathProject(Name,RootPath)))
            return
        if not force: 
            Description=input('Enter a brief description of the project: ')
        else:
            Description = ""
        Owner={'UserName':self.UserName,'Affiliation':self.Affiliation,'Email':self.Email}

        self.__CreateProject(Name,RootPath,Description,Owner, force)
        
    def SetProjectsFile(self,FileName:str=None)->None:
        """
        Set the project yml file in UBox and reload projects from this file.
        :param FileName: new project yml file, defaults to None
        :type FileName: str, optional
        :return: None
        :rtype: None

        """
        
        if FileName is None:
            print('Please select a  file for the UBox projects')
            FileName=easygui.filesavebox(title='Please select a file for the UBox projects',default='.UBoxProjects.yml',filetypes=['*.yml'])
        if FileName is None:
            print('No  file set for the UBox projects...')
            return
        if not os.path.exists(FileName):
                with open(FileName,"w") as f:
                    pass
   
        self.ProjectsFile=FileName 
        self.LoadProjects()
        
    def LsInputDir(self,Folder=None,Ext='*.py'):
        if Folder is None:
            Folder=''    
        LsFolder(os.path.join(self.CurrentProject.InputDir,Folder),Ext)
        
    def LsSaveDir(self,Folder=None,Ext='*'):
        if hasattr(self,'_AvailableFormat'):
            Ext=['*'+v.Ext for v in getattr(self,'_AvailableFormat').values()]
        if Folder is None:
            Folder=''    
        LsFolder(os.path.join(self.CurrentProject.SaveDir,Folder),Ext=Ext)

    def LsGridDir(self,Folder=None,Ext='*'):
        if Folder is None:
            Folder=''    
        LsFolder(os.path.join(self.CurrentProject.GridDir,Folder),Ext=Ext)
    
         

    
