#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 10:46:09 2020

@author: jguterl
"""

import io,inspect,builtins,types,sys,os,pkgutil,platform,shutil
from typing import Callable
from datetime import date,datetime
global ShowPreFix
import numpy as np
import fnmatch
try:
    import uedge
except:
    pass
# class AddUBoxPrefix():

#     def __init__(self,PreFix='test'):
#         self.PreFix = PreFix
        
#     def GetDecorator(self,Method):
#         """
#         If there are decorator arguments, __call__() is only called
#         once, as part of the decoration process! You can only give
#         it a single argument, which is the function object.
#         """
#         def DecoratorFunc(*args, **kwargs):
#              old = builtins.print
#              # if hasattr(args[0],'PrintPrefix'):
#              #     if not getattr(args[0],'PrintPrefix'):
#              #         _PreFix=''
#              _PreFix=self.PreFix
            
#              if _PreFix!='' and hasattr(Method,'__self__') and hasattr(Method.__self__,'VerbosePrefix') and getattr(Method.__self__,'VerbosePrefix'):
#                  PreFix='[{}]'.format(_PreFix)
#                  s=io.StringIO()
#                  old('test',file=s)
#                  if PreFix not in s:
#                  #if not isinstance(old, types.LambdaType):
#                      builtins.print = lambda x, *args, **kwargs:  old(PreFix, x, *args, **kwargs)
              
#              try:
#                  result = Method(*args, **kwargs)
#              except Exception as e:
#                  print(repr(e))
#                  raise e
#              finally:
#                  builtins.print = old
#              return result
     
#         return DecoratorFunc
    
# def AddUBoxPrefix(orig_func,_PreFix=''):
#     """
#     Return decorator which add/remove "[UBox]"+Prefix to the built-in function print.
#     """
    
#     def DecoratorFunc(*args, **kwargs):
#           old = builtins.print
#           if hasattr(args[0],'PrintPrefix'):
#               if not getattr(args[0],'PrintPrefix'):
#                   _PreFix=''
        
             
#           if _PreFix!='':
#               PreFix='[{}]'.format(_PreFix)
#               s=io.StringIO()
#               old('test',file=s)
#               if PreFix not in s:
#               #if not isinstance(old, types.LambdaType):
#                   builtins.print = lambda x, *args, **kwargs:  old(PreFix, x, *args, **kwargs)
         
#           try:
#               result = orig_func(*args, **kwargs)
#           except Exception as e:
#               raise e
#           finally:
#               builtins.print = old
#           return result
     
#     return DecoratorFunc

    #  def decorator(*args, **kwargs):
    #      old = builtins.print
    #      if Prefix!='':
    #          _PreFix='[{}]'.format(PreFix)
    #          s=io.StringIO()
    #          print('test',file=s)
             
    #          if not _PreFix in s: 
    #      #isinstance(old, types.LambdaType)
    #      #if not isinstance(old, types.LambdaType) or \:
    #          #_Prefix="[UBox]"
    #          #if not Prefix=='':
    #             # _Prefix+='['+_Prefix+']'   
    #             builtins.print = lambda x, *args, **kwargs:  old(Prefix, x, *args, **kwargs)

    #          if not isinstance(old, types.LambdaType):
    #              builtins.print = old
                 
                 
    #      return orig_func(*args, **kwargs)
    # return decorator

    
def UBoxPreFix():
    
    def DecoratorClass(cls,_PreFix=''):
        for name, method in inspect.getmembers(cls):
              if (inspect.ismethod(method) or inspect.isfunction(method))and not inspect.isbuiltin(method) and not name.startswith('_'):
                #  if cls.__name__ in method.__qualname__.split('.')[0]:
                _PreFix=ProcessPreFix(_PreFix,cls.__qualname__,"UBox")
                print("Adding Prefix '{}' to {} for class '{}'".format(_PreFix,name,cls.__name__))
                setattr(cls, name, AddUBoxPrefix(_PreFix).GetDecorator(method))
        return cls
    
    return DecoratorClass


    
def ProcessPreFix(PreFix,ClsName,Str):
    if PreFix=='':
        return ''.join(ClsName.split(Str))
    else:
        return PreFix
    
def GetListPackage()->list:
    import pkgutil
    ListPkgUEDGE=[]
    try: 
        import uedge
        
        package = uedge
        PkgList=list(pkgutil.iter_modules(package.__path__))
        for pkg in PkgList:
            PkgName=pkg.name
            if PkgName.endswith('py'):
                ListPkgUEDGE.append(PkgName[:-2])
    except:
        pass
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

# def GetPath(Project,Folder:str):
#     if Project is None:
#         return os.path.abs(Folder)
#     else:
#         return Project.GetDir.abspath(Folder)

        
# def Source(ObjectName=None,CaseName=None,Folder='InputDir',Project=None,Enforce=True,CheckExistence=True,CreateFolder=False,Verbose=False):
#     """
    

