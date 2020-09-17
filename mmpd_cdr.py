# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 08:40:01 2020

@author: -
"""

from scipy import signal
import numpy as np
from control.matlab import *
import control
import matplotlib.pyplot as plt
from prbs_gen import prbs_gen
from eyediagram import bres_segment_count_slow, bres_curve_count_slow,random_trace


class pam4cdr():
    
    def __init__(self, osr, prbslsb, prbsmsb, dr):
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
        self.prbsmsb = prbsmsb
        self.dr = dr
        #self.txtf = txtf
        #self.chtf = chtf
        
    def txch(self, txtf, chtf, listlength):
        osr = self.osr
        if (len(self.prbslsb) == 7):
            print('preparing prbs7 pattern')
            prbsgen_lsb=prbs_gen(self.prbslsb)
            prbslst_lsb=prbsgen_lsb.prbs7()
            prbsgen_msb=prbs_gen(self.prbsmsb)
            prbslst_msb=prbsgen_msb.prbs7()
        elif (len(self.prbslsb) == 15):   
            print('preparing prbs15 pattern')
            prbsgen_lsb=prbs_gen(self.prbslsb)
            prbslst_lsb=prbsgen_lsb.prbs15()
            prbsgen_msb=prbs_gen(self.prbsmsb)
            prbslst_msb=prbsgen_msb.prbs15()
        else:
            print("wrong length prbs seeds")
                    
        prbslst_msb = [a *2 for a in prbslst_msb]
        #for PAM4
        prbs2x= [a + b for a,b in zip(prbslst_lsb, prbslst_msb)]*int(listlength)
        ####################
        # for NRZ
        #prbs2x=prbslst_lsb
        ####################
        prbs_os=prbsgen_lsb.prbs_ext(prbs2x, osr)
        tt = np.linspace(0, len(prbs_os), len(prbs_os))        
        dr=10e9        
        dt=1/osr       
        tt=tt*dt
        syst=series(txtf, chtf)
        y, t, x =lsim(syst, prbs_os, tt)
        print('tx output done!!!!!!!!!')
        return y, t
    
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
        dm2 = 1
        errm2 = 0
        dm1 = 1
        errm1 =0
        rxtd = int(initphase)
        rxtdreal = initphase
        tdval = []
        ysample0=[]
        ysample1=[]
        ysample2=[]
        ysample3=[]
        errval = []
        dataval = []
        vpval1 =[]
        vpscale = 0.6
        vp1 = -1*vpscale
        vpval2 =[]
        vp2 = 1*vpscale
        vpval3 =[]
        vp3 = 2*vpscale
        vpval0 =[]
        vp0 = -2*vpscale
        osr = self.osr
        y4i=np.reshape(y4i, [int(len(y4i)/osr), osr])
        h1 = []
        h1val = 0.1
        for k in range(len(y4i)-1):
            tnow = rxtd
            y4i[k] = y4i[k]-dm1*(h1val)
            y4i[k][tnow] = int(y4i[k][tnow]/6*64 )*6/64
            if ((vp1+vp0)/2< y4i[k][tnow] <= (vp1+vp2)/2):
                d0 = -1
                err = np.sign(y4i[k][tnow]-vp1)#*np.sign(d0)
                vp1 = vp1+0.05*(err)
                ysample1.append(y4i[k][tnow])
                
            elif ((vp1+vp2)/2 < y4i[k][tnow] <= (vp3+vp2)/2):
                d0 = 1
                err = np.sign(y4i[k][tnow]-vp2)#*np.sign(d0)
                vp2 = vp2+0.05*(err)
                ysample2.append(y4i[k][tnow])
            elif (y4i[k][tnow] > (vp3+vp2)/2):
                d0 =2
                err = np.sign(y4i[k][tnow]-vp3)#*np.sign(d0)
                vp3 = vp3+0.05*(err)
                ysample3.append(y4i[k][tnow])
            elif (y4i[k][tnow] < (vp1+vp0)/2):
                d0 = -2
                err = np.sign(y4i[k][tnow]-vp0)#*np.sign(d0)
                vp0 = vp0+0.05*(err)
                ysample0.append(y4i[k][tnow])
                
            if ((d0==1 or d0 == -1) and (np.sign(dm1) ==np.sign(d0))):
            #if ((d0!=dm1)):
                dvstep1 = np.sign(err*d0)*np.sign(dm1)
            else: dvstep1 = 0
            
            #if ((d0!=dm1) and (dm1 != dm2)):
            if ((d0==2 or d0 == -2) and (np.sign(dm1) ==np.sign(d0))):
                dvstep2 = np.sign(errm1*dm1)*np.sign(dm2)
            else: dvstep2 = 0
            dvstep = 0.5*(dvstep1+dvstep2)
            
            #dvstep = np.sign(err*d0)*np.sign(dm1)
            h1val = h1val-dvstep*0.00625
            if (h1val < 0): h1val = 0
            #dstep = (dm1*err-d0*errm1)+(dm2*err-d0*errm2)#reside h1 and h2
            dstep = (dm1*err-d0*errm1)
            #rxtdreal =((rxtdreal+0.25*dstep+np.random.rand()*0.0125)%len(y4i[1]))
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
            vpval1.append(vp1)
            vpval2.append(vp2)
            vpval3.append(vp3)
            vpval0.append(vp0)
            
        vpval = [vpval0, vpval1, vpval2, vpval3]
        ysample = [ysample0, ysample1, ysample2,ysample3]
        errmean = np.mean(errval)
        phasemean = np.mean(tdval[-3000:-1])
        return ysample, vpval, errmean, phasemean,h1, tdval
    
    def rxCDRmmse(self, y4i, vpscale, initphase):
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
        dm2 = 1
        errm2 = 0
        dm1 = 1
        errm1 =0
        rxtd = int(initphase)
        rxtdreal = initphase
        tdval = []
        ysample0=[]
        ysample1=[]
        ysample2=[]
        ysample3=[]
        errval = []
        dataval = []
        vpval1 =[]
        vpscale = 0.6
        vp1 = -1*vpscale
        vpval2 =[]
        vp2 = 1*vpscale
        vpval3 =[]
        vp3 = 2*vpscale
        vpval0 =[]
        vp0 = -2*vpscale
        osr = self.osr
        y4i=np.reshape(y4i, [int(len(y4i)/osr), osr])
        h1 = []
        h1val = 0.05
        for k in range(len(y4i)-1):
            tnow = rxtd
            y4i[k] = y4i[k]-dm1*h1val
            if ((vp1+vp0)/2< y4i[k][tnow] <= (vp1+vp2)/2):
                d0 = -1
                err = np.sign(y4i[k][tnow]-vp1)#*np.sign(d0)
                vp1 = vp1+0.025*(err)
                ysample1.append(y4i[k][tnow])
                
            elif ((vp1+vp2)/2 < y4i[k][tnow] <= (vp3+vp2)/2):
                d0 = 1
                err = np.sign(y4i[k][tnow]-vp2)#*np.sign(d0)
                vp2 = vp2+0.025*(err)
                ysample2.append(y4i[k][tnow])
            elif (y4i[k][tnow] > (vp3+vp2)/2):
                d0 =2
                err = np.sign(y4i[k][tnow]-vp3)#*np.sign(d0)
                vp3 = vp3+0.025*(err)
                ysample3.append(y4i[k][tnow])
            elif (y4i[k][tnow] < (vp1+vp0)/2):
                d0 = -2
                err = np.sign(y4i[k][tnow]-vp0)#*np.sign(d0)
                vp0 = vp0+0.025*(err)
                ysample0.append(y4i[k][tnow])
                
            if (d0==1 or d0 == -1 and dm1 != d0):
                dvstep = np.sign(err*d0)*np.sign(dm1)
            else: dvstep = 0
            #dvstep = np.sign(err*d0)*np.sign(dm1)
            h1val = h1val+dvstep*0.00625
            if (h1val <0): h1val = 0
            #dstep = (dm1*err-d0*errm1)+(dm2*err-d0*errm2)#reside h1 and h2
            slope = np.sign(d0-dm2)
            dstep = slope*np.sign(errm1)
            #rxtdreal =((rxtdreal+0.25*dstep+np.random.rand()*0.0125)%len(y4i[1]))
            rxtdreal =((rxtdreal-0.25*dstep+np.random.rand()*0.0)%len(y4i[1]))
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
            vpval1.append(vp1)
            vpval2.append(vp2)
            vpval3.append(vp3)
            vpval0.append(vp0)
            
        vpval = [vpval0, vpval1, vpval2, vpval3]
        ysample = [ysample0, ysample1, ysample2,ysample3]
        errmean = np.mean(errval)
        phasemean = np.mean(tdval[-3000:-1])
        return ysample, vpval, errmean, phasemean,h1, tdval
    
    def rxCDReq(self, dfin, vpscale, initphase):
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
        dm2 = 1
        errm2 = 0
        dm1 = 1
        errm1 =0
        dm3 = 1
        errm3 = 0
        dm4 = 1
        errm4 =0
        dm5 = 1
        errm5 = 0
        dm6 = 1
        errm6 =0
        rxtd = int(initphase)
        rxtdreal = initphase
        tdval = []
        ysample0=[]
        ysample1=[]
        ysample2=[]
        ysample3=[]
        errval = []
        dataval = []
        vpval1 =[]
        vpscale = 0.6
        vp1 = -1*vpscale
        vpval2 =[]
        vp2 = 1*vpscale
        vpval3 =[]
        vp3 = 2*vpscale
        vpval0 =[]
        vp0 = -2*vpscale
        osr = self.osr
        eqval = 3
        eqstep = 0
        eqvalreal=eqval    
        h1 = []
        h1val = 0.05
        yout = []
        eqlst = []
        for k in range(int(len(list(dfin[eqval]))/osr)-1):
            y4i = list(dfin[3])
            #print(y4i)
            y4i=np.reshape(y4i, [int(len(y4i)/osr), osr])
        
            tnow = rxtd
            
            y4i[k] = y4i[k]-dm1*h1val
            if ((vp1+vp0)/2< y4i[k][tnow] <= (vp1+vp2)/2):
                d0 = -1
                err = np.sign(y4i[k][tnow]-vp1)#*np.sign(d0)
                vp1 = vp1+0.05*(err)
                ysample1.append(y4i[k][tnow])
                
            elif ((vp1+vp2)/2 < y4i[k][tnow] <= (vp3+vp2)/2):
                d0 = 1
                err = np.sign(y4i[k][tnow]-vp2)#*np.sign(d0)
                vp2 = vp2+0.05*(err)
                ysample2.append(y4i[k][tnow])
            elif (y4i[k][tnow] > (vp3+vp2)/2):
                d0 =2
                err = np.sign(y4i[k][tnow]-vp3)#*np.sign(d0)
                vp3 = vp3+0.05*(err)
                ysample3.append(y4i[k][tnow])
            elif (y4i[k][tnow] < (vp1+vp0)/2):
                d0 = -2
                err = np.sign(y4i[k][tnow]-vp0)#*np.sign(d0)
                vp0 = vp0+0.05*(err)
                ysample0.append(y4i[k][tnow])
                
            if ((d0==1 or d0 == -1) and (np.sign(dm1) ==np.sign(d0))):
            #if ((d0!=dm1)):
                dvstep1 = np.sign(err*d0)*np.sign(dm1)
            else: dvstep1 = 0
            
            #if ((d0!=dm1) and (dm1 != dm2)):
            if ((d0==2 or d0 == -2) and (np.sign(dm1) ==np.sign(d0))):
                dvstep2 = np.sign(errm1*dm1)*np.sign(dm2)
            else: dvstep2 = 0
            dvstep = 0.5*(dvstep1+dvstep2)
            
            #dvstep = np.sign(err*d0)*np.sign(dm1)
            h1val = h1val-dvstep*0.00625
            #dstep = (dm1*err-d0*errm1)+(dm2*err-d0*errm2)#reside h1 and h2
            dstep = (dm1*err-d0*errm1)
            #rxtdreal =((rxtdreal+0.25*dstep+np.random.rand()*0.0125)%len(y4i[1]))
            rxtdreal =((rxtdreal+0.125*dstep+np.random.rand()*0.0)%len(y4i[1]))
            #added jitter, without jitter the pd will lock to wrong phases
            rxtd =int(rxtdreal)
            tdval.append(tnow)
            if ((dm1 >0 and d0<dm1) or (dm1<0 and d0>dm1)):
                eqstep = (dm6+dm5+dm4)*np.sign(errm1*dm1)/9
                eqvalreal = eqvalreal+0.00125*eqstep
                if (eqvalreal >15): eqvalreal = 15
                elif(eqvalreal <0): eqvalreal = 0
                eqval = int(eqvalreal)
                        
            eqlst.append(eqval)
            yout = yout+list(y4i[k])
            h1.append(h1val)    
            errval.append(err)
            dataval.append(d0)
            dm6 = dm5
            errm6 = errm5
            dm5 = dm4
            errm5 = errm4
            dm4 = dm3
            errm4 = errm3
            dm3 = dm2
            errm3 = errm2
            dm2 = dm1
            errm2 = errm1
            dm1 = d0
            errm1=err
            vpval1.append(vp1)
            vpval2.append(vp2)
            vpval3.append(vp3)
            vpval0.append(vp0)
            
        vpval = [vpval0, vpval1, vpval2, vpval3]
        ysample = [ysample0, ysample1, ysample2,ysample3]
        errmean = np.mean(errval)
        phasemean = np.mean(tdval[-3000:-1])
        return yout, ysample, vpval, errmean, phasemean,h1, tdval, eqlst



if __name__ == "__main__":
    osr=32 #when osr is 64, the cdr final lock point depends on initial point
    seed_lsb=[1,0,1,1,0,1,0]
    seed_msb=[1,1,0,1,0,0,1]
    #seed_lsb=[1,0,1,1,0,1,0,1,0,1,0,1,1,0,1]
    #seed_msb=[1,1,0,1,0,0,1,1,0,1,1,0,1,1,1]
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
    
    listlength = 512
    #syst=series(sys, sys2)
    pam4sys = pam4cdr(osr, seed_lsb, seed_msb, dr)
    rxin, t = pam4sys.txch(txtf, chtf, listlength)
    ti=t[0:osr*2]
    # add noise 
    shp=rxin.shape
    vrnd=np.random.rand(len(rxin))*0.125
    rxin=rxin+vrnd
    y4i=np.reshape(rxin, [int(len(rxin)/osr/2), osr*2])
    
    #######################
    #   Plot 2UI eyediagram   #
    #######################
    for k in range(int(len(y4i)/listlength)-1):    
        plt.plot(ti, y4i[k], label='y_0', color='g', alpha=.15)    
        plt.grid()    
        plt.title('Eye Diagram of Channel Out 2UI')    
    plt.show()
    
    #MMSEPD CDR #############################
    #ysample, vpval, errmean, phasemean,h1, tdval = pam4sys.rxCDRmmse(rxin, 0.6, 15)
    #MMPD CDR #############################
    ysample, vpval, errmean, phasemean,h1, tdval = pam4sys.rxCDR(rxin, 0.6, 16)
    #######################################
    print("err: ", errmean)
    print("phase: ",phasemean)
    y4i=np.reshape(rxin, [int(len(rxin)/osr), osr])
    for k in range(int(len(y4i)/listlength)-1):    
        plt.plot(y4i[k], label='y_0', color='g', alpha=.15)    
        plt.grid()    
        plt.title('Eye Diagram of Channel Out 2UI')    
    plt.show()
    plt.plot(vpval[0], label='y_0', color='g', alpha=.15)    
    plt.plot(vpval[1], label='y_0', color='b', alpha=.15)   
    plt.plot(vpval[2], label='y_0', color='r', alpha=.15)   
    plt.plot(vpval[3], label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('Eye Diagram of Channel Out 2UI')    
    plt.show()
    plt.plot(ysample[0], label='y_0', color='g', alpha=.15)    
    plt.plot(ysample[1], label='y_0', color='b', alpha=.15)   
    plt.plot(ysample[2], label='y_0', color='r', alpha=.15)   
    plt.plot(ysample[3], label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('Eye Diagram of Channel Out 2UI')    
    plt.show()
    plt.plot(h1, label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('H1')    
    plt.show()
    plt.plot(tdval, label='y_0', color='k', alpha=.15)   
    plt.grid()    
    plt.title('phase')    
    plt.show()
