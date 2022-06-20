#!/usr/bin/env python3
#workflow to get experimental profiles of Te.ne (radial), project them onto UEDGE grid and adjust transport coefficients to match these data

import numpy as np
import matplotlib.pyplot as plt
import yaml
from scipy import interpolate
from UEDGEToolBox.Utils.Misc import GetListPackage
class ExperimentalData(object):
    def __init__(self,*args,**kwargs):
        self.GetExpData(*args,**kwargs)

    def GetExpData(self,Data,psi_shift=0):
        if type(Data) == str:
            self.ExpData=yaml.safe_load(open(Data).read())
        else:
            self.ExpData = Data
            
        self.ExpData['psi'] = [p+psi_shift for p in self.ExpData['psi']]
        self.CreateInterpolant()


    def PlotExpData(self,ax=None, **kwargs):
        if ax is None:
            if not hasattr(self,'ax_data') or self.ax_data is None:
                fig, self.ax_data = plt.subplots(2);
        else:
            self.ax_data = ax

        if kwargs.get('label') is None:
            kwargs['label'] = 'Exp.'

        self.ax_data[0].plot(self.ExpData['psi'],self.ExpData['ne'],**kwargs)
        self.ax_data[1].plot(self.ExpData['psi'],self.ExpData['Te'],**kwargs)
        self.ax_data[0].set_xlabel('\Psi')
        self.ax_data[1].set_xlabel('\Psi')
        self.ax_data[0].set_ylabel('n_e [m^-3]')
        self.ax_data[1].set_ylabel('T_e [eV]')
        self.ax_data[0].legend()
        self.ax_data[1].legend()



    def CreateInterpolant(self):
        psi = np.array(self.ExpData['psi'])
        ne = np.array(self.ExpData['ne'])
        Te = np.array(self.ExpData['Te'])
        idx = np.unique(psi,return_index=True)[1]
        ne = ne[idx]
        psi = psi[idx]
        Te= Te[idx]

        self.Interpolant = {}
        self.Interpolant['ne'] = interpolate.InterpolatedUnivariateSpline(psi, ne)
        self.Interpolant['Te'] = interpolate.InterpolatedUnivariateSpline(psi, Te)


