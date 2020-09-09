#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 14:06:22 2020
@author: jguterl
"""
import os
from UEDGEToolBox.Utils.Doc import UBoxDoc
from UEDGEToolBox.Utils.Misc import LsFolder
from UEDGEToolBox.ProjectManager.Source import UBoxSource
from uedge import *
import re
from datetime import datetime

class UBoxBas2Py():
    def __init__(self,Verbose=False,VerboseParserVar=False,VerboseArgout=False,Doc=None):
        self.Verbose=Verbose
        self.VerboseArgout=VerboseArgout
        self.VerboseParserVar=VerboseParserVar
        self.ActionKeyWord=['read','remark']
        self.TypeBas=['integer','real','character','real8','integer8']
        self.ExcludeList=['echo','oldecho','exponseed']
        self.Doc=UBoxDoc()
        self.MathSymbols=['+','-','/','*']
            
    def Convert(self,BasFileName,PyFileName=None,ExcludeList=[],Imax=None,Verbose=None):
        if Verbose is not None:
            self.Verbose=Verbose
            self.VerboseArgout=Verbose
            self.VerboseParserVar=Verbose
        if PyFileName is None:
                PyFileName=os.path.splitext(BasFileName)[0] + '.py'


        print('Converting Basis file:{} -> {}'.format(BasFileName,PyFileName))  
            
        with open(BasFileName,'r') as self.f:
            with open(PyFileName,'w') as self.fw:
                #Lines = f.readlines() 
                self.Line=next(self.f,None)
                self.LineNumber=0
                self.fw.write('#>>> Produced by UBoxBas2Py. Original file: {}\n'.format(BasFileName))
                self.fw.write('#>>> Timestamp: {:%Y-%m-%d %H:%M:%S}\n'.format(datetime.now()))
                self.fw.write('iota=np.array([np.arange(1,i+1) for i in range(1,300)],dtype=np.ndarray)\n')
                self.fw.write("api.apidir=Source('api',Folder='InputDir')") 
                self.fw.write("aph.aphdir=Source('aph',Folder='InputDir')")
                while self.Line:
                    if Imax is not None and self.LineNumber>Imax:
                        break
                    LineOut=self.__LineParser(self.Line,self.ExcludeList+ExcludeList)
                    self.LineNumber+=1
                    self.fw.write(LineOut+'\n')
                    self.Line=next(self.f,None)  
                    
    def __LineParser(self,Line,ExcludeList=[]):
            Out=[]
            
            Line=Line.strip('\n').strip('\r').strip()
            if self.Verbose:
                print('>>>> Parsing Line #{} : {}'.format(self.LineNumber,Line))
            # First we ignore all comments in line

  
            #Gather cut lines
            while Line.endswith('\\'):
               Lnext=next(self.f)
               self.Line=Lnext
               Line=Line.split('\\')[0]+Lnext.rstrip()
            Line=Line.strip('\n').strip('\r').strip()
            #remove trailing comments 
            Comment=''
            
            if Line.count('#')>0:
                Comment='#'+Line.split('#',1)[1]
                Line=Line.split('#',1)[0]
            Line=Line.strip('\n').strip('\r').strip() 
            
            if Line=='':
                pass

            # Second we look for several commands in one line 
            elif Line.count(';')>0:
               Line=Line.split(';')
               for L in Line:
                   Out.append(self.__LineParser(L)+'\n')
            
            elif Line.startswith('!'):
                Out.append('#>> '+Line)
                
            else:
            
                ##############################################
                #Third Let do the special keywords and commands
                Splt=Line.strip().split(' ',1)
                Kw=Line.strip().split(' ',1)[0].strip()
                if len(Splt)>1:
                    Arg=Line.strip().split(' ',1)[1].strip()
                    if self.Verbose: print('>>>>>>>> Keyword found:{} with argument:{}'.format(Kw,Arg))
                else:
                    Arg=''
                
                if Kw in ExcludeList:
                         Out.append('##'+Line)
                         
                elif Kw in 'read':
                        if len(Arg)>0 and 'plate' not in Arg:
                           Out.append('ReadInput("'+Arg+'")') 
                        else:
                           Out.append('#>> '+Line)
                    #deal with remark:
                elif Kw in 'remark' or Kw in '<<':
                        if len(Arg)>0:
                           Out.append('print('+Arg+')')
                        else:
                           Out.append('#>> '+Line)
                           
                elif Kw in self.TypeBas or 'character*' in Kw.lower():
                        if '=' in Arg:
                            Out.append(self.__LineParser(Arg))
                        else:
                            Out.append('#>> '+Arg)
                            
                elif Kw in 'call':
                            Out.append('#>> '+Arg)
     
                    
                else:
                    if Line.count('=')==0: # not an assignment
                        if Line.strip()=='allocate':
                            OutVar='bbb.allocate()'
                        else:
                            OutVar=self.__ParseVariable(Line,ForceCheck=True)
                        
                        if OutVar is None:
                            Out.append('#>> '+Line) 
                        else:
                            Out.append(OutVar)
                    
                    else:
                        
                                
                        Var=Line.split('=')[0].strip()
                        Arg=Line.split('=')[1].strip()
                        if Var in self.ExcludeList:
                            Out.append('#>> '+Var+'='+Arg)
                        if Var=='probname':
                            Out.append('SetCaseName({})'.format(Arg))
                        else:
                            if Var=='del':
                                    Var='delperturb'
                            
                            Varout=self.__ParseVariable(Var,ForceCheck=False,ExcludeList=ExcludeList)
                            Argout=self.__ParseArgout(Arg)
                            
                            if self.Verbose: print('>>>>>>>> Assignment found for "{}" -> {}={}'.format(Line,Varout,Argout))

                            if Varout is not None:
                                
                                Out.append(Varout+'='+Argout)
                            else:
                                
                                Out.append(Var+'='+Argout)
                        
            if Out==[]:
                Out=[Comment]
            else:
                Out.append('  '+Comment)
            Out=''.join(Out)
            if self.Verbose: print('>>>> Result of parsing:{}'.format(Out))
            return  Out
        
    def __ParseArgout(self,Arg,SymbolIndex=0): 
        
        if SymbolIndex>len(self.MathSymbols)-1:
            return Arg
        else:
            Symbol=self.MathSymbols[SymbolIndex]
        Args=Arg.strip().split(Symbol)
        CArgs=Arg.strip().count(Symbol)
        if self.VerboseArgout:
            print('Splitting Argout={}, with Symbol "{}":{}'.format(Arg,Symbol,Args))
            
        SymbolIndex_=SymbolIndex+1
        Argouts=[]
        for Argo in Args:
            Argo=Argo.strip()
            
            Argo=self.__ParseArgout(Argo,SymbolIndex_)
            Argo=self.__SubExpo(Argo)
            Argo=self.__ParseVariable(Argo,ForceCheck=False)
            Argo=Argo.strip()
            if CArgs>0 and Argo.startswith('[') and Argo.endswith(']'):
                Argo="np.array({})".format(Argo)
            Argouts.append(Argo)
        
        return Symbol.join(Argouts)
          
    def __SubExpo(self,Arg):
         if self.IsFloat(Arg):
             Arg=Arg.replace('D','e')
             Arg=Arg.replace('d','e')
         return Arg
     
    def __GetPackageMethod(self,VarName):
        
            Out=self.Doc.Search(VarName,Exact=True,Silent=True)
            
            if len(Out)<1 or Out[0] is None or Out[0].get('Function') is None:
                return None
            else:
                return Out[0]
            
    
    def __GetPackageVariable(self,VarName,IsDim=False):
        
        Info=self.Doc.Search(VarName,Silent=True,Exact=True)    
        if len(Info)>1:
            raise ValueError('More than one variable name found for {}'.format(VarName))
        if len(Info)<1:
           # if not a variable of a package, check if this is a package method      
            Out=None
        else:    
            Out=Info[0]['Package']+'.'+VarName
            if Info[0].get('Dimension') is not None and '(' in Info[0]['Dimension'] and IsDim:
                Out=Out+'[0]'
        return Out
    
    def __ParseVariable(self,Var,ForceCheck=True,ExcludeList=[],IsDim=False):
        
        Var=Var.strip()
        if Var in ExcludeList:
            return '#>> '+ Var
        # Does Var has dimension?
        #print('#Var:',Var) 
        if Var.isnumeric() or self.IsFloat(Var):
            return Var
        
        if Var.startswith('array') or Var.startswith('np.array'):
            return Var
        if Var.startswith('[') and Var.endswith(']'):
            return Var
        VarName=Var.strip().split('(')[0].strip()
        
        
        if VarName.endswith('array') or VarName.endswith('np.array'):
            return Var
        
        
        Out=self.__ParseVariableName(VarName,IsDim=IsDim)
        
        if Out is None: 
            if ForceCheck:
                return '#>> ' + Var
            else:
                Out=Var.strip().split('(')[0].strip()
                       
        if '(' in Var:
                il=Var.find('(')+1
                ir=Var.rfind(')')
                Dim=Var[il:ir].strip()
                Dout=self.__ParseVariableDim(Dim)
                #print(Dim,'->',Dout)
                Out=Out+'['+Dout+']'    
        
        if self.VerboseParserVar:
            print('Parsing variable "{}" -> {}'.format(Var,Out))        
        return Out        
                
    def __ParseVariableName(self,VarName,IsDim=False):
        Out=self.__GetPackageVariable(VarName,IsDim=IsDim)
        if Out is None:
            Out=self.__GetPackageMethod(VarName)
        return Out
    
    def __ParseMathSymbol(self,Str):
        Out=[]
        W=''
        
        for c in Str:
            if c in self.MathSymbols:
                Out.append(W)
                Out.append(c)
                W=''
            else:
                W=W+c
        Out.append(W)    
        return Out   
    
    def __ParseVariableDim(self,Dim):
        Dout=[]
        idl=self.findall(Dim,'(')
        idr=self.findall(Dim,')')
        idc=self.findall(Dim,',')
        Ind=[-1]
        if (len(idl)!=len(idr)):
        
            raise ValueError('Cannot parse expression with incomplete bracket:',Dim)
        Ind.extend([i for i in idc if all([False for (il,ir) in zip(idl,idr) if i>=il and i<=ir])])
        DimArgs = [Dim[i+1:j] for i,j in zip(Ind, Ind[1:]+[None])]

        #print('DimArgs:',DimArgs)
        for D in DimArgs:
            #print('D:',D)
            d=D.strip()
            if d!='':
                rout=[]
                IsFirst=True
                for r in d.split(':'):
                    
                    rr=self.__ParseMathSymbol(r)
                    outrr=[]
                    for rrr in rr:
                        if rrr in self.MathSymbols:
                            outrr.append(rrr)
                        else:
                            O=self.__ParseVariable(rrr,ForceCheck=False,IsDim=True)
                            outrr.extend(O)
                    routrr=outrr
                    if IsFirst:
                        if len(routrr)==1 and routrr[0].isnumeric(): 
                            routrr=[str(int(routrr[0])-1)]
                        else:
                            routrr.extend('-1')
                    IsFirst=False        
                    rout.append(''.join(routrr))
                Dout.append(':'.join(rout))
            else:
                Dout.append(':')
        Dout=','.join(Dout) 
        return Dout
    
    @staticmethod
    def IsFloat(Str):
        try:
            float(Str) # for int, long and float
        except ValueError:
            return False
        return True
        
    def findall(self,string,substring):
        """
        Function: Returning all the index of substring in a string
        Arguments: String and the search string
        Return:Returning a list
        """
        length = len(substring)
        c=0
        indexes = []
        while c < len(string):
            if string[c:c+length] == substring:
                indexes.append(c)
            c=c+1
        return indexes
# if __name__== "__main__":
#    UEDGEBas2Py('/home/jguterl/Dropbox/python/UEDGEInputDir/InputW.bas','/home/jguterl/Dropbox/python/UEDGEInputDir/InputW.py',Verbose=True)
#    UEDGEBas2Py('/home/jguterl/Dropbox/python/UEDGEInputDir/plate2.iter-feat.bas','/home/jguterl/Dropbox/python/UEDGEInputDir/plate2.iter-feat.py',Verbose=True)        
        
def ConvertBas2Py(BasFileName=None,PyFileName=None,Folder=None,**kwargs):
        if Folder is None:
            Folder=os.getcwd()
        if BasFileName is None:
            BasFileName=LsFolder(Folder,Ext='*')
        if BasFileName is None:
            print("No basis file provided... Exiting")
            return

        FilePath=UBoxSource.Source(BasFileName,None,None,None)
        # Looking for file
        if FilePath is not None and os.path.isfile(FilePath):
            UBoxBas2Py().Convert(FilePath,PyFileName,**kwargs)
        else:
            print("Cannot read the file {}... Exiting".format(FilePath))

    