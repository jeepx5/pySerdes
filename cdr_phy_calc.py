import numpy as np
from scipy import signal
import matplotlib.pyplot as mplt
from linModel import linModel
from JTOL_EXT import csv2msk, filABpoint
import numpy as np

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
lst=[1,2,3,5,6,7,9,10,11]
exlst=['A','B','C','D','E','F']

pltn=1
#===calibration============
fin="D:\\proj\\CPHY_12FF\\LVDS_TEST\\1231\\bert2nd10M.csv"
callist=bertCal(fin)
#====cal list gen==========

for cdrset in lst:
    pgain=np.mod(cdrset, 4)

    fgain=np.floor((cdrset-pgain)/4)
    print(pgain, fgain)
    hodb, hoph, freq, jtol = cdrph.cdrStb(0.77, 5.2e9, 36, 2**(pgain+2), 2**(fgain), 2 ** 6, 2 ** 6, 32, 4, 0.183)#20/1000*5.2)

    #jtolmask = [[500e3, 1e6, 2e6, 4.9e6, 50e6], [0, 0, 0, 0, 0]]
    #jtolmask = [[500e3, 1e6, 2e6, 4.9e6, 50e6], [2, 1, 0.5, 0.2, 0.2]]
    #pth="D:\proj\CPHY_12FF\LVDS_TEST\LVDS_BERT\LVDS_5P2G\VGAEQ00_CDR"
    #fname = "_ber-10_500M_5mUIRJ5mUIBUJ.csv"
    #pth='D:\\proj\\CPHY_12FF\\LVDS_TEST\\lvds\\CDR_'
    #fname='704.csv'
    pth='D:\\proj\\CPHY_12FF\\LVDS_TEST\\1231\\lvds'
    fname='704_2nd10M.csv'


    pth4M='D:\\proj\\CPHY_12FF\\LVDS_TEST\\LVDS_5P2G\\VGAEQ00_CDR'
    fname4M="_ber-10_500M_5mUIRJ5mUIBUJ.csv"
    if cdrset < 10:
        cfile = pth+str(cdrset)+fname
        cf4M=pth4M+str(cdrset)+fname4M
    else:
        cdrpos=cdrset - 10
        cfile=pth+str(exlst[cdrpos])+fname
        cf4M = pth4M + str(exlst[cdrpos]) + fname4M
    m={}
    m4m={}
    m=csv2msk(cfile)
    lst=[]
    #m=filABpoint(m, [10414058,22588636])

    mcal=np.array(m['amp'])+np.array(callist['amp'])

    jtolreal=[m['freq'], mcal]

    jtol4M=[m['freq'],m['amp']]
    #cdrph.jtol(jtolmask, jtol, jtolreal, freq)
    fig1 = mplt.figure(1)
    mplt.subplot(3,3,pltn)
    lms, = mplt.loglog(jtolreal[0], jtolreal[1], 'g^--', lw=2, label='after_cal')
    lmd, =mplt.loglog(freq, jtol, color='blue', lw=2, label='model')
    lmk, = mplt.loglog(jtol4M[0], jtol4M[1], 'r+--', lw=2, label='before_cal')
    #lmk,=mplt.loglog(jtolmask[0], jtolmask[1], color='red', lw=4, label='mask')
    mplt.legend(handles=[lmd,lmk,lms])
    #mplt.legend(handles=[lmd, lms])

    mplt.title('2e2 setting is '+str(cdrset), fontsize=10)
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



