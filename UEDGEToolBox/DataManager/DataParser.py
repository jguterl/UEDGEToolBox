import numpy as np
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod, SetClassArgs,AddPrintMethod

# @UBoxPreFix()

@AddPrintMethod(4)
class UBoxDataParser():

    Verbose = False

    def __init__(self, Verbose=False):
        self.Verbose = Verbose

    @staticmethod
    def _ParseDataField(DataField: str, Verbose=False) -> (str, list):
        """
        Parse and return a field with dataname and indexes.

        Example:
            >>> ParseDataField('ni[1,4:6]')
            ('ni',[1,[4,5])

            >>> ParseDataField('ni[:]')
            ('ni', [[0, -1]])

        Args:
            DataField (str): Name of the field to be retrieved (e.g. ni, te,ti) with indexes of third dimension between brackets []

        Returns:
            (DataFieldName,DataFieldIndex) (str,list(int)): Name of the field (e.g. te), indexes of third dimensions if any; otherwise None

        """
        # Input data for
        Nb = DataField.count('[') + DataField.count(']')
        Np = DataField.count('(') + DataField.count(')')
        if Nb > 0 and Np > 0:
            print('Cannot combine () and [] in field name: {}'.format(DataField))
            return ('', [])
        from pyparsing import nestedExpr
        if Nb > 0:
            Bracket = ['[', ']']
        elif Np > 0:
            Bracket = ['(', ')']
        if Np == 0 and Nb == 0:
            return (DataField, [])

        if DataField.count('[') != DataField.count(']'):
            print('# of [ != # of ] in {}'.format(DataField))
            return ('', [])

        S = DataField.split(Bracket[0], 1)
        if Np > 0:
            Offset = -1
        else:
            Offset = 0

        Name = S[0]
        if Name == '':
            print('No field provided in {} ...'.format(DataField))
            return ('', [])
        if Verbose:
            print('Bracket:', Bracket, 'Name:', Name)
        if len(S) < 2:
            Index = []
        else:
            S = '[' + S[1]
            Index = []
            if Verbose:
                print('Parsing S:', S)
            Sb = nestedExpr('[', ']').parseString(S).asList()[0]
            for sb in Sb:
                if type(sb) == str:
                    S = sb.split(',')
                    for s in S:
                        if s == '':
                            continue
                        if s.count(':') > 0:
                            s1 = s.split(':')[0]
                            if s1 == '':
                                s1 = 0
                            s2 = s.split(':')[1]
                            if s2 == '' or s2 == '-1':
                                s2 = '-1'
                                Index.append([int(s1) + Offset, int(s2)])
                            else:
                                Index.append(np.array(range(int(s1) + Offset, int(s2) + Offset)).tolist())
                        else:
                            Index.append(int(s) + Offset)

                elif type(sb) == list:
                    S = sb[0].split(',')
                    ILocal = []
                    for s in S:
                        if s == '':
                            continue
                        if s.count(':') > 0:
                            s1 = s.split(':')[0]
                            if s1 == '':
                                s1 = 0
                            s2 = s.split(':')[1]
                            if s2 == '' or s2 == '-1':
                                s2 = '-1'
                                ILocal.extend([int(s1) + Offset, int(s2)])
                            else:
                                ILocal.extend(np.array(range(int(s1) + Offset, int(s2) + Offset)).tolist())
                        else:
                            ILocal.append(int(s) + Offset)
                    Index.append(ILocal)

        if Verbose:
            print('ParsingDataField: Name:{}; IndexSet:{}'.format(Name, Index))
        return (Name, Index)

    @staticmethod
    def _ProcessIndex(Shape: int, Index: list):

        Idx = Index.copy()
        for i, I in enumerate(Idx):
            if I == -1 and len(Idx) > 1:
                Start = Idx[i - 1]
                Idx.pop(i)
                if Start > Shape:
                    return ValueError('Start>Shape')
                Idx.extend(range(Start, Shape))
            elif I == -1:
                Idx[0] = Shape - 1
        Idx = list(dict.fromkeys(Idx))
        return np.array(Idx)

    @ClassInstanceMethod
    def GetIndexes(self, DataShape: tuple, IndexSet: list):
        """Return an list of numpy arrays of indexes for each dimension.

        Example
        -------
            >>> GetIndexes((10,10,),[[0, -1], [3, 4]])
            [array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), array([3, 4])]

        """
        Indexes = []
        for i, S in enumerate(DataShape):
            Indexes.append(np.arange(0, DataShape[i]))

        if len(IndexSet) != len(DataShape):
            print('Dim of data shape =! dim of index list in input of GetIndexes')
            return Indexes
        else:
            for i, I in enumerate(IndexSet):
                if type(I) != list:
                    I = [I]
                if I != []:
                    Indexes[i] = self._ProcessIndex(DataShape[i], I)

        return Indexes

    @ClassInstanceMethod
    def ProcessArrayIndexes(self, DataShape: tuple, IndexSet: list or int or range = []):
        """Return numpy arrays or indexes from a given set of indexes (IndexSet).

        If no IndexSet provided, return arrays of all indexes defined by DataShape.

        When len(DataShape)<=2 (1D or 2D array), len(Index) must be equal to len(DataShape).
        When len(DataShape)>2 (3D or 4D array), len(Index) must be equal to len(DataShape) or len(Index)+1<len(DataShape).
        When len(DataShape)>2 and len(Index)+1<len(DataShape), first two missing dimensions are added to IndexSet (third example).

        Example:
            >>> ProcessArrayIndexes((6,6))
            [array([0, 1, 2, 3, 4, 5]), array([0, 1, 2, 3, 4, 5])]

            >>> ProcessArrayIndexes((10,8,12),[[1,2],[0, -1], [3, 4]])
            [array([1, 2]), array([0, 1, 2, 3, 4, 5, 6, 7]), array([3, 4])]

            >>> ProcessArrayIndexes((6,6,5),[[3, 4]])
            [array([0, 1, 2, 3, 4, 5]), array([0, 1, 2, 3, 4, 5]), array([3, 4])]


            >>> ProcessArrayIndexes((6,6),[[3, 4]])
            Mismatch in DataShape and IndexSet: (6, 6) vs [[3, 4]]

        """
        Indexes = []
        for S in DataShape:
            Indexes.append(np.arange(0, S))

        if len(IndexSet) == 0:
            return Indexes
        if len(DataShape) < len(IndexSet):
            raise ValueError('len(DataShape)< len(IndexSet): {} vs {}'.format(DataShape, IndexSet))

        if len(DataShape) < 3:
            if len(DataShape) != len(IndexSet):
                raise ValueError('Mismatch in DataShape and IndexSet: {} vs {}'.format(DataShape, IndexSet))
            else:
                AddIndexes = self.GetIndexes(DataShape, IndexSet)
                if self.Verbose:
                    print('AddIndex:', AddIndexes)
                return AddIndexes

        else:
            # when dimension >2, assume that first two dimensions are not given when len(IndexSet)<len(DataShape)
            if len(DataShape) > len(IndexSet) + 1:
                while len(IndexSet) < len(DataShape):
                    IndexSet.insert(0, [])

            if len(DataShape) != len(IndexSet):
                raise ValueError('Mismatch in DataShape and IndexSet: {} vs {}'.format(DataShape, IndexSet))
            else:
                AddIndexes = self.GetIndexes(DataShape, IndexSet)
                if self.Verbose:
                    print('AddIndex:', AddIndexes)
                return AddIndexes

    @staticmethod
    def _ConcatSliceIndexes(Indexes: list, IdxSlice: np.array or list, DimSlice: int):

        if type(IdxSlice) == int:
            IdxSlice = [IdxSlice]

        if type(IdxSlice) == list or type(IdxSlice) == range:
            IdxSlice = np.array(IdxSlice)

        if type(IdxSlice) == np.ndarray:
            for i in range(0, len(IdxSlice)):
                if IdxSlice[i] < 0:
                    IdxSlice[i] = Indexes[DimSlice][IdxSlice[i]]

        if type(IdxSlice) == tuple:
            IdxSlice = list(IdxSlice)
            for i in range(0, len(IdxSlice)):
                if IdxSlice[i] < 0:
                    IdxSlice[i] = Indexes[DimSlice][IdxSlice[i]]

            if len(IdxSlice) == 2:
                IdxSlice = np.arange(IdxSlice[0], IdxSlice[1])
            elif len(IdxSlice) == 3:
                IdxSlice = np.arange(IdxSlice[0], IdxSlice[1], IdxSlice[2])
            else:
                raise ValueError('IdxSlice given as tuple must contain 2 or 3 elements corresponding to np.arange(IdxSlice[0],IdxSlice[1],IdxSlice[2]). If IdxSlice[i]<0, then IdxSlice[i]=Indexes[DimSlice][IdxSlice[i]]')

        if DimSlice is None or IdxSlice is None or IdxSlice.size == 0:
            return Indexes

        if len(Indexes) < DimSlice:
            raise IOError('DimSlice cannot exceed dimension of Indexes: {}>{}.'.format(DimSlice, len(Indexes.shape)))

        Ind = Indexes.copy()

        Ind[DimSlice] = np.intersect1d(Indexes[DimSlice], IdxSlice)
        return Ind

    @staticmethod
    def _CheckArrayIndex(DataShape: tuple, Indexes: list):

        for i, (S, I) in enumerate(zip(DataShape, Indexes)):
            if I.size != 0 and I.max() > S - 1:
                return 'Out of bound index for dimension {}: {} > 0:{}'.format(i, I.max(), S - 1)
            if I.size != 0 and I.min() < 0:
                return 'Out of bound index for dimension {}: {} < {}'.format(i, I.max(), 0)
        return True

    @staticmethod
    def _SliceDataArray(DataArray, Indexes):
        if Indexes is None or Indexes == []:
            return DataArray

        DataOut = DataArray.copy()
        # only implemented for three-dimensional arrays!
        OffsetDim = 0
        for i, Idx in enumerate(Indexes):
            if Idx.size > 0:
                DataOut = np.take(DataOut, Idx, axis=i + OffsetDim)
                if Idx.size == 1 and len(DataOut.shape) < len(DataArray.shape):  # prevent axis out of bound when Dataout is squeeze
                    OffsetDim = OffsetDim - 1
            else:
                return np.array([])
        return DataOut

    @staticmethod
    def _SplitDataArray(DataArray, Dim):
        if Dim is None or Dim > len(DataArray.shape) - 1 or Dim < 0:
            return [DataArray]
        else:
            DataOut = []
            for Idx in range(0, DataArray.shape[Dim]):
                DataOut.append(np.take(DataArray, Idx, axis=Dim))
            return DataOut

    @staticmethod
    def _SplitIndexes(Indexes, Dim):
        if Dim is None or Dim > len(Indexes) - 1 or Dim < 0:
            return [Indexes]
        else:

            IndexesOut = []
            for i in range(0, Indexes[Dim].size):
                IndexesCopy = Indexes.copy()
                IndexesCopy[Dim] = np.array(Indexes[Dim][i])
                IndexesOut.append(IndexesCopy)

            return IndexesOut

            # L=[]
            # if Indexes[Dim].size<2:
            #     return [Indexes[Dim]]
            # for D in Indexes[Dim]:
            #     if Dim<len(Index)-1:
            #         L.append(Index[0:Dim]+[np.array([D])]+Index[Dim+1:len(Index)])
            #     else:
            #         L.append(Index[0:Dim]+[np.array([D])])
            # return L

    @ClassInstanceMethod
    def GetDataFieldNames(self, DataFields: list) -> list:
        L = []
        for F in DataFields:
            (Field, IndexSet) = self._ParseDataField(F, self.Verbose)
            L.append(Field)
        return L

    @ClassInstanceMethod
    def ProcessDataArray(self, DataArray, Indexes=[], IdxSlice=None, DimSlice=None, DimSplit=None) -> (list, list):
        self.PrintVerbose('Processing Data arrays: IdxSlice:{} DimSlice:{}'.format(IdxSlice, DimSlice))
        if Indexes == []:
            Indexes = self.ProcessArrayIndexes(DataArray.shape, [])

        (DataArray, Indexes) = self.SliceDataArray(DataArray, Indexes, IdxSlice, DimSlice)
        (DataArray, Indexes) = self.SplitDataArray(DataArray, Indexes, DimSplit)
        return (DataArray, Indexes)

    @ClassInstanceMethod
    def SliceDataArray(self, DataArray, Indexes, IdxSlice=None, DimSlice=None) -> (list, list):

        Shape = DataArray.shape
        # process data array

        self.PrintVerbose('SliceDataArray: IdxSlice:{},DimSlice:{}'.format(IdxSlice, DimSlice))

        if type(DimSlice) != list:
            DimSlice = [DimSlice]
            IdxSlice = [IdxSlice]

        if len(DimSlice) != len(IdxSlice):
            raise IOError('IdxSlice and DimSlice must have the same length')

        for D, I in zip(DimSlice, IdxSlice):
            Indexes = self._ConcatSliceIndexes(Indexes, I, D)

        Check = self._CheckArrayIndex(Shape, Indexes)

        if Check != True:
            raise ValueError('{} for data field {} with Indexes={}'.format(Check, Indexes))

        return (self._SliceDataArray(DataArray, Indexes), Indexes)

    @ClassInstanceMethod
    def SplitDataArray(self, DataArray, Indexes, DimSplit=None) -> (list, list):
        return(self._SplitDataArray(DataArray, DimSplit), self._SplitIndexes(Indexes, DimSplit))

    @ClassInstanceMethod
    def ParseDataFields(self, DataFields: list or str, IdxSlice=None, DimSlice=None, DimSplit=2, EnforceDataExist=False, DataType: dict or str or None = 'UEDGE', **kwargs):
        """


        Args:
            Data (dict): dictionary of data.
            DataFields (list): Field names for data (entries).
            IdxSlice (list, optional): DESCRIPTION. Defaults to [].
            DimSplit (list, optional): DESCRIPTION. Defaults to [2].

        Returns:
            Data (TYPE): Dictionary of data extracted from original data dictionary.
            Indexes (TYPE): Indexes of .
            OriginalShape (TYPE): DESCRIPTION.

        """
        assert type(DataFields) == list or type(DataFields) == str, "DataFields must be a string or list"
        assert type(DataType) == list or type(DataType) == str or type(DataType) == dict, "DataType must be a string or list or a dict"

        # Convert DataFields to a list
        if type(DataFields) == str:
            DataFields = [DataFields]

        # If DataType is not a list, then make it a list with the same number of elements than DataFields
        if type(DataType) != list:
            V = DataType
            DataType = [V for D in DataFields]

        self.PrintVerbose('Parsing DataFields: DataFields={}\nIdxSlice={}; DimSlice:{}; DimSplit:{}; DataType:{}'\
                  .format( DataFields, IdxSlice, DimSlice,  DimSplit,DataType))

        assert len(DataType) == len(DataFields), 'DataType must be either a string or have the same number of entries than DataFields'

        Fields = []
        IndexSets = []
        for F in DataFields:
            (Field, IndexSet) = self._ParseDataField(F, self.Verbose)
            Fields.append(Field)
            if Fields.count(Field) > 1:
                raise IOError("Duplicate of the field '{}' found. Field names must be unique in DataFields.".format(Field))
            IndexSets.append(IndexSet)

        DicOut = {}
        for Field, IndexSet, Data in zip(Fields, IndexSets, DataType):
            DicOut.update(self.ParseArray(Field, Data, IndexSet, IdxSlice, DimSlice, DimSplit))

        return DicOut

    @ClassInstanceMethod
    def ParseArray(self, Field, DataType, IndexSet, IdxSl, DimSl, DimSp):
        DicOut = {}
        self.PrintVerbose('Parse Array: Processing field "{}" with IndexSet:"{}" DataType:"{}" IdxSl:{} DimSl:{}'.format(Field, IndexSet, DataType, IdxSl, DimSl))

        if type(DataType) == dict:
            DataArray = DataType.get(Field)
        else:
            if hasattr(self, 'GetDataField'):
                DataArray = self.GetDataField(Field, DataType)
            else:
                DataArray = None

        if DataArray is None:
            print('Cannot find the field {} in the data dictionary "{}"'.format(Field, DataType))
            DicOut[Field] = {'Data': None, 'Indexes': None, 'OriginalShape': None, 'Label': Field}
            return DicOut

        self.PrintVerbose('Field:"{}" type:"{}"'.format(Field, type(DataArray)))

        if not isinstance(DataArray, np.ndarray):
            DicOut[Field] = {'Data': DataArray, 'Indexes': None, 'OriginalShape': None, 'Label': Field}
            return DicOut

        else:
            Shape = DataArray.shape
            Indexes = self.ProcessArrayIndexes(DataArray.shape, IndexSet)
            self.PrintVerbose('Indexes for field "{}" after processing of IndexSet:\n {}'.format(Field, Indexes))
            if DimSp is None or DimSp > len(Indexes) - 1:
                DimSp = None
            (DataArray, Indexes) = self.ProcessDataArray(DataArray, Indexes, IdxSl, DimSl, DimSp)

        if DimSp is None:
            DicOut[Field] = {'Data': DataArray[0], 'Indexes': Indexes[0], 'OriginalShape': Shape, 'Label': Field}
        else:
            for D, I in zip(DataArray, Indexes):
                self.PrintVerbose('Field "{}" I:{}'.format(Field, I))
                Str = '{}__{}'.format(Field, I[DimSp])
                DicOut[Str] = {'Data': D, 'Indexes': I, 'OriginalShape': Shape, 'Label': Str}

        return DicOut

    def RadialSlice(self, DataFields, Iy, DimSplit=2):
        return self.ParseData(DataFields, IdxSlice=Iy, DimSlice=0, DimSplit=DimSplit)

    def PoloidalSlice(self, DataFields, Ix, DimSplit=2):
        return self.ParseData(DataFields, IdxSlice=Ix, DimSlice=1, DimSplit=DimSplit)

        #     (Field,IndexSet)=self._ParseDataField(F,self.Verbose)
        #     if self.Verbose: print('Processing field "{}"->"{}" with index "{}"'.format(F,Field,IndexSet))
        #     DataArray=Data.get(Field)
        #         Shape=DataArray.shape
        #         #process data array

        #     if Data.get(Field) is not None:
        # OriginalShape={}
        # for D,I in zip(Dim,Idx):
        #     print('Process:',np.array(I).tolist())
        #     (Data,Indexes,OriginalShape)=UBoxDataProcess(Verbose).ExtractData(Data,DataFields,I,D,OriginalShape)
        #     DataFields=list(Data.keys())

        # return Data,Indexes,OriginalShape