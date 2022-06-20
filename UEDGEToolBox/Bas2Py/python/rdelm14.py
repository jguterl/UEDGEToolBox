#>>> Produced by UBoxBas2Py. Original file: /home/guterlj/boundary/uedge_face_1D/basis/rdelm1
#>>> Timestamp: 2021-09-30 16:50:20
iota=np.array([np.arange(1,i+1) for i in range(1,300)],dtype=np.ndarray)
api.apidir=Source('api',Folder='InputDir')
aph.aphdir=Source('aph',Folder='InputDir')
# 1D case
# MVU, 7-aug-09
#---------------------------------------------------------------------------#

#>> package flx  
#>> package grd  
#>> package bbb  
  
bbb.mhdgeo=-1  #set cartesian geometry
bbb.isfixlb=2  #left boundary as sym. plane; no flux at cut

# Set the geometry
grd.radx=0.164155443  #outer "radial" wall
grd.radm=0.154154443  #minimum "radial" position
grd.rad0=0.154155443  
grd.alfyt=-2.0  #radial nonuniformity factor; < 0 => expanding
grd.za0=0.  #poloidal symmetry plane location
grd.zaxpt=2.61  #poloidal location of x-point
grd.zax=4.18  #poloidal location of divertor plate

grd.alfxt=6.0  
#poliodal nonuniformity factor; to make smooth
#transition to exp. grid, alfxt should satisfy
#the eqn dzun = (zax-zaxpt+dzun)
#               (1-exp(-alfxt/(nx-ixpt2+1))) /
#               (1-exp(-alfxt))
#where dzun = (zaxpt-za0)/ixpt2 and
#ixpt2 = ncore(1,2).
grd.btfix=3.0  #constant total B-field
grd.bpolfix=0.314  #constant poloidal B-field
bbb.ngrid=1  
com.nxleg[0,0]=0  
com.nxcore[0,0]=0  
  
com.nxcore[0,1]=25  
com.nxleg[0,1]=75  
  
com.nycore[0]=0  
com.nysol=1  
  

# Boundary conditions

#-core boundary
#        isnicore(1)=0
#        curcore(1)=0.
#        isnicore(2)=1
#        ncore(2)=0.
bbb.isnicore=0  
bbb.curcore=0.  
bbb.iflcore=1  
bbb.pcoree=3.e4  
bbb.pcorei=3.e4  
bbb.isupcore=1  #if 1 then slip, if 0 vel =0 on core bndry

#-outer wall boundary
bbb.istewc=0  #wall has zero temp. deriv.
bbb.istiwc=0  
bbb.isnwcono=0  
bbb.isupwo=1  #slip

#-private region boundary
bbb.istepfc=0  #priv. flux has zero temp. deriv.
bbb.istipfc=0  
bbb.isnwconi=0  
bbb.isupwi=1  #slip


bbb.recycp=1.0  # plate recycling coeff.
bbb.recycw=1.0  
bbb.recycm=0.3  

bbb.bcee=5.  
bbb.bcei=3.5  
  #energy transmission coeffs. for elec & ions
bbb.isupss=0  #parallel vel sonic


# Transport coefficients
bbb.difni[0]=2.0  # anomalous hydrogenic particle diff. coeff.
bbb.difni[1:12]=1.0  # anomalous impurity particle diff. coeff.
bbb.kye=4.  
bbb.kyi=0.2  
  # anomalous elec. & ion energy diff. coeff.
bbb.travis[0]=0.2  # anomalous viscosity coeff.

# Flux limits
bbb.flalfe=1e20  
bbb.flalfi=1e20  
bbb.flalfgx=1.e20  
bbb.flalfgy=1.e20  
bbb.flalfv=1.e20  
  

# Finite difference algorithms
bbb.methe=33  
bbb.methu=33  
bbb.methg=33  
  
bbb.methn=33  
bbb.methi=33  
  

