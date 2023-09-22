# -*- coding: utf-8 -*-
from UEDGEToolBox.Bas2Py.Bas2Py import UBoxBas2Py
Worker=UBoxBas2Py(Verbose=True,VerboseArgout=True)
BasFile='/home/jguterl/d3d_174270_2500/rd_nf_2019_nc57_ln4'
PyFile='/home/jguterl/Dropbox/python/UEDGEToolBox/UEDGEToolBox/Bas2Py/test.py'
Worker.Convert(BasFile,PyFile,Imax=None)

    
    