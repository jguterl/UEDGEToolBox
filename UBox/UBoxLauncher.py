# -*- coding: utf-8 -*-


import sys,builtins
import os,sys,builtins,types,inspect
import pkg_resources 
from UBox.UBoxUtils import *
from UBox.UBoxProjects import *
from UBox.UBoxDoc import *
#from contextlib import contextmanager
    
# @contextmanager
# def add_prefix(prefix): 
#     global is_new_line
#     orig_write = sys.stdout.write
#     is_new_line = True
#     def new_write(*args, **kwargs):
#         global is_new_line
#         if args[0] == "\n":
#             is_new_line = True
#         elif is_new_line:
#             orig_write("[" + str(prefix) + "]: ")
#             is_new_line = False
#         orig_write(*args, **kwargs)
#     sys.stdout.write = new_write
#     yield
#     sys.stdout.write = orig_write
@UBoxPrefix
class UBoxLaunch:
    
    def __init__(self):
        self.Version='n/a'
        self.Settings=None
        self.Projects=None
        self.Doc=None
        self.GetVersion()
        self.CheckUEDGE()
           
    
    def Start(self):
        print('Starting UBox version:  {}  '.format(self.Version)) 
        if self.CheckUEDGE():
            print('UEDGE package found ...')
            try:
                self.Settings=UBoxSettings()
            except:
                pass
            try:
                self.Projects=UBoxProjects()
            except:
                pass
            try:
                self.Doc=UBoxDoc()
            except:
                pass
            
        else:
            print('UEDGE package not found. Cannot start UBox. Install UEDGE first...')
        return (self.Settings,self.Projects,self.Doc)
    
    def CheckUEDGE(self):
        try: 
            import uedge
            return True
        except:
            print('UEDGE cannot be loaded. Check that the UEDGE package is correctly installed ... (see     documentation)') 
            return False
        
    def GetVersion(self):
        try:
            self.Version='{}'.format(pkg_resources.get_distribution('UBox').version)
        except:
            pass
            



#from UEDGESimulation import *    

#from UEDGEMisc import *       
#from UEDGEBas2Py import *
#from UEDGEIO import *
#from UEDGEMesh import *


#Defining

UB=UBoxLaunch()
(Settings,Projects,Doc)=UB.Start() 
CreateGlobalAliases(Doc,globals())
#ListObjects=['Settings','Sim']
#print('### UEDGEUBox objects available:{}'.format(ListObjects))