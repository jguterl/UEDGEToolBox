#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 19:20:36 2020

@author: jguterl
"" 16.84704033613164
   16.84704064249413
"""

import numpy as np
import os
import uedge
#from uedge.UEDGEDoc import *
def DumpData(FileName,DataName):
    com='np.savetxt("{}",{})'.format(FileName,DataName)
    exec(com,globals(),locals())
    
def BatchDumpData(Suffix:str,Folder:str,VarList:list,Verbose=False):
    import uedge
    from uedge import bbb,com,grd,flx,api,aph
    for V in VarList:
        Result=SearchSilent(V,exact=True)
        if len(Result)>0:
            Package=Result[0]['Package']
            FileName=os.path.join(Folder,'{}_{}.txt'.format(V,Suffix))
            DataName='{}.{}'.format(Package,V)
            if Verbose:
                print(FileName)
                print(DataName)
        
            comm='np.savetxt("{}",{}.flatten(),header=str({}.shape))'.format(FileName,DataName,DataName)
            exec(comm,globals(),locals())
        else:
            print('skipping {}'.format(V))

            
def GetList(FileName):
    with open(FileName) as f:
        out=f.read().splitlines()
    return list(dict.fromkeys(out))

def Compare(Suffixes:list,Folder:str,VarList:list,Verbose=False,Precision=1e-15):
    Dic={}
    if len(Suffixes)!=2: raise ValueError('Suffixes must be a list of two elements')
    for V in VarList:
        for S in Suffixes:
            FileName=os.path.join(Folder,'{}_{}.txt'.format(V,S))
            DataName='{}_{}'.format(V,S)
            com='{}=np.loadtxt("{}")'.format(DataName,FileName)
            exec(com,globals(),Dic)
            
    for V in VarList:
        Data=[]
        for S in Suffixes:
            DataName='{}_{}'.format(V,S)
            Data.append(Dic[DataName])
            
        diff=np.where(abs((Data[0]-Data[1])/Data[0])>Precision)[0].shape
        print('{}:{}'.format(V,diff))
    return Dic

def CompareOMPJacobian(Suffixes:list,Folder:str,VarList:list,Verbose=False,Precision=1e-15):
    Dic={}
    if len(Suffixes)!=2: raise ValueError('Suffixes must be a list of two elements')
    for V in VarList:
        for S in Suffixes:
            FileName=os.path.join(Folder,'{}_{}.txt'.format(V,S))
            DataName='{}_{}'.format(V,S)
            com='{}=np.loadtxt("{}")'.format(DataName,FileName)
            exec(com,globals(),Dic)
            
    for V in VarList:
        Data=[]
        for S in Suffixes:
            DataName='{}_{}'.format(V,S)
            Data.append(Dic[DataName])
            
        diff=np.where(abs((Data[0]-Data[1])/Data[0])>Precision)[0].shape
        print('{}:{}'.format(V,diff))
    return Dic


def CompareOMPJacobian(Suffixes:list,Folder:str,VarList:list,Verbose=False,Precision=1e-15):
    Dic={}
    if len(Suffixes)!=2: raise ValueError('Suffixes must be a list of two elements')
    for V in VarList:
        for S in Suffixes:
            FileName=os.path.join(Folder,'{}_{}.txt'.format(V,S))
            DataName='{}_{}'.format(V,S)
            com='{}=np.loadtxt("{}")'.format(DataName,FileName)
            exec(com,globals(),Dic)
            
    for V in VarList:
        Data=[]
        for S in Suffixes:
            DataName='{}_{}'.format(V,S)
            Data.append(Dic[DataName])
            
        diff=np.where(abs((Data[0]-Data[1])/Data[0])>Precision)[0].shape
        print('{}:{}'.format(V,diff))
    return Dic
    
class WriteDebugRoutine():
    def __init__(self,FileName,ListVariable,Doc,Verbose=False):
        
        self.Doc=Doc
        self.ImportList(ListVariable)
        self.FileName=FileName
        self.ListUse=[]
        self.VarDic={}
        self.Verbose=Verbose
        
    def WriteRoutine(self):
        self.GetVarDoc()
        self.GetListGrp()
        self.WriteFortranSubroutine()
        
    def ImportList(self,ListVariable):
        if type(ListVariable)==str:
            self.ListVariableFile=os.path.abspath(ListVariable)
            self.ListVariable=[D.strip() for D in open(self.ListVariableFile,'r').readlines()]
        self.ListVariable=list(dict.fromkeys(self.ListVariable))
        self.ListVariable.sort()
        
    def SetFfile(self):
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
            self.ffile = open(self.FileName, status)    
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
    def GetVarDoc(self):
        for VarName in self.ListVariable:
            VarDoc=self.Doc._GetVarInfo(VarName)
            if self.Verbose:
                VarName
            if len(VarDoc)<1:
                print('Cannot find variable {}'.format(VarName))
            elif len(VarDoc)>1:
                print('Found variable {} in two groups'.format(VarName))
            else:
                self.VarDic[VarName]=VarDoc[0]
    def GetListGrp(self):
        for VarName,VarDoc in self.VarDic.items():
            self.ListUse.append(VarDoc['Group'])
        self.ListUse=list(dict.fromkeys(self.ListUse))
        self.ListUse.sort()
        
    def WriteFortranSubroutine(self):
        self.SetFfile()
        self.fw90('subroutine WriteArrayReal(array,s,iu)')
        self.fw90('implicit none')
        self.fw90('real:: array(*)')
        self.fw90('integer:: i,s,iu')
        self.fw90('do i=1,s')
        self.fw90('write(iu,*) array(i)')
        self.fw90('enddo')
        self.fw90('end subroutine WriteArrayReal')
        self.fw90('subroutine WriteArrayInteger(array,s,iu)')
        self.fw90('implicit none')
        self.fw90('integer:: array(*)')
        self.fw90('integer:: i,s,iu')
        self.fw90('do i=1,s')
        self.fw90('write(iu,*) array(i)')
        self.fw90('enddo') 
        self.fw90('end subroutine WriteArrayInteger')
        
        
        self.fw90('subroutine DebugHelper(FileName)')
        
        self.fw90('')
        for UseGrp in self.ListUse:
            self.fw90('Use {} '.format(UseGrp))
        self.fw90('implicit none')
        self.fw90('integer:: iunit')
    
        self.fw90('character(len = *) ::  filename')    
        self.fw90('open (newunit = iunit, file = trim(filename))')
        for VarName,VarDoc in self.VarDic.items():
            self.fw90('write(iunit,*) "{}"'.format(VarName))
            if VarDoc['Dimension'] is None:
                self.fw90('write(iunit,*) {}'.format(VarName))
            else:
                if 'integer' in VarDoc['Type']:
                    self.fw90('call WriteArrayInteger({},size({}),iunit)'.format(VarName,VarName))
                elif 'real' in VarDoc['Type'] or 'double' in VarDoc['Type']:
                    self.fw90('call WriteArrayReal({},size({}),iunit)'.format(VarName,VarName))    
                else:
                    raise ValueError('Unknown type')
        self.fw90('close(iunit)')    
        self.fw90('end subroutine DebugHelper')
        self.ffile.close()
#%% 
#Dic File is generated by the script UEDGEFortranParser.py  
#ListVariable=DicFile['convert']['convsr_vo']['AssignedNonLocalVars']+DicFile['convert']['convsr_aux']['AssignedNonLocalVars']+DicFile['odepandf']['pandf']['AssignedNonLocalVars']     
#dbg=WriteDebugRoutine('DebugHelper.F90',ListVariable,Doc)
#%%
def CompareDebugDump(FileName1='dumpserial.txt',FileName2='dumpomp.txt',Folder=None):
    if Folder is None:
        FileName1=os.path.abspath(FileName1)
        FileName2=os.path.abspath(FileName2)
    else:
        FileName1=os.path.join(os.path.abspath(Folder),FileName1)
        FileName2=os.path.join(os.path.abspath(Folder),FileName2)
    VarCheck=CompareDump(FileName1,FileName2)
    # for V,B in VarCheck.items():
    #     if not B:
    #         print('###',V)
            
def CompareDump(FileName1,FileName2):
    
    Dic1=ReadDumpFile(FileName1)
    Dic2=ReadDumpFile(FileName2)
    
    VarCheck={}
    
    for Var in Dic1.keys():
        VarCheck[Var]=True  
        if len(Dic1[Var])!=len(Dic2[Var]):
            print('##',Var,len(Dic1[Var]),len(Dic2[Var]),)
            VarCheck[Var]=False
            #aise ValueError('dics of different length')
            continue
        isfirst=True
        for i,(L1,L2) in enumerate(zip(Dic1[Var],Dic2[Var])):
            if L1!=L2:
                VarCheck[Var]=False
                if isfirst:
                    print(Var,i,L1,L2)
                    isfirst=False
                
    return VarCheck
                
def ReadDumpFile(FileName):
    file = open(FileName, 'r') 
    Lines = file.readlines()
    file.close()
    Dic={}
    for L in Lines:
        L=L.rstrip().strip()
        try:
            Lf=float(L)
            isnumeric=True
        except:
            isnumeric=False
        if not isnumeric:
            VarName=L
            Dic[VarName]=[]
        else:
            Dic[VarName].append(float(L))
    return Dic

     
def CompareJac(SerialFile='serialjac.dat',ParallelFile='paralleljac.dat',Folder=None):
    if Folder is None:
        SerialFile=os.path.abspath(SerialFile)
        ParallelFile=os.path.abspath(ParallelFile)
    else:
        SerialFile=os.path.join(Folder,SerialFile)
        ParallelFile=os.path.join(Folder,ParallelFile)
    array=np.loadtxt(SerialFile)
    array_omp=np.loadtxt(ParallelFile)
    neq=int(max(array[:,0]))
    print('Comparing jacobian in {} to jacobian in {} for neq={}'.format(SerialFile,ParallelFile,neq))
    for i in range(0,array.shape[0]):
        if array_omp[i,2]!=array[i,2] or array_omp[i,1]!=array[i,1] or array_omp[i,3]!=array[i,3]:
            print(i)
            print(array[i,:])
            print(array_omp[i,:])
            break
            
    
   