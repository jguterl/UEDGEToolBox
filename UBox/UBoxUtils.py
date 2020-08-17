#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 10:46:09 2020

@author: jguterl
"""

import inspect,builtins,types,sys,os,uedge,pkgutil
from typing import Callable
def AddUBoxPrefix(orig_func):
    def decorator(*args, **kwargs):
         old = builtins.print
         if not isinstance(old, types.LambdaType):
             builtins.print = lambda x, *args, **kwargs:  old("[UBox]", x, *args, **kwargs)
         try:
             result = orig_func(*args, **kwargs)
         finally:
             if not isinstance(old, types.LambdaType):
                 builtins.print = old
         return result
    return decorator

    
def UBoxPrefix(cls):
    for name, method in inspect.getmembers(cls):
        if (not inspect.ismethod(method) and not inspect.isfunction(method)) or inspect.isbuiltin(method):
            continue
        setattr(cls, name, AddUBoxPrefix(method))
    return cls



def GetListPackage()->list:
    import pkgutil
    import uedge
    ListPkgUEDGE=[]
    package = uedge
    PkgList=list(pkgutil.iter_modules(package.__path__))
    for pkg in PkgList:
        PkgName=pkg.name
        if PkgName.endswith('py'):
            ListPkgUEDGE.append(PkgName[:-2])
   
    return ListPkgUEDGE

def CheckFileExist(FilePath:str)->bool:
    import os
    if os.path.isfile(FilePath):
        out=' '
        while out!='y' and out!='n' and out!='': 
            out=input('The file {} already exists. Do you want to overwrite it? [y]/n'.format(FilePath))
            if out=='y' or out=='':
                return True
            elif out=='n':
                return False            
    else:
        return True        

    ListPkgUEDGE=[]
    package = uedge
    PkgList=list(pkgutil.iter_modules(package.__path__))
    for pkg in PkgList:
        PkgName=pkg.name
        if PkgName.endswith('py'):
            ListPkgUEDGE.append(PkgName[:-2])
   
    return 

def Source(ObjectName:str=None,Folder:str='InputDir',Enforce=True,Verbose:bool=False,CaseName=None,CheckExistence=True,CreateFolder=False):
    """
    

    Args:
        ObjectName (str): DESCRIPTION.
        Folder (str, optional): DESCRIPTION. Defaults to 'InputDir'.
        Enforce (TYPE, optional): DESCRIPTION. Defaults to True.
        Verbose (bool, optional): DESCRIPTION. Defaults to False.
        CaseName (TYPE, optional): DESCRIPTION. Defaults to None.
        CheckExistence (TYPE, optional): DESCRIPTION. Defaults to True.

    Raises:
        IOError: DESCRIPTION.

    Returns:
        ObjectPath (TYPE): DESCRIPTION.

    """
    #if Settings.CurrentProject is None:
     #   raise ValueError("No current project defined. Use SetCurrentProject() to define one")
        
    if Verbose:
        print('# Looking for input file {} in {}'.format(ObjectName,Folder))
    if Folder=='InputDir':
        try:
            ObjectDir=Settings.CurrentProject.GetDir('InputDir')
        except: 
            print('# Settings object for UEDGE not find... Looking for InputDir in current directory')
            ObjectDir='InputDir'        
    elif Folder=='RunDir':
        try:
            ObjectDir=Settings.CurrentProject.GetDir('RunDir')
        except: 
            print('# Settings object for UEDGE not find... Looking for RunDir in current directory')
            ObjectDir='RunDir'
    elif Folder=='SaveDir':
        try:
            ObjectDir=Settings.CurrentProject.GetDir('SaveDir')
        except: 
            print('# Settings object for UEDGE not find... Looking for SaveDir in current directory')
            ObjectDir='SaveDir'
    elif Folder is None:
        ObjectDir=None
    else:    
        ObjectDir=Folder
        
    if ObjectName is None:
        return ObjectDir
    if ObjectDir is None:    
        ObjectPath=os.path.abspath(ObjectName)
    else:
        if CaseName is  not None:
            ObjectDir=os.path.join(ObjectDir,CaseName)
            if not os.path.isdir(ObjectDir) and CreateFolder:
                try:
                    os.mkdir(ObjectDir)
                except OSError:
                    pass
                    #print ("Creation of the directory {} failed".format(ObjectDir))
        ObjectPath=os.path.join(os.path.abspath(ObjectDir),ObjectName)
        
    if CheckExistence and not os.path.exists(ObjectPath):
        if Enforce:
            raise IOError('Cannot find {}:'.format(ObjectPath))
        else:
            print('### Cannot find {}'.format(ObjectPath))
        return None
    else:
        if Verbose:
            print('### Found {}'.format(ObjectPath))
        return ObjectPath 
        
        
def PrintSummary():
    print('******** Summary **********')
    print('* neq  :',bbb.neq)
    print('* nisp :',com.nisp)
    print('* nhsp :',com.nhsp)
    print('* ngsp :',com.ngsp)
    print('* nzspt:',com.nzspt)
    print('* nusp :',com.nusp)
    print('* iigsp:',bbb.iigsp)
    print('***************************')
    
def MakeTrajectories(Npoints,Data):
        for k,v in Data.items():
            Min=v['Min'] 
            Max=v['Max']
            x=np.linspace(0,1,Npoints)
            f=v['f']
            Data[k]=Min+f(x)*(Max-Min)
        return Data

    
def QueryYesNo(question, default="yes"):
        """Ask a yes/no question via input() and return their answer.
    
        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).
    
        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)
    
        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n") 
                
                
               
