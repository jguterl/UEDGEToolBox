#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 18:19:37 2022

@author: guterlj
"""

import itertools
import numpy as np
import os
from UEDGEToolBox.ParallelLauncher import slurm_support 

import subprocess
def chmodx_directory(directory):
    command = 'chmod -R u+x {}'.format(directory)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output,error)
    
def tot_sim(params, tridyn_params={}):
    return np.prod([np.array(len(v)) for v in itertools.chain(params.values(),tridyn_params.values())])

def gnu_parallel_command(runner_exec_file,runner_input, njob):
    commands = ['module load parallel']
    commands += ['parallel -j {} {} {{}} < {}'.format(njob, runner_exec_file,runner_input)]
    return commands

def dump_log(filename,dic):
    np.save(filename,dic)
    
        
class UBoxParallelLauncher():
    def __init__(self,directory=None):
        self.sim_setup = {}
        self.njobs = 0
        
        


    def setup_parallel_runs(self, params, inputfile, casename='run'):

        print("----- Project:",self.CurrentProject)
        dic={}
        dic['inputfile'] = os.path.abspath(inputfile)
        dic['project'] = self.CurrentProject.Name
        dic['directory'] = os.path.abspath(self.CurrentProject.GetPath())
        dic['params'] = params
        dic['nsim'] = np.prod([np.array(len(v)) for v in params.values()])
        
        sims = {}
        sim_param_array = np.zeros((dic['nsim'],len([k for k in params.values()])))  
            
        for i,val in enumerate(itertools.product(*(v for v in params.values()))):
            print('Setup simulation # {} with :'.format(i),';'.join(['{}={}'.format(k,val) for k,val in zip(params.keys(),val)]))
            sim = {}
            val_params = val[0:len(list(params.keys()))]
            sim['inputfile'] =  dic['inputfile']
            sim['project'] = dic['project']
            sim['params'] = dict((k,v) for k,v in  zip(params.keys(),val_params))
            sim['casename'] = '{}_{}'.format(casename,i)
            sim_param_array[i,:] =  np.array([v for v in val])
            self.make_command_line(sim)
            sims[i] = sim
            
        dic['sims_param_array'] = sim_param_array
        dic['sims'] = sims
        self.sim_setup = dic 
        self.njobs = len(list(self.sim_setup['sims'].keys()))
        
  
    @staticmethod
    def make_command_line(sim):
        args = " ".join(['--{}={}'.format(k,v) for (k,v) in sim['params'].items()] + ["--casename={} --project={}".format(sim['casename'],sim['project'])])
        command = "python {} {}".format(sim['inputfile'],args)
        sim['command'] = command 
        
    def setup_slurm_scripts(self,slurm_options):
        self.slurm_runners = [] 
        for (i,sim) in self.sim_setup['sims'].items():
            self.slurmscript_directory = os.path.join(self.sim_setup['directory'],'sbatch_scripts')
            try: 
                os.mkdir(self.slurmscript_directory)
            except:
                pass
            script_name = '{}.sbatch'.format(sim['casename'])
            slurm_options["J"] = sim['casename']
            slurm_options["o"] = os.path.join(self.slurmscript_directory,"{}.o".format(sim["casename"]))
            slurm_options["e"] = os.path.join(self.slurmscript_directory,"{}.e".format(sim["casename"]))
            logpath= os.path.join(self.slurmscript_directory,"{}.log".format(sim["casename"]))
            sim['logpath'] = logpath
            slurm_runner = slurm_support.SlurmSbatch(sim['command']+' >> {}'.format(logpath), **slurm_options, script_dir = self.slurmscript_directory, script_name = script_name, pyslurm=True)
            self.slurm_runners.append(slurm_runner)
            slurm_runner.write_job_file()

    def _sbatch(self):
        #chmodx_directory(self.directory)
        for s in self.slurm_runners:
           s.submit_job()
           
        #job_id = 0
        self.saveas(os.path.join(self.sim_setup['directory'],"log.npy"),self.sim_setup)
        
    def sbatch(self,slurm_options):
            self.setup_slurm_scripts(slurm_options)
            self._sbatch()
            
        
    def saveas(self,filename, obj):
        filename = os.path.join(filename)
        np.save(filename, obj)
        