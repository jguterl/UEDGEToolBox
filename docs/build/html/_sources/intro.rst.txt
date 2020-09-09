Introduction
============

UEDGEToolBox is a python package to pre-process, run and post-process UEDGE simulations developed by 'J. Guterl <guterlj@fusion.gat.com>`_ at General Atomics. UEDGEToolBox provide the following functionnalities:

* Parsing input scripts
* Running UEDGE simulations in time-dependent mode with the nksol solver
* Saving/loading UEDGE simulation data in a structured way
* Plotting 1D and 2D UEDGE simulation data
* Comparing data from several UEDGE simulations
* Converting BAS script into python script
* Handling of advanced workflows to perform parameter scan and incremental convergence 

UEDGEToolBox is an object-oriented package developed for python 3.6 and above. A primer on object-oriented programming in python can be found `here <https://realpython.com/python3-object-oriented-programming/>`_ or `here <https://www.tutorialspoint.com/python/python_classes_objects.htm>`_.   

Getting started
===============
 
UEDGEToolBox requires python version >= 3.6. A list of the dependency  and the package UEDGE. Instructions to install the UEDGE package can be found `here <>`_. UEDGEToolBox can be installed through Pypi
   
>>> pip install UEDGEToolBox

or can installed from the source code available in the UEDGEToolBox Git repository https://github.com/jguterl/UEDGEToolBox/. 

>>> git clone https://github.com/jguterl/UEDGEToolBox/
>>> cd UEDGEToolBox
>>> python setup.py install


  
QuickStart
==========
Open a python session and import UEDGEToolBox. The UEDGE pakcage is automatically imported by UEDGEToolBox.  

>>> from UEDGEToolBox import *

When UEDGEToolBox is imported for the first time, a prompt is displayed to set the default name, email address and affiliation of the local user (see Settings). Upon agreement of the user, a file `.UBoxSettings` will be created in the user's home folder to store these settings. 
The following message is displayed once UEDGEToolBox have been loaded:

.. highlight:: python

   UEDGEToolBox sucessfully launched. Type QuickStart() for basic commands. 
   
  

UEDGEToolBox requires that at least one project is loaded in :py:object:'UBox' to load and dump UEDGE simulation data (see Projects). To create a new project, a path toward an existing or new project file where projects settings will be stored must first be set with 

>>> SetProjectsFile()

A new project can then be created with

>>> CreateProject()

Once a project has been created, grid and input files can be added to the folder

>>> UBox.Inputdir
>>> 

UEDGE simulations can be run. 


 
UEDGEToolBox.Settings
=====================

     

Initialization of UEDGEToolBox 
==============================

The initialization of the UEDGEToolBox is handled by the module :py:mod:`Launcher`. When the module is imported, an instance :py:object:`UBox` of the class :py:class:`UBoxLauncher` is created

>>> UBox=UboxLauncher()

The method Start() is then applied to :py:object:`UBox` to create and overload instances of the classes :py:class:`UBoxSettings` , :py:class:`UBoxProjects` and :py:class:`UBoxSim` into :py:object:`UBox`. An instance of the class :py:class;UBoxDoc` is also created and returned to the current namespace.
  
>>> (Doc)=UBox.Start() 

The instantiation of the class :py:class:`UBoxSettings` requires the existence of the 
 

  

Developping UEDGEToolBox
========================

hello 

Loading UEDGEToolBox when starting a python session 
===================================================

hello 

Documentation
=============
>>> make html
>>> sphinx-apidoc -o source ../UEDGEToolBox

 