# Solver package
bbb.svrpkg="nksol"  
bbb.mfnksol=3  
bbb.iscolnorm=3  
bbb.epscon1=.005  
bbb.ftol=1.e-8  
bbb.premeth="banded"  
bbb.runtim=1.e-7  
bbb.rlx=.1  

# Neutral gas propeties
bbb.cngfx=1.  
bbb.cngfy=1.  
  #turn-on grad(T_g) flux if =1
bbb.cngflox=0.  
bbb.cngfloy=0.  
  #turn-on drift with ions if =1
bbb.cngmom=0.  #ion-gas momentum transfer
bbb.eion=5.  #birth energy of ions
bbb.ediss=10.  #dissoc. energy lost from elecs (eion=2*ediss)
bbb.isrecmon=1  #=1 turns on recombination
bbb.sxgsol=1.  #poloidal stretching factor for gas in SOL
bbb.sxgpr=1.  #poloidal stretching factor for gas in priv. fl


# Currents and potential parameters
bbb.isphion=0  
bbb.rsigpl=1.e-8  #anomalous cross-field conductivity
bbb.cfjhf=0.  #turn-on heat flow from current (fqp)
bbb.jhswitch=0  #Joule Heating switch

# Parallel neutral momentum equation
bbb.isupgon[0]=1  
#>> if (isupgon(1) .eq. 1) then  
bbb.isngon[0]=0  
com.ngsp=1  
com.nhsp=2  
bbb.ziin[com.nhsp-1]=0  
# The following are probably default, set them anyway to be sure
bbb.cngmom=0  
bbb.cmwall=0  
bbb.cngtgx=0  
bbb.cngtgy=0  
bbb.kxn=0  
bbb.kyn=0  
#>> endif  


#Atomic physics packages
com.istabon=10  #analytic rates
bbb.minu=1  #hydrogen
bbb.fnuizx=0  #no nuiz contribution for gas diff.
bbb.flalfgx=1e20  
bbb.flalfgy=1e20  
  #no flux-limiter for gas diffusion
aph.issgvcxc=2  
aph.sgvcxc=5e-19  
  #constant CX crossection (gas diffusion)
bbb.sigcx=5e-19  #using same value for neutral viscosity
bbb.rnn2cx=0  #eliminate n-n effects in neutral viscosity

# Particular values for test
bbb.minu[0]=1.  # ion mass relative to mp (hydrogen)
bbb.lnlam=10.  # Coulomb logarithm
#cthe = 0.       # thermal force coeff. for || mom. eq. (0.71 default)
#cvgp = 0.       # turn off grad p in Te and Ti eqns.
#cfvisx = 0.     # turn off viscous heating for ions
#cfvisy = 0.     # turn off viscous heating for ions
#!ckinfl = 0.     # turn off viscous boundary term for heat flux
bbb.cfnidh=1.d-3  
#cfticx = 0.

bbb.bcen=0.  
bbb.cgengpl=1.  
bbb.cgengw=0.  

bbb.isimpon=2  

#new setting initial/background fields:
bbb.allocate()  
#         tes=10.*ev
#         tis=10.*ev
bbb.nis=1.e19  
bbb.ups=1e4  
bbb.ngs=1e18  

bbb.albedolb[0,0]=1.0  
bbb.albedorb[0,0]=1.0  

#-set a fix for neutral gas convective energy flux
#bcgpatch=0 #same as gcfacgx=1 in the archive version
bbb.gcfacgx=1  

# Restart from a save file
bbb.restart=1  
bbb.ngbackg=1.e11  # applies for all species here (as in pfb file)

bbb.isbcwdt=1  
bbb.nurlx=1.d9  

#>> readpost("mist.dat")  
#>> splinem  

#>> ii  
do ii=0,nx+1  
bbb.afracs[ii,:]=0.05*exp[:]-4.*np.array([n-1])+1-ii)/np.array([n-1])-ixpt2))  
#>> enddo  
bbb.atau[:,:]=1.e-4  
bbb.ntau[:,:]=bbb.ne*bbb.atau  

#>> restore pfinitial  

