import numpy as np
from scipy import signal
import matplotlib.pyplot as mplt
from linModel import linModel
from JTOL_EXT import csv2msk, filABpoint, csv2mskUP


def bertCal(fin):
    mbert = csv2msk(fin)
    calbert = mbert['amp']
    deo=1-calbert[-1]
    #print(mbert['amp'])
    mbert['amp']=[deo for i in calbert if (i+deo) >1.1]
    mbert['amp']=mbert['amp']+[1-i for i in calbert if (i+deo) <=1.1]
    #print(mbert['amp'])
    return mbert





cdrph = linModel()
lst=[3,5,6,7]
exlst=['A','B','C','D','E','F']

rjlst=[1,2,3]
pltn=1
#===calibration============
#fin="D:\\proj\\CPHY_12FF\\LVDS_TEST\\1231\\bert2nd10M.csv"
#callist=bertCal(fin)
#====cal list gen==========
for cdrset in lst:

    for rjsrc in rjlst:
        pgain=np.mod(cdrset, 4)

        fgain=np.floor((cdrset-pgain)/4)
        #pgain=3
        #fgain=1
        print(pgain, fgain)
        rjtt=np.sqrt(0.083*0.083+rjsrc*rjsrc/100/100)
        print(rjtt)
        eo=0.75-12*(rjsrc/100)
        print(eo)
        hodb, hoph, freq, jtol = cdrph.cdrStb(eo, 5.2e9, 26, 2**(pgain+2), 2**(fgain), 2 ** 6, 2 ** 6, 32, 4,
                                              rjtt)#20/1000*5.2)

        #jtolmask = [[500e3, 1e6, 2e6, 4.9e6, 50e6], [0, 0, 0, 0, 0]]
        #jtolmask = [[500e3, 1e6, 2e6, 4.9e6, 50e6], [2, 1, 0.5, 0.2, 0.2]]
        #pth="D:\proj\CPHY_12FF\LVDS_TEST\LVDS_BERT\LVDS_5P2G\VGAEQ00_CDR"
        #fname = "_ber-10_500M_5mUIRJ5mUIBUJ.csv"
        #pth='D:\\proj\\CPHY_12FF\\LVDS_TEST\\lvds\\CDR_'
        #fname='704.csv'
        pth='D:\\proj\\CPHY_12FF\\LVDS_TEST\\20180112_phyd+phya\\20180112_phyd+phya\\cdr'
        cdr_reg='704_RJ'
        fname='0mUI.csv'



        if cdrset < 10:
            cfile = pth+str(cdrset)+cdr_reg+str(rjsrc)+fname

        else:
            cdrpos=cdrset - 10
            cfile=pth+str(exlst[cdrpos])+cdr_reg+str(rjsrc)+fname

        m={}
        m=csv2mskUP(cfile)
        lst=[]
        #m=filABpoint(m, [10414058,22588636])

        jtolreal=[m['freq'], m['amp']]

        #cdrph.jtol(jtolmask, jtol, jtolreal, freq)
        fig1 = mplt.figure(1)
        mplt.subplot(4,3,pltn)
        lms, = mplt.loglog(jtolreal[0], jtolreal[1], 'g^--', lw=2, label='after_cal')
        lmd, =mplt.loglog(freq, jtol, color='blue', lw=2, label='model')
        #lmk,=mplt.loglog(jtolmask[0], jtolmask[1], color='red', lw=4, label='mask')
        mplt.legend(handles=[lmd,lms])
        #mplt.legend(handles=[lmd, lms])

        mplt.title('reg: '+str(cdrset)+'  RJ='+str(rjsrc)+'0mUI', fontsize=10)
        mplt.grid(True)
        pltn+=1

mplt.show()


# pi analog delay1.2ns(6UI), des=5UI, PI dig=4UI, slicer=1UI

'''open loop bode plot
try:
    ind = np.ndarray.tolist(hodb).index(-1 * min(np.ndarray.tolist(np.absolute(hodb))))
except:
    ind = np.ndarray.tolist(hodb).index(1 * min(np.ndarray.tolist(np.absolute(hodb))))



print('PM = ', 180 + np.ndarray.tolist(hoph)[ind])
print('BW = ', format(freq[ind], '.2e'))

# print(type(hodb))
# print(np.where(hodb==np.abs(hodb).min()))

fig1 = mplt.figure(1)
mplt.subplot(2, 1, 1)
mplt.semilogx(freq, hodb, color='blue', lw=2)
mplt.annotate(format(freq[ind], '.2e'), xy=(freq[ind], 0), xytext=(freq[ind], 12),
              arrowprops=dict(facecolor='black', shrink=0.005),
              )
mplt.grid(True)
mplt.subplot(2, 1, 2)
mplt.semilogx(freq, hoph, color='red', lw=2)
mplt.annotate(format(180 + np.ndarray.tolist(hoph)[ind], '.2f'), xy=(freq[ind], np.ndarray.tolist(hoph)[ind]),
              xytext=(freq[ind], np.ndarray.tolist(hoph)[ind] - 20),
              arrowprops=dict(facecolor='black', shrink=0.005),
              )

mplt.grid(True)

mplt.show()

end open loop bode plot'''



