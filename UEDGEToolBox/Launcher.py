"""Launcher for UEDGEToolBox.

An instance "UBox" of  :py:class:`UBoxLauncher`  is created and initialized when :py:mod:`Launcher` is imported. 
The following code snipet is executed when :py:mod:`Launcher` is imported:
    
.. code-block:: python

    >>> UBox=UBoxLaunch()
    >>> from uedge import *
    >>> (Doc)=UBox.Start() 
    >>> CurrentProject=UBox.CurrentProjectGetter
    >>> CreateGlobalAliases(Doc,globals())
    >>> CreateGlobalAliases(UBox,globals())
    >>> UBox.Print('UEDGEToolBox sucessfully launched. Type QuickStart() for basic commands.')
"""
import types
import pkg_resources
from UEDGEToolBox.Utils.Misc import CreateGlobalAliases,GetMethods
from UEDGEToolBox.ProjectManager.Projects import UBoxProjects
from UEDGEToolBox.ProjectManager.Settings import UBoxSettings
from UEDGEToolBox.Utils.Doc import UBoxDoc
from UEDGEToolBox.DataManager.ExtData import UBoxExtData
from UEDGEToolBox.DataManager.Grid import UBoxGrid
from UEDGEToolBox.Simulation.RunSim import UBoxRun
from UEDGEToolBox.Simulation.Sim import UBoxSim
#from UEDGEToolBox.Grid import *
import yaml
try: 
    from uedge import *
except Exception as e:
    print('Cannot load UEDGE... ',repr(e))
    
#@UBoxPrefix
class UBoxLauncher(UBoxProjects,UBoxRun):
    """Class handling the initialization and loading of UEDGEToolBox.
    
    Example:
        >>> UBox=UBoxLauncher()
        >>> UBox.Start()
        
    """
    
    def __init__(self,Dic={},Verbose=False,*args, **kwargs):
        self.Version='n/a'
        self.Doc=None
        self.Dic=Dic
        self.__GetVersion()
        self.__CheckUEDGE()
        self.Verbose=Verbose
 
    
    def Launch(self,CreateAliases=True,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.Doc=UBoxDoc()
        self.Dic['Doc']=self.Doc
        self.Dic['CurrentProject']=self.CurrentProjectGetter
        self.Print('UEDGEToolBox sucessfully launched. Type QuickStart() for basic commands.')
        if CreateAliases:
            CreateGlobalAliases(self.Doc,Verbose=self.Verbose)
            CreateGlobalAliases(self,Include=GetMethods(UBoxSim),Verbose=self.Verbose)
            CreateGlobalAliases(self,Include=['SetCaseName','Source','SourceGrid'],Verbose=self.Verbose)
                               
    def __CheckUEDGE(self):
        try: 
            import uedge
            return True
        except:
            print('UEDGE cannot be loaded. Check that the UEDGE package is correctly installed ... (see     documentation)') 
            return False
        
    def __GetVersion(self):
        try:
            self.Version='{}'.format(pkg_resources.get_distribution('UBox').version)
        except:
            pass

    def AddBoundedMethod(self,Method):
        #if callable(Method):
        MethodName=Method.__name__
        if hasattr(self,MethodName) and not QueryYesNow('Method {} already exists . Overwrite it?'.format(MethodName)):
            return
        
        setattr(self,MethodName,types.MethodType(Method,self))
        print('Bounded method {} added'.format(MethodName))
        
                
yaml.add_representer(UBoxSettings, UBoxLauncher.to_yaml0, Dumper=yaml.SafeDumper)
yaml.add_representer(UBoxLauncher, UBoxLauncher.to_yaml0, Dumper=yaml.SafeDumper)
yaml.add_constructor(UBoxSettings._YAMLTag, UBoxLauncher.from_yaml0, Loader=yaml.SafeLoader) 
UBox=UBoxLauncher()    
#UBox.Launch()
