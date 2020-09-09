#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: jguterl
"""
import numpy as np


####################################################################################
class UBoxXYZ():
    """Template class for load/save UEDGE data in XYZ format."""
    
    Ext='.XYZ'

    @staticmethod
    def WriteData(FileName:str,DataSave:dict={},Tag:dict={},Verbose=False)->bool:
        """Save Data and Tag dictionaries in XYZ format."""       
        return True
        

    @staticmethod
    def ReadData(FileName:str,Verbose=False)->(dict,dict):
        """Return data and tag dictionaries loaded from a file in hdf5 format."""
        return ({},{}) 
    
    
##################################################################################    
class UBoxNumpy():
    """ Class for load/save UEDGE data in numpy format."""
    
    Ext='.npy'

    @staticmethod
    def WriteData(FileName:str,DataSave:dict={},Tag:dict={},Verbose=False)->bool:
        """
        Save Data and Tag ditionaries in numpy format.

        Args:
            FileName (str): Name of the file where data will be written.
            DataSave (dict, optional): Dictionary containing data which will be saved. Defaults to {}.
            Tag (dict, optional): Dictionary containing user and environment information. Defaults to {}.

        Returns
        -------
            bool: True if data successfully written in file.

        """       
        print('Saving {} datafields in {} ...'.format(len(list(DataSave.keys())),FileName))
        if not DataSave:
            print('No data to save... Skipping')
            return False
        
        
        if not Tag: # check if dictionaary is empty
            HeaderTag=['dummy']
            DataTag=['0']
            
        HeaderTag=list(Tag.keys())
        DataTag=list(Tag.values())    
        HeaderData=list(DataSave.keys())
        Data=list(DataSave.values())

        if Verbose: 
            print('- Header:',HeaderData)
            print('- Header Tag:',HeaderTag)
            print('- Tag Data:',DataTag)
    
        try: 
            np.save(FileName,(HeaderData,HeaderTag,tuple(DataTag),tuple(Data)))
            if Verbose:
                print('Numpy: Data saved in file:',FileName)
            return True
        except Exception as e:
            print('Could not save plasma state in numpy format in {}:'.format(FileName),repr(e))  
            return False

    @staticmethod
    def ReadData(FileName:str,Verbose=False)->(dict,dict):
        """Return data and tag dictionaries loaded from a file in hdf5 format."""
        print('Reading data from {} ...'.format(FileName))
        
        try: 
            Header,HeaderTag,TagData,Data=np.load(FileName,allow_pickle=True)
        except Exception as e:
            raise IOError('Could not load data from numpy file {}:{}'.format(FileName,repr(e)))
        
        if Verbose: print('Data loaded from {}'.format(FileName))
        
        Data=dict((K,V) for (K,V) in zip(Header,Data))
        Tag=dict((K,V) for (K,V) in zip(HeaderTag,TagData))
        
        return (Data,Tag)

##################################################################################          
class UBoxHdf5():
    """Methods to load/save UEDGE data in hdf5 format (suign deepdish)."""
    
    Ext='.h5'
    
    @staticmethod
    def WriteData(FileName:str,DataSave:dict={},Tag:dict={},Verbose=False)->bool:
        """
        Save Data in hdf5 format.
        
        Warning:
            This method does not check the extension of the FileName.
            
        Args:
            FileName (str): Name of the file where data will be written.
            DataSave (dict, optional): Dictionary containing data which will be saved. Defaults to {}.
            Tag (dict, optional): Dictionary containing user and environment information. Defaults to {}.

        Returns
        -------
            bool: True if data successfully written in file.

        """       
        print('Saving {} datafields in {} ...'.format(len(list(DataSave.keys())),FileName))
        if not DataSave:
            print('No data to save... Skipping')
            return False
        
    
        try: 
            deepdish.io.save(FileName,(DataSave,Tag))
            if Verbose:
                print('hdf5: Data saved in file:',FileName)
            return True
        except Exception as e:
            print('Could not save plasma state in numpy format in {}:'.format(FileName),repr(e))  
            return False

    @staticmethod
    def ReadData(FileName:str,Verbose=False)->(dict,dict):
        """
        Load data from a file in hdf5 format.

        Args:
            FileName (str): Name of the file.

        Raises
        ------
            IOError: .

        Returns
        -------
            Data (TYPE): Dictionary .
            Tag (TYPE): DESCRIPTION.
        """
        print('Loading data from {} ...'.format(FileName))
        
        try: 
            (Data,Tag)=np.load(FileName)
        except Exception as e:
            raise IOError('Could not load data from hdf5 file {}:{}'.format(FileName,repr(e)))
        
        if Verbose: print('Data loaded from {}'.format(FileName))
        return (Data,Tag)        