#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 22:33:45 2020

@author: jguterl
"""
import glob, os
from fparser import one
from fparser.api import parse
from uedge import *
from UEDGEToolBox.ParserFortran.FortranTreeExplorer import UBoxFortranTreeExplorer 
from UEDGEToolBox.Utils.Doc import UBoxDoc 
        
class UBoxParserFortran(UBoxFortranTreeExplorer):
    def __init__(self,Verbose=False):
        super().__init__()
        self.Verbose=Verbose
        
    def GetFortranTree(self,UEDGESourcePath,ExcludeList=[]):
        self.UEDGESourcePath=os.path.abspath(UEDGESourcePath)
        print('Parsing UEDGE Fortran source files in the folder:{}'.format(self.UEDGESourcePath))
        print('Excluding files:{}'.format(ExcludeList))
        self.ListTree={}
        InitDir=os.getcwd()
        self.Doc=UBoxDoc()
        for pkg in self.Doc.ListPkg:
            os.chdir(os.path.join(self.UEDGESourcePath,pkg))
            for file in glob.glob("*.F"):
                if file not in ExcludeList:
                    print('Processing {} ...'.format(file))
                    name=os.path.splitext(file)[0]
                    print(os.path.join(os.getcwd(), file))
                    tree=parse(os.path.join(os.getcwd(), file), isfree=False)
                    DicG=globals()
                    DicG['tree']=tree
                    exec(name+'=tree',DicG,self.ListTree) 
                else:
                    print('Skipping {} ...'.format(file))
        os.chdir(InitDir)
    
    
    def AnalyzeTree(self,IgnoreCall):
        self.IgnoreCall=IgnoreCall
        self.DicFortranObject={}
        for File,tree in self.ListTree.items():
            DicFortranObject={}
            for FortranContent in tree.content:
                FortranObject=self.AnalyzeFortranContent(FortranContent,self.IgnoreCall)
                if FortranObject is not None:
                    DicFortranObject[FortranContent.name]=FortranObject
            self.DicFortranObject[File]=DicFortranObject
        self.CleanUp()    
        self.FindFunction()
        self.FilterFunctionName()
        self.FindCallObject()
        self.FindExternalObject()
        
        self.FindFunctionObject()
        self.AddAssignedArgs()
        self.CleanUp()   

    def AddAssignedArgs(self):
        for File,DicObjectFortran in self.DicFortranObject.items():
            for ObjectFortran in DicObjectFortran.values(): 
                self.ExploreRecursiveAssignedArgs(ObjectFortran)
                
    def CleanUp(self):
        for File,DicFortranObject in self.DicFortranObject.items():
                for Name,FortranObject in DicFortranObject.items():
                    FortranObject['AssignedVars']=list(dict.fromkeys(FortranObject['AssignedVars']))
                    FortranObject['AssignedArgs']=list(dict.fromkeys(FortranObject['AssignedArgs']))
                    for Arg in FortranObject['AssignedArgs']:
                        if Arg in FortranObject['AssignedVars']:
                            FortranObject['AssignedVars'].remove(Arg)
                    FortranObject['AssignedNonLocalVars']=list(dict.fromkeys(FortranObject['AssignedNonLocalVars']))            
                
                
                
    def AnalyzeFortranContent(self,FortranContent,IgnoreCall=[]):
        if self.Verbose:
            print('## Analyzing {}:{}'.format(FortranContent.name,FortranContent.blocktype))
        if FortranContent.blocktype=='subroutine' or FortranContent.blocktype=='function':
           FortranObject={}
           FortranObject['Name']=FortranContent.name
           FortranObject['Content']=FortranContent.content
           FortranObject['Args']=self.FilterArgs(FortranContent.args)
           FortranObject['VariableDic']=FortranContent.a.todict()
           FortranObject['LocalVars']=self.FindLocalVars(FortranObject['VariableDic']['variables'],FortranContent.blocktype,FortranContent.name)
           FortranObject['Type']=FortranContent.blocktype
           FortranObject['Use']=self.FindModuleUse(FortranContent.content)
           FortranObject['Call']={}
           self.FindCall(FortranContent.content,FortranObject['Call'],IgnoreCall)
           FortranObject['CallObject']={}
           FortranObject['AssignedVars']=self.FindAssignedVars(FortranContent.content,FortranContent.name,FortranContent.blocktype)
           FortranObject['AssignedArgs']=self.FindAssignedArgs(FortranObject['AssignedVars'],FortranObject['Args'])
           FortranObject['AssignedVars']=self.CleanAssignedVars(FortranObject['AssignedVars'],FortranObject['Args'])
           FortranObject['AssignedNonLocalVars']=self.FindNonLocalAssignedVars(FortranObject['AssignedVars'],FortranObject['LocalVars'],FortranObject['Args'],FortranContent.name,FortranContent.blocktype)
           FortranObject['External']=self.FindExternal(FortranObject['VariableDic'])
           FortranObject['ExternalObject']={}
           
           FortranObject['Function']=[]
           FortranObject['FunctionObject']={}
        else: 
           print('Unknown blocktype {} for Object:{}'.format(FortranContent.blocktype,FortranContent.name))
           FortranObject=None
        return FortranObject
        
    @staticmethod    
    def FilterArgs(Args):
        ListArgs=[]
        for Arg in Args:
            ListArgs.append(Arg.split('(')[0].strip())
        return ListArgs    
    
    
                    
                    
    @staticmethod        
    def FindExternal(VariableDic,Verbose=False):
        ListExternalVar=[]
        for VarName,Var in VariableDic['variables'].items():
            
            if len(Var.attributes)>0 and Var.attributes[0]=='EXTERNAL':
                if Verbose:
                    print('External Call to:',VarName)
                ListExternalVar.append(VarName)
        return ListExternalVar
    
    @staticmethod
    def FindLocalVars(VariableDic,BlockType,ParentName,Verbose=False):
        ListLocalVars=[]
        for VarName,Var in VariableDic.items():
            if (len(Var.attributes)>0 and Var.attributes[0]!='EXTERNAL') or (len(Var.attributes)==0):
                if (BlockType=='function' and VarName!=ParentName) or (BlockType!='function'):
                    if Verbose:
                        print('Local Vars:',VarName)
                    ListLocalVars.append(VarName)
            
                
        return ListLocalVars
    
    @staticmethod
    def CleanExternal(External,LocalVars,Verbose=False):
        for Var in LocalVars:
            if Var in External:
                LocalVars.remove(Var)
        return LocalVars
            
            
             
    def FindCall(self,Content,DicCall,IgnoreCall=[]):
        
        for Line in Content:
            if type(Line)==one.statements.Call:
                if Line.designator not in IgnoreCall:
                    if self.Verbose:
                            print('Call to:',Line.designator) 
                    ListItems=[]
                    for item in Line.items:
                        ListItems.append(item.split("(")[0].strip())
                    if Line.designator not in DicCall.keys():
                        DicCall[Line.designator]=[ListItems]
                    else:
                        DicCall[Line.designator].append(ListItems)
            else:
                if hasattr(Line,'content'):
                   self.FindCall(Line.content,DicCall,IgnoreCall)
            
        return DicCall     
    
    def FindModuleUse(self,Content):
        ListMod=[]
        for Line in Content:
            if type(Line)==one.statements.Use:
                ModName=Line.item.line.split('use')[1].lower().strip()
                if self.Verbose:
                    print('Use ModName:',ModName)
                if ModName not in ListMod:
                    ListMod.append(ModName)
            else:
                if hasattr(Line,'content'):
                    ListMod.extend(self.FindModuleUse(Line.content))
        return ListMod
  
    def FindAssignedVars(self,Content,ParentName,BlockType):
        ListAssignedVariable=[]
        for Line in Content:
            if type(Line)==one.statements.Assignment:
                VarName=Line.variable.split('(')[0].strip()
                if self.Verbose:
                    print('Assigned Variable',VarName)
                if VarName not in ListAssignedVariable and ((BlockType!='function') or (BlockType=='function' and VarName!=ParentName)):
                    ListAssignedVariable.append(VarName)
            else:
                if hasattr(Line,'content'):
                    ListAssignedVariable.extend(self.FindAssignedVars(Line.content,ParentName,BlockType))
                    
        return ListAssignedVariable
    
    @staticmethod
    def FindAssignedArgs(ListAssignedVariable,ListArgs,Verbose=False):
        ListAssignedArgument=[]
        for Arg in ListArgs:
            if Arg in ListAssignedVariable:
                ListAssignedArgument.append(Arg)
                ListAssignedVariable.remove(Arg)
        return ListAssignedArgument
    
    @staticmethod
    def CleanAssignedVars(ListAssignedVariable,ListArgs):
        for Arg in ListArgs:
            if Arg in ListAssignedVariable:
                ListAssignedVariable.remove(Arg)
        return ListAssignedVariable
    
    
    
    def FindNonLocalAssignedVars(self,ListAssignedVars,ListLocalVars,ListArgs,ParentName,BlockType):
        ListNonLocalAssignedVars=[]
        for Var in ListAssignedVars:
            #if 'rra' in Var:
                #print('here is rra:',Var)
            if Var not in ListLocalVars and Var not in ListArgs and ( BlockType!='function' or (BlockType=='function' and Var!=ParentName)):
                #if Var=='rra':
                    #print('Adding rra here')
                ListNonLocalAssignedVars.append(Var)
        return ListNonLocalAssignedVars
    
    @staticmethod
    def GetListFunctions(DicFortranObject):
        ListFunctions=[]
        for File,DicFortranObject in DicFortranObject.items():
                for Name,FortranObject in DicFortranObject.items():
                    if FortranObject['Type']=='function':
                        ListFunctions.append(Name)
        return ListFunctions
    

    def FindFunction(self):
        ListFunctions=self.GetListFunctions(self.DicFortranObject)
        for File,DicFortranObject in self.DicFortranObject.items():
            for Name,FortranObject in DicFortranObject.items():
                for Var in FortranObject['LocalVars']:
                    if Var in ListFunctions:
                        self.DicFortranObject[File][Name]['Function'].append(Var)
                        self.DicFortranObject[File][Name]['LocalVars'].remove(Var)
    
    def FindCallObject(self):
        for File,DicFortranObject in self.DicFortranObject.items():
            for Name,FortranObject in DicFortranObject.items():
                for CallName in FortranObject['Call']:
                    if CallName not in list(self.DicFortranObject[File][Name]['CallObject'].keys()):
                        #if self.Verbose:
                        #    print
                        FortranObject['CallObject'][CallName]=self.FindFortranObject(CallName)
                        
    
    def FindExternalObject(self):
        for File,DicFortranObject in self.DicFortranObject.items():
            for Name,FortranObject in DicFortranObject.items():
                for CallName in FortranObject['External']:
                    if CallName not in list(self.DicFortranObject[File][Name]['ExternalObject'].keys()):
                        FortranObject['ExternalObject'][CallName]=self.FindFortranObject(CallName)
                        

    def FindFunctionObject(self):
        for File,DicFortranObject in self.DicFortranObject.items():
            for Name,FortranObject in DicFortranObject.items():
                for CallName in FortranObject['Function']:
                    if CallName not in list(self.DicFortranObject[File][Name]['FunctionObject'].keys()):
                        FortranObject['FunctionObject'][CallName]=self.FindFortranObject(CallName)                    

    def FilterFunctionName(self):
        for File,DicFortranObject in self.DicFortranObject.items():
            for Name,FortranObject in DicFortranObject.items():
                for Var in FortranObject['AssignedVars']: 
                    if Var in FortranObject['Function']:
                        FortranObject['AssignedVars'].remove(Var)
                                          
    def FindFortranObject(self,CalledObject):
        FortranObjectFound=None
        for File,DicFortranObject in self.DicFortranObject.items():
            if CalledObject in DicFortranObject.keys():
                if FortranObjectFound is not None:
                    if self.Verbose: print('Warning: already found called object: {} of type: {} in file:{}'.format(CalledObject ,DicFortranObject[CalledObject]['Type'],File))
                else:
                    FortranObjectFound=DicFortranObject[CalledObject]
                    if self.Verbose:
                        print('Found called Object:{} of type:{} in file:{}'.format(CalledObject ,DicFortranObject[CalledObject]['Type'],File))
                        
        return FortranObjectFound 
    
    
    def ExploreRecursiveAssignedArgs(self,FortranObject):
        if self.Verbose:
            print('Recursive search of assigned argument in {}'.format(FortranObject['Name']))
        
        for CallName,CallObject in FortranObject['CallObject'].items():
            if CallObject is not None:
                if self.Verbose:
                    print('Analyzing Call:',CallName)
                
                for ArgItems in FortranObject['Call'][CallName]:
                    
                    L0=len(ArgItems)
                    L1=len(CallObject['Args'])
                    if L0!=L1:
                        print(ArgItems)
                        print(CallObject['Args'])
                        raise ValueError('Mismatch between number of arguments for {}'.format(CallName))
                    self.ExploreRecursiveAssignedArgs(CallObject)
                    Iterator=zip(CallObject['Args'],ArgItems)
                    for (ChildArg,ParentArg) in Iterator:
                        if ChildArg in FortranObject['CallObject'][CallName]['AssignedArgs']:
                            if ParentArg not in FortranObject['LocalVars'] and ParentArg not in FortranObject['Function'] and ParentArg not in FortranObject['External']:
                                #if ParentArg =='rra':
                                    #print('rra in recur explo:',ParentArg)
                                    #print('Analyzing Call:',CallName)
                                    #print('ArgItems:', FortranObject['Call'][CallName])
                                FortranObject['AssignedNonLocalVars'].append(ParentArg) 
                            if ParentArg in FortranObject['Args'] and ParentArg not in FortranObject['AssignedArgs']:
                                FortranObject['AssignedArgs'].append(ParentArg)  
            else:
                pass
    def SetFfile(self,FileName):
        """
        Set the ffile attribute, which is the fortran file object.
        It the attribute hasn't been created, then open the file with write status.
        If it has, and the file is closed, then open it with append status.
        """
        if 'ffile' in self.__dict__:
            status = 'a'
        else:
            status = 'w'
        if status == 'w' or (status == 'a' and self.ffile.closed):
            self.ffile = open(FileName, status)    
            
    def fw90(self, text, noreturn=0):
        i = 0
        while len(text[i:]) > 132 and text[i:].find('&') == -1:
            # --- If the line is too long, then break it up, adding line
            # --- continuation marks in between any variable names.
            # --- This is the same as \W, but also skips %, since PG compilers
            # --- don't seem to like a line continuation mark just before a %.
            ss = re.search('[^a-zA-Z0-9_%]', text[i+130::-1])
            assert ss is not None, "Forthon can't find a place to break up this line:\n" + text
            text = text[:i+130-ss.start()] + '&\n' + text[i+130-ss.start():]
            i += 130 - ss.start() + 1
        if noreturn:
            self.ffile.write('      '+text)
        else:
            self.ffile.write('      '+text + '\n')
        
    def WriteCopyConvert(self,FileName='copyconvert.f90'):
        
        Laux=['call OmpCopyPointer{}'.format(V) for V in self.DicFortranObject['convert']['convsr_aux']['AssignedNonLocalVars']]
        Lvo=['call OmpCopyPointer{}'.format(V) for V in self.DicFortranObject['convert']['convsr_vo']['AssignedNonLocalVars']]
        self.SetFfile(FileName)
        self.fw90('subroutine CopyConvert')
        self.fw90('use OmpCopybbb')
        self.fw90('implicit none')
        for L in Lvo+Laux:
            self.fw90(L)
        self.fw90('end subroutine CopyConvert')
        self.ffile.close()
        
        
                         
def CompareListVar(File1,File2):
    L1=[v.strip() for v in open(File1).readlines()]
    L2=[v.strip() for v in open(File2).readlines()]
    LL1=[l for l in L1 if l not in L2]
    LL2=[l for l in L2 if l not in L1]
    print('List of variables in "{}" and not in "{}"'.format(File1,File2))
    print(LL1)
    print('List of variables in "{}" and not in "{}"'.format(File2,File1))
    print(LL2)
    

    

def MakeVarList(FileName='ListVariableThreadPrivate.txt',UEDGESourcePath='.',Verbose=False,PrintTree=False):
    Parser=UBoxParserFortran(Verbose)
    try:
        Parser.GetFortranTree(UEDGESourcePath,ExcludeList=['grdcomp.F','SROTMhG.F'])
        Parser.AnalyzeTree(IgnoreCall=['sendbdry','recvbdry','SROTMhG','b2vahl','b1vahl','intrhv'])
        
        IgnoreExternal=['gettime','xermshg','b2vahl','b1vahl','tick','tock','sdot']
        IgnoreFunction=['gettime','tick','tock']
        IgnoreCall=['xerrab','remark','freeus','gchange','system','exmain','store_neutrals','run_neutrals','run_uedge','run_eirene','run_degas2','writemcnfile','writemcnbkgd','readmcnsor','convertmcnsor','update_neutrals','scale_mcnsor','SROTMhG','xermshg','sscal','sgesl','b1vahl','intrhv','mombal','tick','tock','system_clock']
        IgnoreVariable=[]               
        
        
        Parser.Explore(EntryPoint=['oderhs','pandf1'],IgnoreCall=IgnoreCall,IgnoreExternal=IgnoreExternal,IgnoreFunction=IgnoreFunction,IgnoreVariable=IgnoreVariable)
        if PrintTree:
            Parser.PrintCallTree(EntryPoint=['oderhs','pandf1'],ShowVariable=True,ShowArgs=False)
        Parser.CleanUpAssignedDic()
        ExcludeList=['dtreal','rhseval','travis','parvis']+['yl', 'yldot00', 'ml', 'mu', 'wk','nnzmx', 'jac', 'ja', 'ia']
        Parser.WriteListAssignedVars(FileName,ExcludeList=ExcludeList,AdditionalVariables=['yinc','impradloc', 'yldot_pert'])
    except Exception as e:
        print('Error:',repr(e))
        raise e 
    finally:
        return Parser


          
        
    
    
