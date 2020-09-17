# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 12:03:04 2020

@author: -
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

if __name__ == "__main__":
    osr=32 #when osr is 64, the cdr final lock point depends on initial point
    seed_lsb=[1,0,1,1,0,1,0]
    seed_msb=[1,1,0,1,0,0,1]
    #seed_lsb=[1,0,1,1,0,1,0,1,0,1,1,0,1,0,1]
    #seed_msb=[1,1,0,1,0,0,1,1,0,1,1,0,1,0,1]
    dr = 10e9
    
    normpole=2*np.pi*6.6e9/dr
    normtxpole2=2*np.pi*10e9/dr
    
    normtxpole1=2*np.pi*4e9/dr
    normtxzero=2*np.pi*5.2e9/dr
    
    num = [1]    
    den = [1/normpole/normpole, 1/normpole*2, 1]
    
    numtx = [1/normtxzero, 1]      
    dentx = [1/normtxpole1/normtxpole2, 1/normtxpole1+1/normtxpole2, 1]

    txtf = tf(numtx, dentx)
    chtf = tf(num, den)
    
    listlength = 512#prbs7 =320, prbs15 =1
    #syst=series(sys, sys2)

    pam4sys = pam4cdr(osr, seed_lsb, seed_msb, dr)
    
    rxin, t = pam4sys.txch(txtf, chtf, listlength)
    
    ################
    # add noise 
    shp=rxin.shape
    vrnd=np.random.rand(len(rxin))*0.125
    rxin=rxin+vrnd
    ################
    
    '''
    #######################
    #   Plot 2UI eyediagram   #
    #######################
    ti=t[0:osr*2]
    y4i=np.reshape(rxin, [int(len(rxin)/osr/2), osr*2])
    for k in range(int(len(y4i)/listlength)-1):    
        plt.plot(ti, y4i[k], label='y_0', color='g', alpha=.15)    
        plt.grid()    
        plt.title('Eye Diagram of Channel Out 2UI')    
    plt.show()
    '''
    errlst = []
    phlst = []
    errmean = 0
    phasemean = 0
    
    
    
    
    for phase in range(osr):
        rxin1 = deepcopy(rxin)
        print(phase)
        #ysample, vpval, errmean, phasemean,h1, tdval = pam4sys.rxCDRmmse(rxin1, 0.6, phase)
        ysample, vpval, errmean, phasemean,h1, tdval = pam4sys.rxCDR(rxin1, 0.6, phase)
        print("err: ", errmean)
        print("phase: ",phasemean)
        errlst.append(errmean)
        phlst.append(phasemean)
    '''
    ysample, vpval, errmean, phasemean = pam4sys.rxCDR(rxin, 0.6, 10)
    print(phasemean)
    '''
    #######################
    #   Plot 1UI eyediagram   #
    #######################
    ti=t[0:osr*2]    
    y4i=np.reshape(rxin, [int(len(rxin1)/osr), osr])
    
    
    for k in range(int(len(y4i)/listlength)-1):    
        plt.plot(y4i[k], label='y_0', color='g', alpha=.15)    
        plt.grid()    
        plt.title('Eye Diagram of Channel Out 2UI')    
    plt.show()
    
    plt.plot(errlst, label='y_0', color='r', alpha=.5)    
    plt.grid()
    plt.title('mean error')    
    plt.show()
    
    plt.plot(phlst, label='y_0', color='r', alpha=.5)    
    plt.grid()
    plt.title('mean phase')    
    plt.show()
    
    plt.plot(vpval[0], label='vp_0', color='g', alpha=.5)
    plt.plot(vpval[1], label='vp_1', color='b', alpha=.5)
    plt.plot(vpval[2], label='vp_2', color='r', alpha=.5)
    plt.plot(vpval[3], label='vp_3', color='k', alpha=.5)
    plt.title('Vp0to3')
    plt.grid()
    plt.show()

    plt.plot(ysample[0], label='vp_0', color='g', alpha=.5)
    plt.plot(ysample[1], label='vp_1', color='b', alpha=.5)
    plt.plot(ysample[2], label='vp_2', color='r', alpha=.5)
    plt.plot(ysample[3], label='vp_3', color='k', alpha=.5)
    plt.title('Vp0to3')
    plt.grid()
    plt.show()
    
    plt.plot(h1, label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('H1')    
    plt.show()
    
    plt.plot(tdval, label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('phase')    
    plt.show()
