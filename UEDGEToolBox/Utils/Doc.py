#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    .. module:: Doc
        :platform: Unix, MacOS
        :synopsis: Documentation for UEDGE.

    .. moduleauthor:: Jerome Guterl <guterlj@fusion.gat.com>


"""

from UEDGEToolBox.Utils.Misc import GetListPackage
from colorama import  Back, Style
import uedge
#import uedge
#@UBoxPrefix

class UBoxDoc():
    """ UBoxDoc is a wrapper for the documentation of the various UEDGE variables contained in UEDGE packages (e.g bbb,com,...). 
    
    Note: 
        Aliases of the various public methods are available in the global namespace and can be access from the shell (e.g Search('ni')).
    """
    
    #---------------------------------------------------------------------------
    def __init__(self,Verbose:bool=False):
            self.ListPkg=GetListPackage()
            self.DocPkg={}
            self.DocGrp={}
            self.DocCom={}
            self.widthP=5
            self.widthV=20
            self.widthG=25
            self.widthU=10
            self.__SetupDoc()

    def ShowGroup(self,PkgName:str=None):
        """
        Print list of groups in package PkgName.
        If PkgName is None, print  groups for all UEDGE package.  
        
        Examples:
            >>> Doc.ShowGroup('bbb')
            >>> ShowGroup('bbb')

        Args:
            PkgName (str, optional): Name of package. Defaults to None.
        """
        if PkgName is None:
            ListG=list(self.DocGrp.keys())
            ListG.sort()
            for G in ListG:
                self.__PrintGrpInfo(G,self.DocGrp[G]['Package'])
        else:
            print('Group in package:',PkgName)
            ListG=[g for (g,v) in self.DocGrp.items() if v['Package']==PkgName]
            ListG.sort()
            for G in ListG:
                self.__PrintGrpInfo(G,PkgName)
            
    def ShowPackage(self):
        """
        Print the list of UEDGE packages currently loaded in the global namespace.

        >>> Doc.ShowPackage()
        >>> ShowPackage()
        """
        
        ListP=list(self.DocPkg.keys())
        ListP.sort()
        for P in ListP:
            self.__PrintPkgInfo(P)
        return 
                
    #---------------------------------------------------------------------------
    def ShowVar(self,ObjectName:str or list=None,Start:str='',Contain:str='',OnlyVar:bool=True,Sorted:bool=True):
        """
        Print a list of UEDGE variables contained in packages or groups given by ObjectName. If ObjectName is None, all UEDGE variables are displayed.  
        Args:
            ObjectName (str or list, optional): list or name of UEDGE groups or packages. Defaults to None.
            Start (str, optional): Print only variables with name startingw with "Start". Defaults to ''.
            Contain (str, optional): Print only variables with names containing "Contain". Defaults to ''.
            OnlyVar (bool, optional): True: do not print documentation. Defaults to True.
            Sorted (bool, optional): Sort printed variables by name. Defaults to True.

        Returns:
            None.

        """ 
        Dic={}
      #  ListV=[]
        if ObjectName is None:
           ObjectName=self.ListPkg
           
        if type(ObjectName)==str:
            ObjectName=[ObjectName]
            
        for S in ObjectName:    
            if self.DocPkg.get(S) is not None:
                #Dic.update(self.DocPkg.get(S).fromkeys([v for v in self.DocPkg.get(S).keys() if v.startswith(Start)]))
                ListV=[v for v in self.DocPkg.get(S).keys() if v.startswith(Start) and Contain in v]
                #ListV.sort()
                for V in ListV:
                    Dic[V]=self.DocPkg.get(S)[V]
                    #self.__PrintVarInfo(self.DocPkg.get(S)[V],OnlyVar) 
            if self.DocGrp.get(S) is not None:
                ListV=[v for v in self.DocGrp.get(S).keys() if v.startswith(Start) and Contain in v and v != 'Package']
                #ListV.sort()
                for V in ListV:
                    Dic[V]=self.DocGrp.get(S)[V]
                    #self.__PrintVarInfo(self.DocGrp.get(S)[V],OnlyVar)
        if Sorted:
            for k,v in sorted(Dic.items()):
                self.__PrintVarInfo(v,OnlyVar)
        else:
            for k,v in Dic.items():
                self.__PrintVarInfo(v,OnlyVar)
                
        
            
    def SearchDoc(self,Str:str):
        """
        Print a list of UEDGE variables containing the string Search Str in their documentation. 
    
        Args:
            Str (str): String contained in documentation of UEDGE variables.
    
        Returns:
            None.
    
        """
        
        
        for pkg in self.ListPkg:
            Dic=self.DocPkg[pkg]
            for k in Dic.keys():
                    if Str in Dic[k]['Doc']: 
                        self.__PrintVarInfo(Dic[k],False)
                    
    def Search(self,Str:str,Exact:bool=False,OnlyVar:bool=False,Silent:bool=False):
        """  
        Return the list of UEDGE variables for which the input string is contained in the variable name or/and documentation.
        Example: Search('ni')

        Args:
            Str (str): string contained in names of UEDGE variables.
            Exact (bool, optional): look for exact match between input string and variable name. Defaults to False.
            OnlyVar (bool, optional): True: Print only UEDGE variable names | False: Print only UEDGE variable names and documentation.  Defaults to False.
            Silent (bool, optional): Print list of results when Silent=False. Defaults to False.

        Returns:
            Out (list): return list of dictionaries describing UEDGE variables if Silent is True.

        """
        
        Out:list=[]
        for pkg in self.ListPkg:
            Dic=self.DocPkg[pkg]
            for k in Dic.keys():
                if Exact:
                    if Str==k:
                        if not Silent:
                            self.__PrintVarInfo(Dic[k],OnlyVar)
                        Out.append(Dic[k])
                else:
                    if Str in k:
                        if not Silent:
                            self.__PrintVarInfo(Dic[k],OnlyVar)
                        Out.append(Dic[k])
        if Silent:
            return Out  
        
        
        
    def __ParseInfoVar(self,Str)->dict:
        d={}
        Fields=['Package','Group','Attributes','Dimension','Type','Address','Pyadress','Unit','Comment']
        for F in Fields:
            if F!='Comment':
                idx=Str.find(F+':')
                if idx>-1:
                    S=Str[idx+len(F+':'):]
                    idxS=S.find('\n')
                    S=S[:idxS].strip()
                else:
                    S=None
            else:
                idx=Str.find(F+':')
                if idx>-1: 
                    S=Str[idx+len(F+':'):].strip()
                else:
                    S=None
            d[F]=S
        return d        
    
    #---------------------------------------------------------------------------  
    def __PrintGrpInfo(self,G:str,P:str=None):
        
        if P is not None:
            SP='{colorG}{:<{widthP}}{reset}'.format(P,colorG=Back.RED,reset=Style.RESET_ALL,widthP=self.widthP)
        else:
            SP=''
            
        S='{colorG}{:<{widthG}}{reset}'.format(G,colorG=Back.CYAN,reset=Style.RESET_ALL,widthG=self.widthG)
        print('{} {}'.format(SP,S))
    #---------------------------------------------------------------------------  
    def __PrintPkgInfo(self,P:str):
        
        S='{colorG}{:<{widthP}}{reset}'.format(P,colorG=Back.RED,reset=Style.RESET_ALL,widthP=self.widthP)
        print(S)
    #---------------------------------------------------------------------------     
    def __PrintVarInfo(self,Dic,OnlyVar=False):
        if 'Function' in list(Dic.keys()):
            SP='{colorG}{:<{widthP}}{reset}'.format(Dic.get('Package'),colorG=Back.RED,reset=Style.RESET_ALL,widthP=self.widthP)
            S='{colorV}{:<{widthV}}\
                {reset}'.format(Dic.get('Variable'),colorV=Back.YELLOW,reset=Style.RESET_ALL,widthV=self.widthV)
            print('{:<{widthV}} {:<{widthP}}  '.format(S,SP,widthP=self.widthP,widthV=self.widthV))
        else:    
            if OnlyVar:
                SP='{colorG}{:<{widthP}}{reset}'.format(Dic.get('Package'),colorG=Back.RED,reset=Style.RESET_ALL,widthP=self.widthP)
                SG='{colorG}{:<{widthG}}{reset}'.format(Dic.get('Group'),colorG=Back.CYAN,reset=Style.RESET_ALL,widthG=self.widthG)
                S='{colorV}{:<{widthV}}\
                    {reset}'.format(Dic.get('Variable'),colorV=Back.GREEN,reset=Style.RESET_ALL,widthV=self.widthV)
                print('{:<{widthV}} {:<{widthP}} {:<{widthG}} '.format(S,SP,SG,widthG=self.widthG,widthP=self.widthP,widthV=self.widthV))
            else:
                    
                S='{colorV}{:<{widthV}}{reset} : {color}{:<{widthP}}{reset}\
                    / {colorG}{:<{widthG}}{reset}  [{:<}] : {} : {colorD}{:.10}{reset}\
                        '.format(Dic.get('Variable'),Dic.get('Package'),Dic.get('Group'),Dic.get('Unit'),\
                        Dic.get('Dimension'),str(Dic.get('Default')),widthP=self.widthP,widthV=self.widthV,colorV=Back.GREEN\
                            ,color=Back.RED,reset=Style.RESET_ALL,colorG=Back.CYAN,widthG=self.widthG,colorD=Back.MAGENTA)
                print(S)
        	#NLines=Dic.get('Comment').count('\n')
                for S in Dic.get('Comment').split('\n'):
                    print('{:<{widthV}} : {:<}'.format(' ',S,widthV=self.widthV))
                    print('')
                
 

        
    #---------------------------------------------------------------------------                    
    def _GetVarInfo(self,Str,exact=True):
        L=[]
        for pkg in self.ListPkg:
            Dic=self.DocPkg[pkg]
            for k in Dic.keys():
                if exact:
                    if Str==k:
                     L.append(Dic[k])
                else:
                    if Str in k: 
                     L.append(Dic[k])
        return L
    #---------------------------------------------------------------------------                     
    def __SetupDoc(self):
        for pkg in self.ListPkg:
            loc={}
            self.DocPkg[pkg]={}
            exec('VarList=uedge.'+pkg +'py.'+ pkg+'.varlist()',globals(),loc)
            exec('FuncList=uedge.'+pkg +'py.'+ pkg+'.getfunctions()',globals(),loc)
            VarList=loc['VarList']
            FuncList=loc['FuncList']
            for V in VarList:
                exec('VarStr=uedge.'+pkg +'py.'+ pkg+'.listvar("'+V+'")',globals(),loc)
                VarStr=loc['VarStr']
                
                if V in self.DocPkg[pkg].keys():
                    print('Variable is already defined:',self.DocVar[pkg][V])
                    print('V:',V,'pkg:',pkg)
                    raise ValueError('Variable is already defined')

                try :
                    exec('Val=' + pkg+'.'+V,globals(),loc)
                except: 
                   loc['Val']=None
                Val=loc['Val']

                
                self.DocPkg[pkg][V]=self.__ParseInfoVar(VarStr)
                self.DocPkg[pkg][V]['Variable']=V
                if Val is None:
                    Val=''
                self.DocPkg[pkg][V]['Default']=Val
                self.DocPkg[pkg][V]['Doc']=VarStr
                #self.DocDict[pkg][V]
        for pkg in self.ListPkg:
            for V,D in (self.DocPkg[pkg].items()):
                if 'Group' in D.keys(): 
                    if not D['Group'] in self.DocGrp.keys():
                        self.DocGrp[D['Group']]={}
                    self.DocGrp[D['Group']][V]=D
                    self.DocGrp[D['Group']]['Package']=pkg
            # Functions
            for F in FuncList:
                if F in self.DocPkg[pkg].keys():
                    print('Variable is already defined:',self.DocVar[pkg][V])
                    print('V:',V,'pkg:',pkg)
                    raise ValueError('Variable is already defined')         
                else:
                    self.DocPkg[pkg][F]={'Function':F,'Package':pkg}
    #---------------------------------------------------------------------------
    
    # def HelpDoc(self):
    #     print('****** UEDGE Documentation ***** ')
    #     print('*** Documentation command ***')
    #     print('- ListGrp()')
    #     print('- ListPkg()')
    #     print('- ListVar(): list variable in package or group')
    #     print('- Search()')
    #     print('- SearchDoc()')                     
#---------------------------------------------------------------------------                
#---------------------------------------------------------------------------
                    

 
#---------------------------------------------------------------------------
# def ListGrp(Str=None,OnlyVar=True):
#     Doc.ListGrp(Str,OnlyVar)
    
# #---------------------------------------------------------------------------
# def ListPkg(Str,OnlyVar=True):
#     Doc.ListPkg()
    
# #---------------------------------------------------------------------------
# def ListVar(Str,InStr='',OnlyVar=True):
#     Doc.ListVar(Str,InStr,OnlyVar)
    
# #---------------------------------------------------------------------------
# def Search(Str,exact=False,OnlyVar=False):
#     Doc.Search(Str,exact,OnlyVar)
# #--------------------------------------------------------------------------    
# def SearchSilent(Str,exact=True,OnlyVar=False):
#     return Doc.Search(Str,exact,OnlyVar,Silent=True)
# #--------------------------------------------------------------------------
        
# def SearchDoc(Str,OnlyVar=False):
#     Doc.SearchDoc(Str,OnlyVar)

# def HelpDoc():
#     Doc.HelpDoc()
