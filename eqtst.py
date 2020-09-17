# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 08:05:22 2020

@author: jim.jin
"""

from scipy import signal
import numpy as np
from control.matlab import *
import control
import matplotlib.pyplot as plt
from prbs_gen import prbs_gen
from eyediagram import bres_segment_count_slow, bres_curve_count_slow,random_trace
from mmpd_cdr import pam4cdr
from copy import *
import pandas as pd

if __name__ == "__main__":
    osr=32 #when osr is 64, the cdr final lock point depends on initial point
    seed_lsb=[1,0,1,1,0,1,0]
    seed_msb=[1,1,0,1,0,0,1]
    #seed_lsb=[1,0,1,1,0,1,0,1,0,1,1,0,1,0,1]
    #seed_msb=[1,1,0,1,0,0,1,1,0,1,1,0,1,0,1]
    dr = 10e9
    
    normpole=2*np.pi*5.6e9/dr
    normtxpole2=2*np.pi*10e9/dr
    
    normtxpole1=2*np.pi*12e9/dr
    normtxzero=2*np.pi*10.2e9/dr
    
    normhfpole1=2*np.pi*4.2e9/dr
    normhfpole2=2*np.pi*8.5e9/dr
    normhfzero=2*np.pi*4.2e8/dr
    
    normlfpole1=2*np.pi*10.2e9/dr
    normlfpole2=2*np.pi*12.2e9/dr
    
    num = [1]    
    den = [1/normpole/normpole, 1/normpole*2, 1]
    
    numtx = [1/normtxzero, 1]      
    dentx = [1/normtxpole1/normtxpole2, 1/normtxpole1+1/normtxpole2, 1]

    numhf = [1/normhfzero, 0]
    denhf = [1/normhfpole1/normhfpole2, 1/normhfpole1+1/normhfpole2, 1]
    
    numlf = [1]
    denlf = [1/normlfpole1/normlfpole2, 1/normlfpole1+1/normlfpole2, 1]
  
    txtf = tf(numtx, dentx)
    chtf = tf(num, den)
    
    eqhftf = tf(numhf, denhf)
    eqlftf = tf(numlf, denlf)
    
    #bode(txtf)
    #bode(chtf)
    #bode(series(txtf, chtf))
    '''
    for i in range(1, 16, 1):
        eqtf = eqlftf+i/32*eqhftf#series(eqlftf,eqhftf)
        print(eqtf)
        bode(eqtf)
        #bode(eqlftf)
    '''
    #eqtf = 0.15*eqhftf+eqlftf
    #eqtf = series(txtf, chtf)#series(eqlftf,eqhftf)
    
    listlength = 64#prbs7 =320, prbs15 =1
    #syst=series(sys, sys2)

    pam4sys = pam4cdr(osr, seed_lsb, seed_msb, dr)
    
    rxin, t = pam4sys.txch(txtf, chtf, listlength)
    tt = np.linspace(0, len(rxin), len(rxin))
    dt=1/osr
    tt=tt*dt
    df = pd.DataFrame()
    for i in range(4):
        eqtf = i/12.5*eqhftf+eqlftf
        y, t, x =lsim(eqtf, rxin, tt)
        df.insert(i, i, y)
        #y4i=np.reshape(list(y),[int(len(y)/osr/2), int(osr*2)])
        '''
        for k in range(int(len(y4i)/listlength)-1):    
            plt.plot(y4i[k], label='y_0', color='g', alpha=.15)    
            plt.grid()    
            plt.title('Eye Diagram of Channel Out 2UI')    
        plt.show()
        '''               
        #df.append(y.tolist(), ignore_index=True)
    print('eq data ready')
    sumout, ysample, vpval, errmean, phasemean,h1, tdval, eqval = pam4sys.rxCDReq(df, 0.6,13) 
        
        
    plt.plot(ysample[0], label='y_0', color='r', alpha=.15) 
    plt.plot(ysample[1], label='y_0', color='b', alpha=.15)
    plt.plot(ysample[2], label='y_0', color='g', alpha=.15)
    plt.plot(ysample[3], label='y_0', color='k', alpha=.15)
    #plt.plot(rxin1[k], label='y_0', color='r', alpha=.15) 
    plt.grid()    
    plt.title('Eye Diagram of Channel Out 2UI')    
    plt.show()
    plt.plot(vpval[0], label='y_0', color='g', alpha=.15)    
    plt.plot(vpval[1], label='y_0', color='b', alpha=.15)   
    plt.plot(vpval[2], label='y_0', color='r', alpha=.15)   
    plt.plot(vpval[3], label='y_0', color='k', alpha=.15) 
    plt.show()
    plt.plot(eqval, label='y_0', color='k', alpha=.15) 
    plt.show()
    plt.plot(tdval, label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('phase')    
    plt.show()
    #print(df.head(10))
    
    
    y4i=np.reshape(sumout, [int(len(sumout)/osr), osr])
    
    
    for k in range(int(len(y4i)/listlength)-1):    
        plt.plot(y4i[k], label='y_0', color='g', alpha=.15)    
        plt.grid()    
        plt.title('Eye Diagram of DFE Out 1UI')    
    plt.show()
    #eqtf = eqval[-1]/50*eqhftf+eqlftf
    #bode(series(eqtf, txtf, chtf), series(txtf, chtf), list(range(0,20)))
    
    y4i=np.reshape(rxin, [int(len(rxin)/osr), osr])
    for k in range(int(len(y4i)/listlength)-1):    
        plt.plot(y4i[k], label='y_0', color='g', alpha=.15)    
        plt.grid()    
        plt.title('Eye Diagram of RX Input 1UI')    
    plt.show()
    #eqtf = eqval[-1]/50*eqhftf+eqlftf
    #bode(series(eqtf, txtf, chtf), series(txtf, chtf), list(range(0,20)))    
    
