
from UEDGEToolBox.Utils.Misc import GetListPackage,QueryYesNo,ClassInstanceMethod 

# try:
#     #from UEDGEToolBox.Launcher import Doc
# except:

def GetDefaultDataSet()->dict:
        """
        Return defaults datasets.
        
        Return:
        ------
            DefaultDataSet (dict): dictionary of dataset.

        """
        DefaultDataSet={}
        DefaultDataSet['plasmavars']=['te','ti','phi','ng','up','tg','ni']
        DefaultDataSet['plasmavarss']=[V+'s' for V in DefaultDataSet['plasmavars']]
        DefaultDataSet['grid']=['nisp','ngsp','rm','zm','nx','ny','iysptrx','psi','psinormc','simagxs','sibdrys']
        DefaultDataSet['run']=['dtreal','dt_tot','ftol_dt','GridFileName','minu','ziin','znuclin','itermx','incpset','mfnksol']
        DefaultDataSet['regular']=DefaultDataSet['plasmavars']+DefaultDataSet['plasmavarss']+DefaultDataSet['run']+DefaultDataSet['grid']
        DefaultDataSet['plasma']=DefaultDataSet['plasmavars']+DefaultDataSet['plasmavarss']

        return  DefaultDataSet

    
class UBoxDataFilter():
    """Utility class to handle construction of list of variables."""
    
    @ClassInstanceMethod   
    def CollectUEDGEDataSet(self,DataSet=None,ExtraVars:list=[])->dict:
        return self.CollectDataSet(DataSet,DataType='UEDGE',ExtraVars=ExtraVars)['UEDGE']
    
    @ClassInstanceMethod   
    def CollectDataSet(self,DataSet=None,DataType='UEDGE',ExtraVars:list=[],RemovePackage=False)->dict:
        """
        Get a list of variable names from a data set/or and a list of variable name and return a dictionary with variable names as keys and variable values as values.  

        Args:
            DataSetName (str or None, optional): Name of a data set.
            ExtraVars (list(str), optional): List of variable names.

        Return:
            dict: dictionary dict[variable name]=variable value.

        """
        if type(DataType)!=str:
            raise ValueError('DataType must be a string')

        VarList=self.MakeVarList(DataSet,ExtraVars)
        Data=self.CollectData(VarList,DataType,RemovePackage)
        return {DataType:Data}
    
    @ClassInstanceMethod
    def CollectData(self,VarList:str or list,DataType='UEDGE',RemovePackage=False):
        if type(VarList)!=list:
            VarList=[VarList]
        
        VarList=[self.AddPackage(V,DataType) for V in VarList]
        if self.Verbose: print("Varlist to be collected:",VarList)
        
        if DataType=='UEDGE':
            Data=self.UEDGEDataToDict(VarList,RemovePackage=RemovePackage,Verbose=self.Verbose)
        else:
            Data=self.StoredDataToDict(VarList,DataType,RemovePackage=RemovePackage,Verbose=self.Verbose)
        return Data
    
    @ClassInstanceMethod
    def MakeVarList(self,DataSet:str or None or list or tuple=None,ExtraVars:list=[]):
        """
        Return a list of variable names from a dataset and/or a tuple of variable names or a list of dataset/tuple.
        
        Warning: Tuple cannot contain only one element when created. To create tuple of length 1, type: tuple(1,)
        Example:
            >>> UBoxIO.MakeVarList(['grid'])
            ['iysptrx', 'ngsp', 'nisp', 'nx', 'ny', 'rm', 'zm']
            
            >>> UBoxIO.MakeVarList(('te','ti'))
            ['te', 'ti']
            
            >>> UBoxIO.MakeVarList(['grid',('SpecialField',)])
            ['SpecialField', 'iysptrx', 'ngsp', 'nisp', 'nx', 'ny', 'rm', 'zm']
        
        Args:
            DataSetName (str, optional): Name of a data set. Defaults to None.
            ExtraVars (list(str), optional): List of variable names. Defaults to [].

        Returns:
            List (TYPE): DESCRIPTION.

        """
    
        List=ExtraVars.copy()
        if DataSet is None:
            List.extend(self.GetDataSet(DataSet))
        elif type(DataSet)==tuple:
                List.extend([v for v in DataSet])
        else:
                if type(DataSet)==str:
                    DataSet=[DataSet]
                if type(DataSet)==list:
                    for Set in DataSet:
                        if type(Set)==tuple:
                            List.extend(list(Set))
                        else:
                            List.extend(self.GetDataSet(Set))
                
                if type(DataSet)==tuple:
                          List.extend(list(DataSet))                      
        List=list(dict.fromkeys(List))
        List.sort()
        if self.Verbose: print('Output MakeVarList for DataSet "{}" : {} with ExtraVars:{}'.format(DataSet,List,ExtraVars))
        return List
    
    @ClassInstanceMethod 
    def SetDoc(self):
        from UEDGEToolBox.Utils.Doc import UBoxDoc
        if not hasattr(self,'Doc') or self.Doc is None:
                 self.Doc=UBoxDoc()
                 
    @staticmethod
    def SplitVarName(VarName):
        Str=VarName.split('.')
        if len(Str)>1:
            return tuple(Str)
        else:
            return (None,Str)
        
    @ClassInstanceMethod    
    def FindPackage(self,VarName:str,SearchUEDGEPackage=True)->str:
        Str=VarName.split('.')
        if len(Str)>1:
            return Str[0]
        elif SearchUEDGEPackage:
            self.SetDoc()
            DicVar=self.Doc.Search(VarName,Exact=True,Silent=True)
            if len(DicVar)>1:
                raise ValueError('More than one package found for {}'.format(VarName))
            if len(DicVar)<1:
                return None
            return DicVar[0]['Package']
        else:
            return None
        
   
    
    
    @ClassInstanceMethod    
    def SelectData(self,Data:dict,DataSet=None,DataType='UEDGE')->dict:
        """Return a subset of a dictionary with keys set by a loader."""

        if DataType=='' or DataType is None:
            D=Data
        else:
            D=Data.get(DataType)
            
            
        
        
        if D is not None and type(D)==dict: # Check if a DataType entry is present and if it is a dictionary and get variables with a packagename 
            DataOut=dict((k,v) for (k,v) in D.items() if type(v)!=dict)
        else:
            DataOut=dict((k,v) for (k,v) in Data.items() if type(v)!=dict)
            
        ListUEDGEPkg=GetListPackage()
        
        if DataSet=='all':
            VarList=list(DataOut.keys())
        else:
            VarList=self.MakeVarList(DataSet)
        
        VarList=self.AddPackage(VarList,DataType)    
        if DataType=='UEDGE':
             DataOut=dict((self.AddPackage(k,DataType),v) for (k,v) in DataOut.items() if self.FindPackage(k) in ListUEDGEPkg and k in VarList)
        else:
             DataOut=dict((self.AddPackage(k,DataType),v) for (k,v) in DataOut.items() if k in VarList)
        
        return DataOut

    
    @staticmethod
    def RemovePkg(VarName:str)->str:
        """Return variable name without object prefix.
        
        Example:
            >>> RemovePkg('bbb.te')
            'te'
        """            
        if len(VarName.split('.'))>1:
            return VarName.split('.')[1]
        else:
            return VarName
        
    @ClassInstanceMethod  
    def AddPackage(self,VarName,DataType='UEDGE'):
        """Add the name of a package/object to a variable name if no package/object is present.
        
        Example:
            >>> AddPackage('te',DataType='UEDGE')
           'bbb.te'
           
           >>> AddPackage('te',DataType='DataStore')
           'DataStore.te'
           
           >>> AddPackage('ccc.te')
           'ccc.te'
        """
        if type(VarName)==list:
            return [self.AddPackage(V,DataType) for V in VarName]
        else:
            if VarName.count('.')>0:
                return VarName
            if DataType=='' or DataType is None:
                return VarName
            elif DataType=='UEDGE':
                return self.AddUEDGEPackage(VarName)
            elif DataType!='':
                return '{}.{}'.format(DataType,VarName)
        
        
    @ClassInstanceMethod                      
    def AddUEDGEPackage(self,VarName:str or list,Verbose:bool=False)->list:
        """
        Add UEDGE package in front variable names when variable is part of an UEDGE pakage.
            
        Example:
            >>> ProcessVarList('ne')
            'bbb.ne'
            
        Returns
        -------
            list: DESCRIPTION.

        """  
        
        Pkg=self.FindPackage(VarName,SearchUEDGEPackage=True)
        if Pkg is not None:
                return "{}.{}".format(Pkg,VarName)
        else:
            return VarName
    
    @ClassInstanceMethod
    def StoredDataToDict(self,VarList:list,DataType:str,RemovePackage=False)->dict:
        if DataType=='':
            raise ValueError('DataType cannot be an empty string ...')
        if hasattr(self,DataType) and type(getattr(self,DataType))==dict:
            if RemovePackage:
                Data=dict((K,V) for (K,V) in getattr(self,DataType).items() if self.AddPackage(K,DataType) in VarList)
            else:
                Data=dict((DataType+'.'+K,V) for (K,V) in getattr(self,DataType).items() if self.AddPackage(K,DataType) in VarList)
            return Data
        else:
            print('Cannot retrieve dictionary "{}" from current object...'.format(DataType))
            return {}
        
    @staticmethod    
    def UEDGEDataToDict(VarList:list,RemovePackage=False,Verbose=False)->dict:
        """
        Save a list of UEDGE and regular variables into a dictionary (e.g. VarList=['ne'] -> Dic['ne']=bbb.ne).
    
        Args:
            DataSetName (str or None, optional): DESCRIPTION. Defaults to None.
            ExtraVars (list(str), optional): DESCRIPTION. Defaults to [].
    
        Returns
        -------
            TYPE: DESCRIPTION.
    
        """
           
        for pkg in GetListPackage():
            exec('from uedge import '+pkg)
        Dic=locals()
        Dic['Data']={} 
        for V in VarList:
            if Verbose:print('Preparing data {}'.format(V))
            if RemovePackage:
                #remove package name : bbb.ne->ne
                if len(V.split('.'))>0 :
                        VV=V.split('.')[1]
                else:
                        VV=V
            else:
                VV=V
            try: 
                if Verbose: print('Executing: ',"Data['{}']={}".format(VV,V))
                exec("Data['{}']={}".format(VV,V),globals(),Dic)
            except Exception as e:
                if Verbose: print('Error:',repr(e))
                print('Unable to collect data "{}" from UEDGE package "{}"'.format(V,VV))
        
        if Dic.get('Data') is None:
            Data={}
        else:
            Data=Dic['Data']        
        
        return Data 


        
