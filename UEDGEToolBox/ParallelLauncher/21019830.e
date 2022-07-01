Traceback (most recent call last):
  File "/fusion/projects/boundary/guterlj/UEDGE_1D/slab/input_1D_fixed_fraction.py", line 300, in <module>
    UBox.Run(mult_dt_fwd=5.0,dtreal = 1e-8, t_stop=1e3)
  File "/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/Simulation/Sim.py", line 167, in Run
    return self.RunTime(**kwargs)
  File "/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/Simulation/Sim.py", line 480, in RunTime
    self.SaveLast()  # Save data in file SaveDir/CaseName/last.npy
  File "/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/Simulation/SimUtils.py", line 138, in SaveLast
    self.Save('last',DataSet=DataSet,DataType='UEDGE',OverWrite=True)
  File "/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/Simulation/Sim.py", line 207, in Save
    FilePath = self.Source(FileName, CaseName, Folder, Project, CreateFolder=True, EnforceExistence=False)
  File "/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/ProjectManager/Source.py", line 61, in Source
    os.mkdir(ObjectDir)
FileNotFoundError: [Errno 2] No such file or directory: '/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/ParallelLauncher/SaveDir/runtest_6'