class UBoxProfileFitting(ExperimentalData):
    def __init__(self, UBox, ixslice=None):

        self.Iteration = 0
        self.UBox = UBox
        self.Itermax = 10

    def Setup(self,Data,gFileName, psi_shift=0.0,**kwargs):
        self.GetExpData(Data,psi_shift)
        self.GetPsiN(gFileName)
        self.SetIxSlice(**kwargs)
        self.InterpolateExpData()
        self.SetCore()
        self.PlotExpData()
        self.GetTranspCoeffs()
        self.PlotTranspCoeffs()

    def GetPsiN(self,gFileName):
        from omfit_classes.omfit_eqdsk import OMFITgeqdsk
        g = OMFITgeqdsk(gFileName)
        self.psi = (self.UBox.Grid['psi'][0,:,0]-g['SIMAG'])/(g['SIBRY'] - g['SIMAG'])

    def SetIxSlice(self,ixslice=None, **kwargs):
        from uedge import bbb
        self.ixslice = bbb.ixmp if ixslice is None else ixslice

    def InterpolateExpData(self):
        from uedge import com
        self.ne_exp = self.Interpolant['ne'](self.psi[0:])
        self.te_exp = self.Interpolant['Te'](self.psi[0:])
        self.ne_core = self.Interpolant['ne'](self.psi[0]).mean()
        self.te_core = self.Interpolant['Te'](self.psi[0]).mean()
        print('Experiment te core:',self.te_core)
        print('Experiment ne core:',self.ne_core)
        self.grad_ne_exp=np.diff(self.ne_exp)*com.gyc[self.ixslice,1:]
        self.grad_te_exp=np.diff(self.te_exp)*com.gyc[self.ixslice,1:]

    def GetTranspCoeffs(self):
        from uedge import bbb
        self.D_old = np.copy(bbb.dif_use[self.ixslice,:,0])
        self.kye_old = np.copy(bbb.kye_use[self.ixslice,:])
        self.D_new = np.copy(self.D_old)
        self.kye_new = np.copy(self.kye_old)

    def UpdateTranspCoeffs2(self, kye_max=100, D_max=6,D_min=0.1, kye_min=0.5,max_frac=20, alpha_te=0,beta_te=1.0,**kwargs):
        from uedge import bbb, com
        self.grad_ne = np.diff(bbb.ne[self.ixslice,0:])*com.gyc[self.ixslice,1:]
        self.grad_te = np.diff(bbb.te[self.ixslice,0:])*com.gyc[self.ixslice,1:]
        self.GetTranspCoeffs()
        
        self.D_new[0:-1] = self.D_old[0:-1] * self.grad_ne/self.grad_ne_exp
        self.D_new[self.D_new>self.D_old*max_frac] = self.D_old[self.D_new>self.D_old*max_frac]*max_frac
        fac = (self.grad_te/bbb.ev/self.grad_te_exp)**beta_te
        self.kye_new[0:-1] = self.kye_old[0:-1] * fac
        if beta_te!=1.0:
            print('Fitting with beta_te')
            print(self.kye_new[0:-1]/self.kye_old[0:-1])

        if alpha_te!=0:
            print('Fitting with alpha_te')
            fac = (1+alpha_te* (bbb.te[self.ixslice,0:-1]/bbb.ev - self.te_exp[0:-1])/self.te_exp[0:-1])
            print(fac)
            self.kye_new[0:-1] = self.kye_old[0:-1] *fac
        #Extrapolate
        self.kye_new[-2:] = self.kye_new[-3]
        self.D_new[-2:] = self.D_new[-3]


        self.D_new[(self.D_new<D_min)] = D_min
        #self.kye_new[(self.kye_new<0)] = self.kye_new[np.where(self.kye_new>0)[0][-1]]

        self.kye_new[(self.kye_new>kye_max)] = kye_max
        self.kye_new[(self.kye_new<kye_min)] = kye_min
        self.D_new[(self.D_new>D_max)] = D_max

        bbb.dif_use[:,:,0] =np.copy(self.D_new[:])
        bbb.kye_use[:,:] = np.copy(self.kye_new[:])
        bbb.kyi_use = np.copy(bbb.kye_use)
        print('final kye_use new/old',self.kye_new[0:-1]/self.kye_old[0:-1])
        
        
    def UpdateTranspCoeffs(self, kye_max=100, D_max=10,D_min=0.01, kye_min=0.05,max_frac=1000, alpha_te=0,beta_te=1.0,**kwargs):
        from uedge import bbb, com
        self.UBox.Pandf()
        self.grad_ne = np.diff(bbb.ne[self.ixslice,0:])*com.gyc[self.ixslice,1:]
        self.grad_te = np.diff(bbb.te[self.ixslice,0:])*com.gyc[self.ixslice,1:]
        self.GetTranspCoeffs()
        
        self.D_new[0:-1] = self.D_old[0:-1] * self.grad_ne/self.grad_ne_exp
        self.D_new[self.D_new>self.D_old*max_frac] = self.D_old[self.D_new>self.D_old*max_frac]*max_frac
        fac = (self.grad_te/bbb.ev/self.grad_te_exp)**beta_te
        fac2= (bbb.feey[self.ixslice,0:]/com.sy[self.ixslice,0:]-5.0/2.0*bbb.vey[self.ixslice,0:]*bbb.ne[self.ixslice,0:]*bbb.te[self.ixslice,0:])/bbb.ne[self.ixslice,0:]
        fac3 = -fac2[0:-1]/(self.grad_te_exp*bbb.ev)
        self.kye_new[0:-1] = fac3#self.kye_old[0:-1] * fac
        print('self.kye_old[0:-1] * fac',self.kye_old[0:-1] * fac)
        
        # if beta_te!=1.0:
        #     print('Fitting with beta_te')
        #     print(self.kye_new[0:-1]/self.kye_old[0:-1])

        # if alpha_te!=0:
        #     print('Fitting with alpha_te')
        #     fac = (1+alpha_te* (bbb.te[self.ixslice,0:-1]/bbb.ev - self.te_exp[0:-1])/self.te_exp[0:-1])
        #     print(fac)
        #     self.kye_new[0:-1] = self.kye_old[0:-1] *fac
        #Extrapolate
        
        self.kye_new[-2:] = self.kye_new[-3]
        self.D_new[-2:] = self.D_new[-3]
        print('self.kye_new[0:-1]',self.kye_new[0:-1])

        self.D_new[(self.D_new<D_min)] = D_min
        #self.kye_new[(self.kye_new<0)] = self.kye_new[np.where(self.kye_new>0)[0][-1]]

        self.kye_new[(self.kye_new>kye_max)] = kye_max
        self.kye_new[(self.kye_new<kye_min)] = kye_min
        self.D_new[(self.D_new>D_max)] = D_max

        bbb.dif_use[:,:,0] =np.copy(self.D_new[:])
        bbb.kye_use[:,:] = np.copy(self.kye_new[:])
        bbb.kyi_use = np.copy(bbb.kye_use)
        print('final kye_use new/old',self.kye_new[0:-1]/self.kye_old[0:-1])

    def PlotTranspCoeffs(self, ax=None, NewFig=False):
        if ax is None:
            if not hasattr(self,'ax_transp') or self.ax_transp is None or NewFig is True:
                fig, self.ax_transp = plt.subplots(2);
        else:
            self.ax_transp = ax

        psic = self.psi
        from uedge import bbb
        self.ax_transp[0].plot(psic, bbb.dif_use[self.ixslice,:,0],  label='Iter={}'.format(self.Iteration))
        self.ax_transp[1].plot(psic, bbb.kye_use[self.ixslice,:],label='Iter={}'.format(self.Iteration))
        self.ax_transp[0].legend()
        self.ax_transp[1].legend()
        self.ax_transp[0].set_xlabel('$\Psi_N$')
        self.ax_transp[0].set_xlabel('$\Psi_N$')
        self.ax_transp[0].set_ylabel('D')
        self.ax_transp[1].set_ylabel('kye')
        
    def PlotProfiles(self,ax=None, NewFig=False):
        from uedge import bbb
        if ax is None:
            if not hasattr(self,'ax_data') or self.ax_data is None or NewFig is True:
                fig, self.ax_data = plt.subplots(2);
        else:
            self.ax_data = ax

        self.ax_data[0].plot(self.psi,bbb.ne[self.ixslice,:],marker='o',label='Iter={}'.format(self.Iteration))
        self.ax_data[1].plot(self.psi,bbb.te[self.ixslice,:]/bbb.ev,marker='o',label='Iter={}'.format(self.Iteration))
        self.ax_data[0].legend()
        self.ax_data[1].legend()
        plt.show()
        plt.draw()
        plt.pause(0.1)
        

    def SetCore(self):
        from uedge import bbb
        bbb.ncore[0] = self.ne_core
        bbb.tcoree = self.te_core
        bbb.tcorei = self.te_core
        bbb.iflcore = 0
        bbb.isnicore[0]=1
        
    

    def StartFitting(self, CaseName,Itermax=10, dtreal=5e-8, dt_tot=0, **kwargs):
        self.Itermax = Itermax
        self.Iteration = 0
        self.UBox.CaseName = CaseName + '_fit_{}'.format(self.Iteration)
        self.SetCore()
        self.PlotExpData()
        self.GetTranspCoeffs()
        self.PlotTranspCoeffs()

        plt.show()
        plt.draw()
        plt.pause(0.5)
        
        self.UBox.RunTime(dtreal=dtreal, dt_tot=dt_tot, **kwargs)
        self.PlotProfiles()
        self.UBox.Save('fit.npy',OverWrite=True)
        #self.UBox.Save('last_fit.npy',OverWrite=True)
        self.UBox.Save('transpcoeff.npy',DataSet=[('dif_use','kye_use')],DataType=['UEDGE'],OverWrite=True)
        #self.UBox.Save('last_transpcoeff.npy',DataSet=[('dif_use','kye_use')],DataType=['UEDGE'],OverWrite=True)
        
        self.ContFitting(CaseName, dtreal=5e-8, dt_tot=0, **kwargs)
    
    def RestoreIter(self,CaseName, Iteration):
        self.UBox.CaseName = CaseName + '_fit_{}'.format(Iteration)
        self.UBox.Load('fit.npy')
        self.UBox.Load('transpcoeff.npy')
        self.GetTranspCoeffs()
        self.Iteration = Iteration
        
    def ContFitting(self,CaseName, Itermax=None, dtreal=5e-8, dt_tot=0, **kwargs):
        
        if Itermax is not None:
            self.Itermax = Itermax
        while self.Iteration < self.Itermax and (not hasattr(self.UBox,'Status') or self.UBox.Status != 'aborted'):
            
            self.Iteration+=1
            self.UBox.CaseName = CaseName + '_fit_{}'.format(self.Iteration)
            self.UpdateTranspCoeffs(**kwargs)
            self.PlotTranspCoeffs()
            self.UBox.RunTime(dtreal=dtreal, dt_tot=dt_tot, **kwargs)
            self.UBox.Save('transpcoeff.npy',DataSet=[('dif_use','kye_use')],DataType=['UEDGE'],OverWrite=True)
            #self.UBox.Save('last_transpcoeff.npy',DataSet=[('dif_use','kye_use')],DataType=['UEDGE'],OverWrite=True)
            #self.UBox.Save('last_fit.npy',OverWrite=True)
            self.UBox.Save('fit.npy',OverWrite=True)
            self.PlotProfiles()
            plt.pause(0.5)
            plt.show()