#     Args:
#         ObjectName (str): DESCRIPTION.
#         Folder (str, optional): DESCRIPTION. Defaults to 'InputDir'.
#         Enforce (TYPE, optional): DESCRIPTION. Defaults to True.
#         Verbose (bool, optional): DESCRIPTION. Defaults to False.
#         CaseName (TYPE, optional): DESCRIPTION. Defaults to None.
#         CheckExistence (TYPE, optional): DESCRIPTION. Defaults to True.

#     Raises:
#         IOError: DESCRIPTION.

#     Returns:
#         ObjectPath (TYPE): DESCRIPTION.

#     """
#     #if Settings.CurrentProject is None:
#      #   raise ValueError("No current project defined. Use SetCurrentProject() to define one")

            
#     if Verbose:
#         print('# Looking for file {} in {}'.format(ObjectName,Folder))
        
#     if Folder=='InputDir' or Folder=='SaverDir' or Folder=='GridDir' or Folder=='RunDir':
#         ObjectDir=GetPath(Project,Folder)
#     elif Folder is None:
#         ObjectDir=None
#     else:    
#         ObjectDir=Folder
    
    
#     if ObjectName is None:
#         return ObjectDir
    
#     if ObjectDir is None:    
#         ObjectPath=os.path.abspath(ObjectName)
#     else:
#         if CaseName is  not None:
#             ObjectDir=os.path.join(ObjectDir,CaseName)
#             if not os.path.isdir(ObjectDir) and CreateFolder:
#                 try:
#                     os.mkdir(ObjectDir)
#                 except OSError:
#                     pass
#                     #print ("Creation of the directory {} failed".format(ObjectDir))
#         ObjectPath=os.path.join(os.path.abspath(ObjectDir),ObjectName)
        
#     if CheckExistence and not os.path.exists(ObjectPath):
#         if Enforce:
#             raise IOError('Cannot find {}:'.format(ObjectPath))
#         else:
#             print('Cannot find {}'.format(ObjectPath))
#         return None
#     else:
#         if Verbose:
#             print('Found {}'.format(ObjectPath))
#         return ObjectPath 
        
def CopyDir(source, dest):
    """Copy a directory structure overwriting existing files"""
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)

        for file in files:
            rel_path = root.replace(source, '').lstrip(os.sep)
            dest_path = os.path.join(dest, rel_path)

            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)

            shutil.copyfile(os.path.join(root, file), os.path.join(dest_path, file))
    
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
                
import itertools
from types import FunctionType


def GetMethods(cls,NoParent=True):
    def listMethods(cls):
        return set(x for x, y in cls.__dict__.items()
                     if isinstance(y, (FunctionType, classmethod, staticmethod)))

    def listParentMethods(cls):
        return set(itertools.chain.from_iterable(
            listMethods(c).union(listParentMethods(c)) for c in cls.__bases__))

    methods = listMethods(cls)
    if  NoParent:
        parentMethods = listParentMethods(cls)
        return set(cls for cls in methods if not (cls in parentMethods))
    else:
        return methods  

              
               
def CreateGlobalAliases(Object:object,Include:list=[],Exclude:list=[],Verbose=False):
    """
    Create aliases of methods of a class instance in the global scope.

    Args:
        Object (class instance): Class instance 
        Include (list, optional): List of methods of the class instance Object for which aliases will be created (all methods if =[]). Defaults to [].
        Exclude (list, optional): List of methods of the class instance Object for which aliases will not be created. Defaults to [].

    Returns:
        None.
    """
    AddedAliases=[]
    if len(Include)<1:
        Methods=[]
        for m in dir(Object):
            # if Verbose: print(m)
            if not isinstance(getattr(Object, m), property) and not m.startswith('__') and m not in Exclude  and callable(getattr(Object, m)) and not m.startswith('_'):
                Methods.append((m,getattr(Object, m)))    
    else:
        Methods=[(m,getattr(Object, m)) for m in Include if hasattr(Object,m) and m not in Exclude and callable(getattr(Object, m))]
    # if Verbose:
    #     print([(m,M) for (m,M) in Methods])
    for m,M in Methods:   
        #Dic[m]=M
        
        exec("builtins.{}=getattr(Object,'{}')".format(m,m))
        AddedAliases.append(m)
    if Verbose: print('Aliases created in builtins:',AddedAliases)
    #return Dic

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

def GetPlatform():
        PF={}
        AllFunctions = inspect.getmembers(platform, inspect.isfunction)
        for (n,f) in AllFunctions:
            if not n.startswith('_') and n!='dist' and n!='linux_distribution':
                try: 
                    PF[n]=f()
                except:
                    pass
        return PF
 
