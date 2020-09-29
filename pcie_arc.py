# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 14:04:38 2020

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


class pcie_ch():
    
    def __init__(self, osr, prbslsb, dr):
        '''        
        Parameters
        ----------
        osr : int
            oversampling rate = PI resolution.
        prbslsb : list
            lsb prbs list.
        prbsmsb : list
            msb prbs list.
        dr : int
            datarate.
        txtf : scipy obj
            tx transfer function.
        chtf : scipy obj
            ch transger function.

        Returns
        -------
        None.

        '''
        self.osr = osr
        self.prbslsb = prbslsb
        self.dr = dr
        
    def txch(self, txtf, chtf, listlength):
        osr = self.osr
        if (len(self.prbslsb) == 7):
            print('preparing prbs7 pattern')
            prbsgen_lsb=prbs_gen(self.prbslsb)
            prbslst_lsb=prbsgen_lsb.prbs7()
            
        elif (len(self.prbslsb) == 15):   
            print('preparing prbs15 pattern')
            prbsgen_lsb=prbs_gen(self.prbslsb)
            prbslst_lsb=prbsgen_lsb.prbs15()
            
        else:
            print("wrong length prbs seeds")
                    
        
        ####################
        # for NRZ
        prbs2x=prbslst_lsb
        ####################
        prbs_os=prbsgen_lsb.prbs_ext(prbs2x, osr)
        tt = np.linspace(0, len(prbs_os), len(prbs_os))        
        dr=self.dr        
        dt=1/osr       
        tt=tt*dt
        syst=series(txtf, chtf)
        y, t, x =lsim(syst, prbs_os, tt)
        print('tx output done!!!!!!!!!')
        return y, t
    
    def txFFE(self, datain, pre_cur, post_cur):
        main_cur =1+pre_cur+post_cur
        rxdfin = pd.DataFrame({"pre":rxin,
                           "main":rxin,
                           "post":rxin})
        rxindf = pre_cur*rxdfin["pre"] \
            +main_cur*rxdfin["main"].shift(1*osr, axis = 0) \
            +post_cur*rxdfin["post"].shift(2*osr, axis = 0)
    
        rxindf = rxindf.dropna().values.tolist()
        return rxindf
    
    def rxCtle(self, datain, wp1, wp2, Adc_db):
        normpole=2*np.pi*2.1e9/self.dr #50 ohm and 1.5pF
        numrx = [1]    
        den = [1/normpole, 1]
        denrx = [1]
        rxtf = tf(numrx, denrx)
        Adc = 10**(Adc_db/20)
        num = [wp2, wp2*wp1*Adc]
        dem = [1, wp1+wp2, wp1*wp2]
        tfctle = tf(num, dem)
        
        syst=series(rxtf, tfctle)
        tt = np.linspace(0, len(datain), len(datain))        
        dr=self.dr        
        dt=1/osr       
        tt=tt*dt
        #bode(syst)
        y, t, x =lsim(syst, datain, tt)
        print('ctle output done!!!!!!!!!')
        return y, t
    
    
    
    def eyePlt(self, rxindf, osr, plt_title):
            plt.figure(2)
            y4i=np.reshape(rxindf, [int((len(rxindf))/osr/2), osr*2])
            for k in range(int(len(y4i)/listlength)-1):    
                plt.plot(y4i[k], label='y_0', color='g', alpha=.15)    
                plt.grid()    
                plt.title(plt_title)    
            plt.show()
    
    
    
    
    def rxCDR(self, y4i, vpscale, initphase):
        '''
        Parameters
        ----------
        y4i : list
            rxinput.
        vpscale : float
            gain.

        Returns
        -------
        None.

        '''
        ##########################
        #### MMSE PD CDR #########
        ##########################
        dm3 = 0
        dm2 = 1
        errm2 = 0
        dm1 = 1
        errm1 =0
        rxtd = int(initphase)
        rxtdreal = initphase
        tdval = []
        ysample0=[]
        ysample1=[]
        errval = []
        dataval = []
        vpval1 =[]
        vpscale = 0.4
        vp1 = 1*vpscale
        vpval2 =[]
        vp2 = 1*vpscale
        vpval3 =[]
        vp3 = 1*vpscale
        vpval0 =[]
        vp0 = 1*vpscale
        osr = self.osr
        y4i=np.reshape(y4i, [int(len(y4i)/osr), osr])
        h1 = []
        h1val = 0.1
        #h2 = []
        h2val = 0.05
        h3val = 0.025
        em1 = 1
        for k in range(len(y4i)-3):
            plt.figure(1)
            plt.plot( y4i[k], label='y_0', color='r', alpha=.15)
            tnow = rxtd
            tedge = int(np.mod(tnow+osr/2, osr))
            ifnext = int((tnow+osr/2)/osr)
            y4i[k] = y4i[k]-dm1*(h1val)-dm2*(h2val)-dm3*(h3val)
            #y4i[k][tnow] = y4i[k][tnow]
            
            if (y4i[k][tnow] <0):
                d0 = -1
                err = 0
                ysample0.append(y4i[k][tnow])
                
            elif (y4i[k][tnow] >= 0):
                d0 = 1
                err = np.sign(y4i[k][tnow]-vp0)#*np.sign(d0)
                vp0 = vp0+0.0125*(err)
                ysample1.append(y4i[k][tnow])               
               
            if (y4i[int(k+ifnext)][tedge] >= 0):
                edge0 =1
                
            elif (y4i[int(k+ifnext)][tedge] < 0):
                edge0 = -1
            
            if (dm1 == d0):
                dstep = 0
            else:
                dstep = dm1*em1            
                
            dvstep1 = np.sign(err*d0)*np.sign(dm1)
            dvstep2 = np.sign(err*d0)*np.sign(dm2)         
            dvstep3 = np.sign(err*d0)*np.sign(dm3)                    
            #dvstep = np.sign(err*d0)*np.sign(dm1)
            h1val = h1val+dvstep1*0.00625
            if (h1val < 0): h1val = 0
            h2val = h2val+dvstep2*0.00125
            if (h2val < 0): h2val = 0
            h3val = h2val+dvstep3*0.000625
            if (abs(h3val) >= 0.05): h3val = 0.05*np.sign(h3val)
            rxtdreal =((rxtdreal+0.125*dstep+np.random.rand()/osr/4)%len(y4i[1]))
            #added jitter, without jitter the pd will lock to wrong phases
            rxtd =int(rxtdreal)
            tdval.append(tnow)
         
            h1.append(h1val)    
            errval.append(err)
            dataval.append(d0)
            dm2 = dm1
            errm2 = errm1
            dm1 = d0
            errm1=err
            em1 = edge0
            vpval1.append(h3val)
            vpval2.append(h1val)
            vpval3.append(h2val)
            vpval0.append(vp0)
            plt.figure(2)
            if (k>10000):
                plt.plot( y4i[k], label='y_0', color='g', alpha=.15)    
        plt.grid()    
        plt.title('DFE out waveform')    
        
        plt.show()
            
        vpval = [vpval0, vpval1, vpval2, vpval3]
        ysample = [ysample0, ysample1]
        errmean = np.mean(errval)
        phasemean = np.mean(tdval[-3000:-1])
        return ysample, vpval, errmean, phasemean,h1, tdval






