# -*- coding: utf-8 -*-


import sys
from contextlib import contextmanager

@contextmanager
def add_prefix(prefix): 
    global is_new_line
    orig_write = sys.stdout.write
    is_new_line = True
    def new_write(*args, **kwargs):
        global is_new_line
        if args[0] == "\n":
            is_new_line = True
        elif is_new_line:
            orig_write("[" + str(prefix) + "]: ")
            is_new_line = False
        orig_write(*args, **kwargs)
    sys.stdout.write = new_write
    yield
    sys.stdout.write = orig_write

#with add_prefix("UEDGEToolBox"):
try:
    import pkg_resources 
    version='{}'.format(pkg_resources.get_distribution('UEDGEToolBox').version)
except:
    version='n/a'
    
print('Loading UEDGEToolBox version:{}...'.format(version))

print('Loading UEDGE...')
try: 
    from uedge import *
except:
    raise ImportError('UEDGE cannot be loaded. Check that the UEDGE package is correctly installed ... (see documentation)')  
    
# Setup UEDGEToolBox    
from ToolBoxSettings import *
ToolBox=ToolBoxSettings()


from UEDGEDoc import *
#from UEDGESimulation import *    

#from UEDGEMisc import *       
#from UEDGEBas2Py import *
#from UEDGEIO import *
#from UEDGEMesh import *


#Defining


ListObjects=['Settings','Sim']
print('### UEDGEToolBox objects available:{}'.format(ListObjects))