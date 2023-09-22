#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 10:42:39 2020

@author: jguterl
"""
from UEDGEToolBox.Utils.Misc import SetClassArgs, ClassInstanceMethod, AddPrintMethod
from UEDGEToolBox.Plot.Plot import UBoxPlot
from UEDGEToolBox.DataManager.IO import UBoxIO
from UEDGEToolBox.DataManager.Interpolate import UBoxInterpolate
from UEDGEToolBox.DataManager.Grid import UBoxGrid
from UEDGEToolBox.ProjectManager.Source import UBoxSource
import glob

# @UBoxPreFix()

@AddPrintMethod(0)
class UBoxExtData(UBoxSource, UBoxPlot, UBoxInterpolate):  # ,UBoxPlot):
    """Class managing loading of UEDGE data saved in files."""
    Verbose = False
    Project = None
    CaseName = None
    FileName = None
    GridFileName = None
    Folder = 'SaveDir'
    Data = {}
    Grid = {}

    @SetClassArgs
    def __init__(self, Data: str or None = None, CaseName: str or None = None, Project: str or None = None, Folder: str = 'SaveDir', Grid=None, DataSet=['all'], DataType=['UEDGE'], Verbose=False, *args, **kwargs):
        self.Verbose = Verbose
        self.Project = Project
        self.CaseName = CaseName
        if type(Data) == str:
            self.FileName = Data
        else:
            self.FileName = None
        if type(Data) == dict:
            self.Data = Data
        else:
            self.Data = {}

        self.GridFileName = Grid
        self.Folder = Folder

        self.Tag = {}
        self.CorrectTemp = 1.602176634e-19

        if self.FileName is not None:
            self.Load(self.FileName, DataSet, DataType)

        self.LoadGrid(Grid)

    @ClassInstanceMethod
    def Load(self, FileName=None, DataSet=['all'], DataType=['UEDGE']):
        """
        Load data from a UEDGE data file.
        If no filename is provided, build a filename from object attribute with source.

        Args:
            FileName (TYPE, optional): FileName. Defaults to None.
            LoadList (TYPE, optional): DESCRIPTION. Defaults to [].

        Returns:
            None.

        """

        if FileName is None and self.FileName is None:
            print("No file name given and no file name set in the instance. Cannot load file...")
            return
        else:
            FileName = self.FileName

        self.FileName = self.Source(FileName, self.CaseName, self.Folder, self.Project, EnforceExistence=False)

        if self.Verbose:
            print('Loading ext data from file:{}'.format(self.FileName))
        (self.Data, self.Tag) = self.LoadData(self.FileName)
        L = self.ImportData(self.Data, DataSet, DataType, EnforceDim=False, PrintStatus=self.Verbose, ReturnList=True, ExtData=True)
        print(L)
        
    @ClassInstanceMethod
    def Batch(self, FilePattern, Every=1, **kwargs):
       UData=[]  
       FileList=glob.glob(FilePattern)
       FileList.sort()
       if len(FileList)>0:
           for i in range(0,len(FileList),Every):
               F=FileList[i]
               try:
                   UData.append(UBoxExtData(F, **kwargs))
                   print('Loading {} ... Success'.format(F))
               except:
                   print('Loading {} ... Fail'.format(F))
       return UData
        
        
        


    @ClassInstanceMethod
    def GetData(self, Field: str, DicAttr: str = 'DataUEDGE', CorrectTempUnit=True):
        """Get data values from data dictionary stored in the instance."""
        self.PrintVerbose('Getting data field {} from DicAttr:{}'.format(Field, DicAttr))
        if hasattr(self, DicAttr) and type(getattr(self, DicAttr)) == dict:
            Out = getattr(self, DicAttr).get(Field)
            if Out is not None and Out.size == 1 and Out.dtype.char == 'S':
                Out = Out[0].decode().strip()
            F = Field.lower()
            if Field.count('.') > 0:
                F = F.split('.')[1]
            if Out is not None and CorrectTempUnit and any([F == L for L in ['tes', 'tis', 'tgs', 'te', 'ti', 'tg']]):
                Out = Out / self.CorrectTemp

            return Out
        else:
            return None

    @ClassInstanceMethod
    def GetDataField(self, Field: str or list, DataType: str = 'UEDGE'):
        """Get data values from data dictionary stored in the instance."""
        if DataType == 'UEDGE' or DataType is None:
            DataType = 'DataUEDGE'

        if type(Field) == str:
            return self.GetData(Field, DataType)
        elif type(Field) == list:
            return [self.GetData(k, DataType) for k in Field]
        else:
            raise IOError('Field must be a string or a list of strings')

    @ClassInstanceMethod
    def GetGridField(self, Field: str):
        """Get data values from data dictionary stored in the instance."""
        return self.Grid.get(Field.lower())

    @ClassInstanceMethod
    def GetGrid(self) -> dict:
        """Get the grid dictionary from the instance."""
        return self.Grid

    @ClassInstanceMethod
    def SetGrid(self, Grid: dict = None):
        """Load a grid dictionary into class instance grid attribute."""
        if type(Grid) == str:
            self.ImportGrid(Grid)
        elif type(Grid) == dict:
            self.Grid = Grid
        else:
            if hasattr(self, 'DataUEDGE') and type(getattr(self, 'DataUEDGE')) == dict:
                Data = getattr(self, 'DataUEDGE')
                GridDataSet = self.GetDataSet('grid')
                self.Grid = dict((k, v) for k, v in Data.items() if k in GridDataSet)

    @ClassInstanceMethod
    def LoadGrid(self, GridFileName=None):
        if type(GridFileName) == dict:
            self.Grid = GridFileName
        else:
            self.GridFileName = GridFileName

        if self.GridFileName is None:
            self.GetDataField('GridFileName')
            self.GridFileName = self.GetDataField('GridFileName')
        if self.GridFileName is None:
            print('Cannot find a filename for a grid file in instance Data ... Provide a path toward a grid file')
        else:
            self.Print('Importing grid from {} ...'.format(self.GridFileName))
            self.Grid = self.ReadGridFile(self.GridFileName)

    @ClassInstanceMethod
    def GetTagField(self, TagName: str) -> str or None:
        """Return a tag field from tag dictionary loaded in the instance."""
        return self.Tag.get(TagName)

    @ClassInstanceMethod
    def GetTag(self):
        if hasattr(self,'Tag'):
            return self.Tag
        else:
            return {}

    def InterpolateLoad(self, OldData, OldGrid, NewGrid, DataType=None, **kwargs):
        self.Data = self.InterpolateData(OldData, OldGrid, NewGrid, DataType, **kwargs)

        self.SetGrid(NewGrid)

    def ShowData(self):
        for A in dir(self):
            if type(getattr(self, A)) == dict and not A.startswith('_'):
                print('* ', A)
                ShowDic(getattr(self, A), indent=1)


def ShowDic(Dic, indent=0):
    for key, value in Dic.items():
        print(' ' * indent * 5 + '* ' + str(key))
        if isinstance(value, dict):
            ShowDic(value, indent + 1)
        else:
            pass  # print('\t' * (indent+1) + str(value))