def LsFolder(Folder,Filter='*',Ext="*.py",LoadMode=True)->None or int:
    import glob
    if type(Ext)==str:
        Ext=[Ext]
    ListFile=[]
    for E in Ext:
        if '.' in E:
            ListFile.extend([f for f in glob.glob(os.path.join(Folder,E))] +[f for f in glob.glob(os.path.join(Folder,Filter)) if os.path.isdir(f)])
        else:
            ListFile.extend([f for f in glob.glob(os.path.join(Folder,E))])
    ListFile=list(dict.fromkeys(ListFile))
    ListFile.sort(key=str.casefold)
    print('***** Content matching "{}" in {}:'.format(Ext,Folder))
    if ListFile is not None:
        for i,F in enumerate(ListFile):
            print(' [{}]: {}'.format(i,os.path.basename(F))) 
        print('')
        print('**************************')
    else:
        return None
    if len(ListFile)>0:
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
        return None    
 
def GetContentFolder(Folder,Ext="*.py",Filter='*'):
    import glob
    if type(Ext)==str:
        Ext=[Ext]
    ListFile=[]
    for E in Ext:
        ListFile.extend([f for f in glob.glob(os.path.join(Folder,E))])
    ListFile.extend([f for f in glob.glob(os.path.join(Folder,'*')) if os.path.isdir(f)])
    ListFile=fnmatch.filter(ListFile,Filter)
    ListFile=list(dict.fromkeys(ListFile))
    ListFile.sort(key=str.casefold)
    return ListFile  

    
def BrowserFolder(Folder,Filter='*',Ext="*.py",LoadMode=True)->None or int:
    if Folder is None:
        return None
    ListFile=GetContentFolder(Folder,Ext,Filter)

    Message='Enter a number to look into a folder or return a path to a file or press r (view parent folder) or q (exit)\n >>>: '
    Input=None
    while Input!='q':
        print('***** Content with extension "{}" matching "{}" in {}:'.format(Ext,Filter,Folder))
        if ListFile is not None:
            for i,F in enumerate(ListFile):
                print(' [{}]: {}'.format(i,os.path.basename(F))) 
        print('')
        print('**************************')
        Input=input(Message)
        if Input.isnumeric() and ListFile is not None and int(Input) in range(len(ListFile)):
            if os.path.isfile(ListFile[int(Input)]) and LoadMode:
                print('File:{}'.format(ListFile[int(Input)]))
                if LoadMode:
                    return os.path.abspath(ListFile[int(Input)])
            elif os.path.isdir(ListFile[int(Input)]):
                if LoadMode:
                    return BrowserFolder(os.path.join(Folder,ListFile[int(Input)]),Filter,Ext,LoadMode)
        elif Input=='r':
            return BrowserFolder(os.path.dirname(os.path.abspath(Folder)),Filter,Ext,LoadMode)
        elif Input=='q':
            return None


    
    
def GetTimeStamp()->str:
    """
    Return a time stamp DayMonthYear_HourMinuteSecond.
    
    :return: Time stamp
    :rtype: str

    """ 
    today = date.today()
    now = datetime.now()
    return "{}_{}".format(today.strftime('%d%m%y'),now.strftime("%H%M%S"))


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

def QueryItem(ListItems,Message=None):
    if len(ListItems)>0:
        if Message is None:
            Message='Enter an item number between {} and {} or "r" or "q" to exit\n >>>:'.format(0,len(ListItems)-1)
        Input=input(Message)
        while Input!='q' and Input!='r':
            if Input.isnumeric() and int(Input) in range(len(ListItems)):
                return Input
            elif Input=='r' or Input=='q':
                return None
            else:
                 Input=input(Message)
    else:
        return None
    
def GetClassArgs(cls):
    """Return a dictionary with all the class and parent classes attributes which are not methods or functions."""
    Dic={}
    if cls is not None and hasattr(cls,'__dict__'):
        for k,v in cls.__dict__.items():
            if type(v)!=types.FunctionType and type(v)!=ClassInstanceMethod and not k.startswith('__'):
                Dic[k]=v 
    for C in cls.__bases__:     
        Dic.update(GetClassArgs(C))
    return Dic
def IsMethodClass(v):
    return isinstance(v,types.MethodType) or isinstance(v,staticmethod) or type(v)==types.FunctionType or type(v)==ClassInstanceMethod
    
def SetClassArgs(function):
  """Set all the class and parent classes attributes which are not methods or functions to an class instance (Decorator)."""  
  def wrapper(self,*args,**kwargs):
    Dic=GetClassArgs(self.__class__)
    for k,v in Dic.items():
        if not IsMethodClass(v) and not k.startswith('__'):
            #print('Adding {} to {}'.format(k,self.__class__),v)
            setattr(self,k,v)  
    return function(self,*args,**kwargs)
  return wrapper
    
class ClassInstanceMethod(classmethod):
    def __get__(self, instance, type_):
        descr_get = super().__get__ if instance is None else self.__func__.__get__
        return descr_get(instance, type_)

iota=np.array([np.arange(1,i+1) for i in range(1,300)],dtype=np.ndarray)           
                    
        