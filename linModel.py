import numpy as np
from scipy import signal
import matplotlib.pyplot as mplt


class linModel():
    def __init__(self):
        print('initializing Linear Model')

    def cdrStb(self, EO, DR, Tdelay, Kp, Kf, Divp, Divf, Npi, CDRint, dj):
        Kpd=1/(dj*np.sqrt(2*np.pi))
        #Kpd = 1/dj
        A = Kpd * Kp / Divp / Npi
        B = DR / CDRint
        C = Kf / Divf / Kp
        x = np.logspace(5, 8, num=1000, endpoint=True, base=10., dtype=None)
        x=x*5
        # convert f to w
        f2w = np.vectorize(lambda f: 2 * np.pi * f * complex(0, 1))
        s = f2w(x)
        # done without for loop
        # calc tf
        hsdb = lambda si: 20 * np.log10(abs((A * B / si + A * B * B * C / si / si) * (np.e ** (Tdelay / DR * -1 * si))))
        # hsdb=lambda si:20*np.log10(abs((A*B/si+A*B*B*C/si/si)*np.e**(Tdelay*-1/si*2*np.pi)))
        hodb_func = np.vectorize(hsdb)
        hodb = hodb_func(s)
        hsph = lambda si: np.angle(
            ((A * B / si + A * B * B * C / si / si) * np.e ** (Tdelay / DR * -1 * si))) / np.pi * 180
        hoph_func = np.vectorize(hsph)
        hoph = hoph_func(s)
        jtol_tf = lambda si: +EO / (abs(1 / (1 + ((A * B / si + A * B * B * C / si / si) * np.e ** (Tdelay / DR * -1 * si)))))-(EO-0.75)/12

        jtol_func = np.vectorize(jtol_tf)
        jtol = jtol_func(s)
        # mag & ph done
        '''
        Hspl=np.zeros((1, len(x)))
        hs=[]
        hscl=[]
        Jtol=[]
        hodb=[]
        hoph=[]
        '''
        hs = lambda si: 20 * np.log10(
            abs((A * B / si + A * B * B * C / si / si) * np.e ** (Tdelay * -1 / si * 2 * np.pi)))
        return hodb, hoph, x, jtol

    def jtol(self, jtolmask, jtol, jtol_real, x):
        fig1 = mplt.figure(1)
        # mplt.subplot(2,1,1)
        mplt.loglog(x, jtol, color='blue', lw=2)
        #mplt.loglog(jtolmask[0], jtolmask[1], color='red', lw=4)
        mplt.loglog(jtol_real[0], jtol_real[1], color='k', lw=2)
        mplt.grid(True)
        mplt.show()