class UBoxDataSet(UBoxDataFilter):
    """Class to construct or load a set of UEDGE and python variables."""
    Verbose=False
    _DataSets=GetDefaultDataSet()
    DefaultDataSetName='plasma'
    
    def __init__(self,Verbose=False):
        pass
       
        
    @ClassInstanceMethod    
    def AddDefaultDataSet(self,OverWrite=True):
        DefaultDataSet=GetDefaultDataSet()
        if self.Verbose: print(DefaultDataSet)
        for k,v in DefaultDataSet.items():
            self.AddDataSet(k.lower(),v,OverWrite=True,SaveData=False)
            
    @ClassInstanceMethod        
    def DeleteDataSet(self,Name):
        if self._DataSets.get(Name) is not None:
            self._DataSets.pop(Name)
            print('Data set {} deleted'.format(Name))
            
    @ClassInstanceMethod
    def ShowDataSet(self):
        print('**** Data set available *********')
        for k,v in self._DataSets.items():
            print('{:<20} : {}'.format(k,v))
            
    @ClassInstanceMethod
    def AddDataSet(self,DataSetName:str,ListVariable:list=[],FileName:str or None=None,OverWrite:bool=True,SaveData:bool=True):
        DataSetName=DataSetName.lower()
        if DataSetName=='all' or DataSetName=='none':
            print('Dataset name cannot be "all" or "none"...')
            return
        if self._DataSets.get(DataSetName) is not None:
            if not OverWrite:
                return
            if not QueryYesNo('A dataset named {} already exists. Overwrite it?'.format(DataSetName)):
               print('No dataset created')
               return    
           
        if FileName is not None:
            try:
                with open(FileName,'r') as f:
                    List=list(f.read().splitlines())
                ListVariable.extend(List)
            except:
                pass
        
        if ListVariable==[]:
            print('Cannot create a new dataset. No variable names provided for the dataset.')
            return
        else:
            if self.Verbose:print(DataSetName,ListVariable)
            self._DataSets[DataSetName]=ListVariable
            if SaveData:self.SaveDataSet()
            
    # @ClassInstanceMethod        
    # def GetDataSet(self,DataSetName:str or list):
    #     """
    #     Get the list of variables from a dataset.

    #     Args:
    #         DataSetName (str): DESCRIPTION.

    #     Returns:
    #         TYPE: DESCRIPTION.

    #     """
    #     if type(DataSetName)==str:
    #         DataSetName=[DataSetName]
    #     if type(DataSetName)==tuple:
    #         DataSetName=[DataSetName]
    #     List=[]
    #     for D in DataSetName:   
    #         if type(D)==list:
    #             List.extend(D)
    #         else:
    #             S=self._DataSets.get(D.lower())
    #             if S is not None:
    #                     List.extend(S)
    #             else:
    #                 print('Dataset "{}" is unknow. Have datasets been loaded? '.format(D))
    #     return List
    
    @ClassInstanceMethod        
    def GetDataSet(self,DataSet:str or list,Pkg=None):
        """
        Get the list of variables from a dataset.

        Args:
            DataSetName (str): DESCRIPTION.

        Returns:
            TYPE: DESCRIPTION.

        """ 
        if self.Verbose:
            print('Getting DataSet:',DataSet,type(DataSet))
        if DataSet is None:
            L=self._DataSets.get(self.DefaultDataSetName)
            if L is None:
                L=[]
        if type(DataSet)==tuple:
            L=list(DataSet)
        else:
            L=self._DataSets.get(DataSet.lower())
            if L is None:
                if DataSet!='':
                    print('Dataset "{}" is unknow. Have datasets been loaded? '.format(DataSet))
                    L=[]
                    

        L=self.AddPackage(L,Pkg)
        
        return L
    
    @staticmethod
    def SaveDataSet(self):
        """Dummy method overloaded by an UBoxSettings save method."""
        pass
    
    
