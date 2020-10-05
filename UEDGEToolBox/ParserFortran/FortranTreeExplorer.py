class UBoxPrintFortranTree():
        
    def PrintAssignedArgs(self,FortranObject,level):
        if FortranObject is not None and FortranObject['AssignedArgs'] is not None:
            FortranObject['AssignedArgs'].sort()
            for VarName in FortranObject['AssignedArgs']:
                L=self.Doc._GetVarInfo(VarName,MatchCase=False)
                if len(L)==1:
                    print(level*'                  |'+'$'+VarName+' ({}:{})'.format(L[0]['Package'],L[0]['Group']))
    

    def PrintAssignedVars(self,FortranObject,level):
        if FortranObject is not None and FortranObject['AssignedNonLocalVars'] is not None:
            FortranObject['AssignedNonLocalVars'].sort()
            for VarName in FortranObject['AssignedNonLocalVars']:
                L=self.Doc._GetVarInfo(VarName,MatchCase=False)
                if len(L)==1:
                    print(level*'                  |'+'*'+VarName+' ({}:{})'.format(L[0]['Package'],L[0]['Group']))
    
    
    def PrintCallTree(self,EntryPoint=[],level=0,ShowVariable=True,ShowArgs=True):
        FortranObject=self.GetParentFortranObject(EntryPoint)
        if ShowVariable:
            self.PrintAssignedArgs(FortranObject,level)
            self.PrintAssignedVars(FortranObject,level)
        if FortranObject is not None:
            for CallName in FortranObject['Call'].keys():
                if CallName not in self.IgnoreCall:
                    print(level*'                  |'+'--> call:{}'.format(CallName))
                    for ListVar in FortranObject['Call'][CallName]:
                        if ShowArgs:
                            print(level*'                  |'+'    args:{}'.format(ListVar))    
                    level=level+1
                    #print('Printing:',FortranObject['Name'],':',CallName)
                    self.PrintCallTree(FortranObject['CallObject'][CallName],level,ShowVariable,ShowArgs)
                    level=level-1
        if FortranObject is not None:    
            for ExternalName in FortranObject['External']:
                if ExternalName not in self.IgnoreExternal:
                    print(level*'                  |'+'--> exte:'+ExternalName)
                    level=level+1
                    self.PrintCallTree(FortranObject['ExternalObject'][ExternalName],level,ShowVariable,ShowArgs)
                    level=level-1
        if FortranObject is not None:        
            for FunctionName in FortranObject['Function']:
                if FunctionName not in self.IgnoreFunction:
                    print(level*'                  |'+'--> Func:'+FunctionName)
                    level=level+1
                    self.PrintCallTree(FortranObject['FunctionObject'][FunctionName],level,ShowVariable,ShowArgs)
                    level=level-1

class UBoxFortranTreeExplorer(UBoxPrintFortranTree):
    def __init__(self,Verbose=False):
        self.Verbose=Verbose
        self.DicAssigned={'AssignedVars':[],'Use':[]}
        self.ListPkgVar=[]

        self.IgnoreCall=[]
        self.IgnoreExternal=[]
        self.IgnoreFunction=[]
        self.IgnoreVariable=[]
        
    def CleanUpAssignedDic(self):
        self.DicAssigned['Use'] = list(dict.fromkeys(self.DicAssigned['Use']))
        self.DicAssigned['AssignedVars'] = list(dict.fromkeys(self.DicAssigned['AssignedVars']))
        for VarName in self.IgnoreVariable:
            if VarName in self.DicAssigned['AssignedVars']:
                self.DicAssigned['AssignedVars'].remove(VarName)
        self.DicAssigned['Use'].sort()
        self.DicAssigned['AssignedVars'].sort()
        
    def GetParentFortranObject(self,EntryPoint:list=[]):
        
        if type(EntryPoint)==list:
            Obj=self.DicFortranObject
            for L in EntryPoint:
                Obj=Obj.get(L)
                if Obj is None:
                    raise ValueError('Cannot get the entry {} in FortranObject dictionary'.format(L))
        else:
            Obj=EntryPoint
        return Obj
    
    def Explore(self,EntryPoint=[],IgnoreCall=None,IgnoreExternal=None,IgnoreFunction=None,IgnoreVariable=None):
         if IgnoreCall is not None:
             self.IgnoreCall=self.IgnoreCall+IgnoreCall
         if IgnoreExternal is not None:
            self.IgnoreExternal=IgnoreExternal
         if IgnoreFunction is not None:
             self.IgnoreFunction=IgnoreFunction
         if IgnoreVariable is not None: 
             self.IgnoreVariable=IgnoreVariable
         
         ParentFortranObject=self.GetParentFortranObject(EntryPoint)
         if self.Verbose:
             print('ParentFortranObject[CallObject]:',ParentFortranObject['CallObject'].keys())
         for CallName,CallObject in ParentFortranObject['CallObject'].items():
             if CallName not in self.IgnoreCall:
                 if self.Verbose:
                     print('Looking for non-local variables into call to:', CallName)
            #                     #collect non-local assigned variable           
                 self.DicAssigned['AssignedVars'].extend(CallObject['AssignedNonLocalVars'])
                 self.DicAssigned['Use'].extend(CallObject['Use'])
                 self.Explore(CallObject)
                 
         for FunctionName,FunctionObject in ParentFortranObject['FunctionObject'].items():
             if FunctionName not in self.IgnoreFunction:
                 if self.Verbose:
                     print('Looking for non-local variables into function:', FunctionName)
            #                     #collect non-local assigned variable           
                     self.DicAssigned['AssignedVars'].extend(FunctionObject['AssignedNonLocalVars'])
                     self.DicAssigned['Use'].extend(FunctionObject['Use'])
                     self.Explore(FunctionObject)
         
         for ExternalName,ExternalObject in ParentFortranObject['ExternalObject'].items():
             if ExternalName not in self.IgnoreExternal:
                 if self.Verbose:
                     print('Looking for non-local variables into External:', ExternalName)
            #                     #collect non-local assigned variable           
                 self.DicAssigned['AssignedVars'].extend(ExternalObject['AssignedNonLocalVars'])
                 self.DicAssigned['Use'].extend(ExternalObject['Use'])
                 self.Explore(ExternalObject)
                     
    def WriteListAssignedVars(self,FileName,ExcludeList=[],AdditionalVariables=[],RaiseError=False):               
        f= open(FileName,"w")
        count=1
        ListVar=[V for V in self.DicAssigned['AssignedVars'] if V not in ExcludeList]
        for VarName in ListVar:
            VarDoc=self.Doc._GetVarInfo(VarName,MatchCase=False)
            if len(VarDoc)<1:
                if RaiseError:
                    raise ValueError('Cannot find variable {} in Doc'.format(VarName))
                else:
                    print('Cannot find variable {} in Doc'.format(VarName))
                continue
            elif len(VarDoc)>1:
                 raise ValueError('Variable {} found twice in Doc'.format(VarName))
            else:
                VarDoc=VarDoc[0]
                Pkg=VarDoc['Package']
            print("{}: {} ({})".format(count,VarName,VarDoc['Package']))
            if Pkg not in self.ListPkgVar:
                self.ListPkgVar.append(Pkg)
            f.write('{}\n'.format(VarName))
            count=count+1
        for VarName in AdditionalVariables:
            f.write('{}\n'.format(VarName))
            count=count+1
        f.close()
        print('List Package:',self.ListPkgVar)
        print('Number of variables:',count-1)
        
