from scipy import signal
import numpy as np
from control.matlab import *
import control
import matplotlib.pyplot as plt
from prbs_gen import prbs_gen
from eyediagram import bres_segment_count_slow, bres_curve_count_slow,random_trace

osr=64

seed=[1,0,1,1,0,1,0]
prbsgen=prbs_gen(seed)
prbslst=prbsgen.prbs7()
prbs2x=prbslst#+prbslst
print(len(prbs2x))
prbs_os=prbsgen.prbs_ext(prbs2x, osr)
print(len(prbs_os))
tt = np.linspace(0, len(prbs_os), len(prbs_os))
dr=5e9
dt=1/osr
normpole=2*np.pi*2600e6/dr
normtxpole2=2*np.pi*3000e6/dr
normtxpole1=2*np.pi*1000e6/dr
normtxzero=2*np.pi*1600e6/dr

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
y, t, x =lsim(syst, prbs_os, tt, interp=1)
y=y*0.4
print(y)
#y=np.delete(y[0], -1, axis=0)
print(y)
print(len(y))
y4i=np.reshape(y, [int(len(y)/osr/2), osr*2])
print(y4i.shape)
print(y4i[1].shape)
ti=t[0:osr*2]
s = 0.2
y4i=y4i-s
shp=y4i.shape
vrnd=np.random.rand(list(shp)[0], list(shp)[1])/80
#vrnd=0
y4i=y4i+vrnd


#plt.plot(y)
#plt.plot(tt/osr, prbs_os)
for k in range(len(y4i)-1):
    #print(y4i[1].shape, ti.shape)
    plt.plot(ti, y4i[k], label='y_0', color='g', alpha=.15)
    plt.grid()
    plt.title('Eye Diagram of Channel Out')
#plt.plot(t, y[1],  label='y_1')
plt.show()