if __name__ == "__main__":
    osr=128 #when osr is 64, the cdr final lock point depends on initial point
    #seed_lsb=[1,0,1,1,0,1,0]
    seed_lsb=[1,0,1,1,0,1,0,1,0,1,1,0,1,0,1]
    dr = 16e9
    
    #channel desciption
    normpole=2*np.pi*2.1e9/dr #50 ohm and 1.5pF
    
    normchpole1=2*np.pi*12e9/dr
    normchzero1=2*np.pi*10.2e9/dr
    
    normchpole2=2*np.pi*12e9/dr
    normchpole3=2*np.pi*12e9/dr
    normchpole4=2*np.pi*12e9/dr
    normchpole5=2*np.pi*12e9/dr
    normchpole6=2*np.pi*12e9/dr
    
    num = [1]    
    den = [1/normpole, 1]
    
    numch1 = [1]      
    dench1 = [1/normchpole1/normchpole2, 1/normchpole1+1/normchpole2, 1]
    
    numch2 = [1]      
    dench2 = [1/normchpole3/normchpole4, 1/normchpole3+1/normchpole4, 1]

    numch3 = [1]      
    dench3 = [1/normchpole5/normchpole6, 1/normchpole5+1/normchpole6, 1]
  
    
    chtf1 = tf(numch1, dench1)
    chtf2 = tf(numch2, dench2)
    chtf3 = tf(numch3, dench3)
    txtf = tf(num, den)
    syst=series(chtf1, chtf2)
    chtf = series(syst, chtf3)
    listlength = 128#prbs7 =320, prbs15 =1
    # channel setting done
    #tx output sim & preset check
    pcie_tranceiver = pcie_ch(osr, seed_lsb, dr)
    rxin, t = pcie_tranceiver.txch(txtf, chtf, listlength)
    #rxin eyediagram without FFE
    
    #preset = [[0, -6/24], [0, -4/24], [0, -5/24], [0, -3/24],
    #          [0, 0], [-2/24, 0], [-3/24, 0], [-4/24, -6/24],
    #          [-4/24, -4/24],[-4/24, 0]]
    
    preset = [[0, -6/24], [0, -4/24], [0, -5/24], [0, -3/24],
              [0, 0], [-3/24, 0], [-3/24, 0], [-2/24, -5/24],
              [-3/24, -3/24],[-4/24, 0]]
    

    
    #preset = [[0, -9/36], [0, -6/36], [0, -7/36], [0, -5/36],
    #      [0, 0], [-4/36, 0], [-5/36, 0], [-4/36, -7/36],
    #      [-4/36, -4/36],[-6/36, 0]]
    
    
    #preset = [[0, -8/32], [0, -6/32], [0, -7/32], [0, -4/32],
    #          [0, 0], [-4/32, 0], [-4/32, 0], [-3/32, -7/32],
    #          [-4/32, -4/32],[-6/32, 0]]
    
    
    '''
    #
    pre_cur = -1/24
    post_cur = -8/24
 
    rxindf = pcie_tranceiver.txFFE(rxin, pre_cur, post_cur)
    #y4i=np.reshape(rxindf, [int((len(rxindf))/osr/2), osr*2])
    title = 'Eye Diagram of RX Input 1UI'
    pcie_tranceiver.eyePlt(rxindf, osr, title)
    '''
    
    '''
    # tx presets simulaiton
    for i in range(9):
        pre_cur = preset[i][0]
        post_cur = preset[i][1]
        print(20*np.log10(1-2*pre_cur-2*post_cur))
     
        rxindf = pcie_tranceiver.txFFE(rxin, pre_cur, post_cur)
        y4i=np.reshape(rxindf, [int((len(rxindf))/osr/2), osr*2])
        
        title = 'Preset'+str(i)
        #pcie_tranceiver.eyePlt(rxindf, osr, title)
        for k in range(int(len(y4i)/listlength)-1):    
            #plt.figure(i)    
            plt.subplot(431+i)
            plt.plot( y4i[k], label='y_0', color='g', alpha=.15)    
            plt.grid()    
            plt.title(title)    
            

    plt.show()
    
    presetlst = [4, 1, 0, 9, 8, 7, 5, 6, 3, 2]
    
    for i in presetlst:
        pre_cur = preset[i][0]
        post_cur = preset[i][1]
        vb = 1+2*pre_cur+2*post_cur
        va = 1+2*pre_cur
        vc = 1+2*post_cur
        #print(va, vb, vc,)
        print("|preset"+str(i)+"：|"+str(20*np.log10(vc/vb))+"|"+str(20*np.log10(vb/va))+"|")
    '''
    pre_cur = preset[7][0]
    post_cur = preset[7][1]
    
    rxindf = pcie_tranceiver.txFFE(rxin, pre_cur, post_cur)
    print('tx output waveform simulaiton done')
    pcie_tranceiver.eyePlt(rxindf, osr, 'ctle input')
    
    wp1 =2*np.pi*2e9/dr
    wp2 = 2*np.pi*16e9/dr
    Adc_db = -6
    ctleout, t = pcie_tranceiver.rxCtle(rxindf, wp1, wp2, Adc_db)
    # print('dc gain = ', Adc_db)
    title = 'ADC: '+str(Adc_db)
    # #pcie_tranceiver.eyePlt(rxindf, osr, title)
    pcie_tranceiver.eyePlt(ctleout, osr, title)
    
    '''
    for adc in range(-12, -5, 1):
        n=0
        ctleout, t = pcie_tranceiver.rxCtle(rxindf, wp1, wp2, adc)
        y4i=np.reshape(ctleout, [int((len(ctleout))/osr/2), osr*2])
        print('dc gain = %d', adc)
        title = 'ADC: '+str(adc)
        #plt.figure(n)
        #pcie_tranceiver.eyePlt(rxindf, osr, title)
        for k in range(int(len(y4i)/listlength)-1):                    
            plt.subplot(3,3, n+1)
            plt.plot( y4i[k], label='y_0', color='g', alpha=.15)    
            plt.grid()    
            plt.title(title)    
        n=n+1
        plt.show()
    '''
    initphase = 75
    ysample = []
    vpval = []
    errmean = []
    phasemean = []
    h1 = []
    tdval = []
    ysample, vpval, errmean, phasemean,h1, tdval = pcie_tranceiver.rxCDR(ctleout, 0.3, initphase)

    plt.plot(vpval[0], label='y_0', color='g', alpha=.15)    
    plt.plot(vpval[1], label='y_0', color='b', alpha=.15)   
    plt.plot(vpval[2], label='y_0', color='r', alpha=.15)   
    plt.plot(vpval[3], label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('Adaptive Threshold Voltage Value')    
    plt.show()
    plt.plot(ysample[0], label='y_0', color='g', alpha=.15)    
    plt.plot(ysample[1], label='y_0', color='b', alpha=.15)   
    plt.grid()    
    plt.title('Serdes Digital Out')    
    plt.show()
    plt.plot(h1, label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('H1')    
    plt.show()
    plt.plot(tdval, label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('phase')    
    plt.show()
     
    #############################
    #### Scan init phase    #####
    #############################
    #errlst = []
    # phlst = []
    # for phase in range(osr):
    #     rxin1 = deepcopy(ctleout)
    #     print(phase)
    #     ysample, vpval, errmean, phasemean,h1, tdval = pcie_tranceiver.rxCDR(rxin1, 0.4, initphase)

    #     print("err: ", errmean)
    #     print("phase: ",phasemean)
    #     #errlst.append(errmean)
    #     phlst.append(phasemean)
    
    # plt.plot(phlst, label='y_0', color='r', alpha=.5)    
    # plt.grid()
    # plt.title('mean phase')    
    # plt.show()
