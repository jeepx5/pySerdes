from scipy import signal
import numpy as np
from control.matlab import *
import control
import matplotlib.pyplot as plt
from prbs_gen import prbs_gen
from eyediagram import bres_segment_count_slow, bres_curve_count_slow,random_trace

osr=16

seed=[1,0,1,1,0,1,0]
prbsgen=prbs_gen(seed)
prbslst=prbsgen.prbs7()
prbs2x=prbslst#+prbslst
print(len(prbs2x))
prbs_os=prbsgen.prbs_ext(prbs2x, osr)
print(prbs_os)

tt = np.linspace(0, len(prbs_os), len(prbs_os))
dr=5e9
normpole=2*np.pi*100e6/5e9*osr

num = [1]
den = [1/normpole/normpole, normpole*2, 1]
sys = tf(num, den)
sys2=tf(num, den)
syst=series(sys, sys2)
print(type(sys))

print(len(prbs_os), len(tt))

#t, y=step(sys)
y, t, x =lsim(syst, prbs_os, tt)
y=y*0.4
print(type(y))
y4i=np.reshape(y, [int(len(y)/osr/2), osr*2])
print(y4i.shape)
print(y4i[1].shape)
ti=t[0:osr*2]
s = 0.2
y4i=y4i-s


for k in range(len(y4i)-1):
    #print(y4i[1].shape, ti.shape)
    plt.plot(ti, y4i[k], label='y_0', color='y', alpha=.3)
    plt.grid()
    plt.title('Eye Diagram of Channel Out')
#plt.plot(t, y[1],  label='y_1')
plt.show()

