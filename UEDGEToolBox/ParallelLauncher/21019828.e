/fusion/projects/boundary/guterlj/anaconda3/envs/uedge/lib/python3.8/site-packages/numpy/lib/npyio.py:528: VisibleDeprecationWarning: Creating an ndarray from ragged nested sequences (which is a list-or-tuple of lists-or-tuples-or ndarrays with different lengths or shapes) is deprecated. If you meant to do this, you must specify 'dtype=object' when creating the ndarray.
  arr = np.asanyarray(arr)
Traceback (most recent call last):
  File "/fusion/projects/boundary/guterlj/UEDGE_1D/slab/input_1D_fixed_fraction.py", line 300, in <module>
    UBox.Run(mult_dt_fwd=5.0,dtreal = 1e-8, t_stop=1e3)
  File "/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/Simulation/Sim.py", line 167, in Run
    return self.RunTime(**kwargs)
  File "/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/Simulation/Sim.py", line 517, in RunTime
    self.livedata_collector()
  File "/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/Simulation/livedata.py", line 40, in livedata_collector
    self.collect_livedata()
  File "/fusion/projects/boundary/guterlj/UEDGEToolBox/UEDGEToolBox/Simulation/livedata.py", line 49, in collect_livedata
    self.livedata[k][self.iter_data,:] = getattr(bbb,k)
KeyError: 'ni'