def CreateGlobalAliases(Object:object,Dic,Include:list=[],Exclude:list=[],Verbose=False):
    """
    Create aliases of methods of a class instance in the global scope.

    Args:
        Object (class instance): Class instance 
        Include (list, optional): List of methods of the class instance Object for which aliases will be created (all methods if =[]). Defaults to [].
        Exclude (list, optional): List of methods of the class instance Object for which aliases will not be created. Defaults to [].

    Returns:
        None.
    """
    
    if len(Include)<1:
        Methods=[(m,getattr(Object, m)) for m in dir(Object) if not m.startswith('__') and m not in Exclude and callable(getattr(Object, m)) and not m.startswith('_')]
    else:
        Methods=[(m,getattr(Object, m)) for m in Include if hasattr(Object,m) and m not in Exclude and callable(getattr(Object, m))]
    if Verbose:
        print([(m,M) for (m,M) in Methods])
    for m,M in Methods:
        Dic[m]=getattr(Object, m)
        
    return

def CopyMethod(Method:Callable):
    """
    

    Args:
        Method (Callable): DESCRIPTION.

    Returns:
        NewMethod (TYPE): DESCRIPTION.

    """
    if callable(Method): 
        NewMethod=types.FunctionType(Method.__code__, Method.__globals__, Method.__name__,
            Method.__defaults__, Method.__closure__)
        NewMethod.__dict__.update(Method.__dict__)
        NewMethod.__doc__=Method.__doc__
        return NewMethod
    else:
        return None


# def GetCaseFolder(CaseName:str):
#     if CaseName=='Default':
#         CaseName=UEDGESimulation.GetTag()
    
#         elif         
# def
#  PathFile(FileName:str,SaveFolder:str='SaveDir',CaseName='Default',Enforce=True,Verbose:bool=False):
    
#         CaseFolder=GetCaseFolder(CaseFolder)
            
#          if os.path.dirname(FileName)!=''
#         if Verbose:
#             print('### Looking for input file {} in {}'.format(FileName,Folder))
#         if Folder=='SaveDir':
#             try:
#                 FileDir=Settings.InputDir
#             except: 
#                 print('Settings object for UEDGE not find... Looking for SaveDir in current directory')
#                 FileDir='SaveDir'
#         elif Folder is None:
#             ObjectDir=None
#         else:
#             ObjectDir=Folder
            
#         if ObjectDir is None:    
#             FilePath=os.path.abspath(FileName)
#         else:
#             FilePath=os.path.join(os.path.abspath(ObjectDir),FileName)
            
#         if not os.path.exists(FilePath):
#             if Enforce:
#                 raise IOError('Cannot find {}:'.format(FiletPath))
#             else:
#                 print('### Cannot find {}'.format(ObjectPath))
#             return None
#         else:
#             if Verbose:
#                 print('### Found {}'.format(ObjectPath))
#             return ObjectPath
