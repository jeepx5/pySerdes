# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 16:28:26 2020

@author: -
"""

from scipy import signal

import numpy as np

from control.matlab import *

import control

import matplotlib.pyplot as plt

from prbs_gen import prbs_gen

from eyediagram import bres_segment_count_slow, bres_curve_count_slow,random_trace



osr=32 #when osr is 64, the cdr final lock point depends on initial point



seed_lsb=[1,0,1,1,0,1,0]
seed_msb=[1,1,0,1,0,0,1]


prbsgen_lsb=prbs_gen(seed_lsb)
prbslst_lsb=prbsgen_lsb.prbs7()
prbsgen_msb=prbs_gen(seed_msb)
prbslst_msb=prbsgen_msb.prbs7()
prbslst_msb = [a *2 for a in prbslst_msb]
#for PAM4
prbs2x= [a + b for a,b in zip(prbslst_lsb, prbslst_msb)]*80
####################
# for NRZ
#prbs2x=prbslst_lsb
####################

print(len(prbs2x))

prbs_os=prbsgen_lsb.prbs_ext(prbs2x, osr)

print(len(prbs_os))

tt = np.linspace(0, len(prbs_os), len(prbs_os))

dr=10e9

dt=1/osr

normpole=2*np.pi*8600e6/dr

normtxpole2=2*np.pi*16000e6/dr

normtxpole1=2*np.pi*4000e6/dr

normtxzero=2*np.pi*5200e6/dr



num = [1]

den = [1/normpole/normpole, 1/normpole*2, 1]

numtx = [1/normtxzero, 1]

#numtx = [1]

dentx = [1/normtxpole1/normtxpole2, 1/normtxpole1+1/normtxpole2, 1]

#dentx=[1]



sys = tf(numtx, dentx)

sys2=tf(num, den)

syst=series(sys, sys2)

print(type(sys))



print(len(prbs_os), len(tt))

tt=tt*dt

#t, y=step(sys)

#y, t, x =lsim(syst, prbs_os, tt, interp=1)
y, t, x =lsim(syst, prbs_os, tt)
#y=y*0.4
#print(y)
#y=np.delete(y[0], -1, axis=0)

print(y)
print(len(y))

y4i=np.reshape(y, [int(len(y)/osr/2), osr*2])

print(y4i.shape)

print(y4i[1].shape)

ti=t[0:osr*2]

s = 0

y4i=y4i-s





################
# add noise 
shp=y4i.shape
vrnd=np.random.rand(list(shp)[0], list(shp)[1])/4
y4i=y4i+vrnd
################




for k in range(len(y4i)-1):

    #print(y4i[1].shape, ti.shape)

    plt.plot(ti, y4i[k], label='y_0', color='g', alpha=.05)

    plt.grid()

    plt.title('Eye Diagram of Channel Out 2UI')

#plt.plot(t, y[1],  label='y_1')

plt.show()



##########################
#### MMSE PD CDR #########
##########################
dm2 = 0
errm2 = 0
dm1 = 0
errm1 =0
rxtd = 13
rxtdreal = 13.0
tdval = []
ysample0=[]
ysample1=[]
ysample2=[]
ysample3=[]
errval = []
dataval = []
vpval1 =[]
vpscale = 0.6
vp1 = 1*vpscale
vpval2 =[]
vp2 = 2*vpscale
vpval3 =[]
vp3 = 3*vpscale
vpval0 =[]
vp0 = 0*vpscale

y4i=np.reshape(y4i, [int(len(y)/osr), osr])

for k in range(len(y4i)-1):
    tnow = rxtd
    if ((vp1+vp0)/2< y4i[k][tnow] <= (vp1+vp2)/2):
        d0 = -1
        err = np.sign(y4i[k][tnow]-vp1)
        vp1 = vp1+0.05*(err)
        ysample1.append(y4i[k][tnow])
        
    elif ((vp1+vp2)/2 < y4i[k][tnow] <= (vp3+vp2)/2):
        d0 = 1
        err = np.sign(y4i[k][tnow]-vp2)
        vp2 = vp2+0.05*(err)
        ysample2.append(y4i[k][tnow])
    elif (y4i[k][tnow] > (vp3+vp2)/2):
        d0 =2
        err = np.sign(y4i[k][tnow]-vp3)
        vp3 = vp3+0.05*(err)
        ysample3.append(y4i[k][tnow])
    elif (y4i[k][tnow] < (vp1+vp0)/2):
        d0 = -2
        err = np.sign(y4i[k][tnow]-vp0)
        vp0 = vp0+0.05*(err)
        ysample0.append(y4i[k][tnow])
    #else: 
    #    d0 = 0
    #    err = 0    
    '''
    if(d0 ==1 or d0 ==-1 and d0 != dm1):
        slope = np.sign(d0-dm1)         
    else:
        slope =0
        err =0
   '''     
    
    
    
    #err = (y4i[k][tnow]-d0)
    #Pattern Filter
    '''
    if ((dm2<dm1 and dm1>d0 and dm2==d0 ) or (dm2>dm1 and dm1<d0 and dm2==d0 )):
        #MMPD
        #dstep = np.sign(errm1)*np.sign(dm2-1.5)-np.sign(errm2)*np.sign(dm1-1.5)
        dstep = dm1*err-d0*errm1
    else: dstep = 0
    '''
    dstep = (dm1*err-d0*errm1)
    #print('d0: ',d0)
    #print('dm1: ',dm1)
    #print('err: ',err)
    #print('errm1: ',errm1)
    #print('step： ', dstep)
    #MMSE PD
    #dstep = (slope*err)
    
    #rxtdreal =((rxtdreal+0.25*dstep+np.random.rand()*0.0125)%len(y4i[1]))
    rxtdreal =((rxtdreal+0.25*dstep+np.random.rand()*0.0)%len(y4i[1]))
    #added jitter, without jitter the pd will lock to wrong phases
    rxtd =int(rxtdreal)
    tdval.append(tnow)
 
        
    errval.append(err)
    dataval.append(d0)
    dm2 = dm1
    errm2 = errm1
    dm1 = d0
    errm1=err
    vpval1.append(vp1)
    vpval2.append(vp2)
    vpval3.append(vp3)
    vpval0.append(vp0)
    
plt.plot(tdval, label='y_0', color='g', alpha=.5)
plt.grid()
plt.title('CDR Out')
plt.show()       

plt.plot(vpval0, label='vp_0', color='g', alpha=.5)
plt.plot(vpval1, label='vp_1', color='b', alpha=.5)
plt.plot(vpval2, label='vp_2', color='r', alpha=.5)
plt.plot(vpval3, label='vp_3', color='k', alpha=.5)
plt.title('Vp0to3')
plt.grid()
plt.show()



plt.plot(ysample0, label='ys_0', color='g', alpha=.5)
plt.plot(ysample1, label='ys_1', color='b', alpha=.5)
plt.plot(ysample2, label='ys_2', color='r', alpha=.5)
plt.plot(ysample3, label='ys_3', color='k', alpha=.5)
plt.title('Ysample0to3')
plt.grid()
plt.show()

########################
##### eye position #####
########################    
print('err_mean: ',np.mean(errval))
print('data_mean: ',np.mean(dataval))
print('cdr_out: ', np.mean(tdval))
'''
ti = range(osr)
for k in range(len(y4i)-1):

    #print(y4i[1].shape, ti.shape)

    plt.plot(ti, y4i[k], label='y_0', color='g', alpha=.15)

    plt.grid()

    plt.title('Eye Diagram of Channel Out 1UI')

#plt.plot(t, y[1],  label='y_1')

plt.show()
'''
