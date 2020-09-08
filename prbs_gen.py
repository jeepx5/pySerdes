# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 16:30:27 2020

@author: -
"""

import numpy as np

from scipy import signal

import matplotlib.pyplot as mplt





class prbs_gen:

    def __init__(self, seed):

        self.seed = seed



    def prbs7(self):

        if len(self.seed) != 7:

            print("wrong input of seed or num")



        # x^7+x^6+1

        seq = self.seed

        while len(seq) <= 127:

            seq.insert(0, seq[5] ^ seq[6])
        seq = (seq-np.ones(len(seq))*0.5)*2

        return seq



    def prbs15(self):

        if len(self.seed) != 15:
            print(len(self.seed))
            print("wrong input of seed or num")



        # x^15+x^14+1

        seq = self.seed

        while len(seq) <= 2 ** 15 - 1:

            seq.insert(0, seq[13] ^ seq[14])
        seq = (seq-np.ones(len(seq))*0.5)*2

        return seq



    def prbs_ext(self, din, n):

        dintmp=np.array(din)

        dintmplst=dintmp.T.repeat(n)

        print(dintmplst)

        return dintmplst







class eyeplt:

    def __init__(self, seqin, eyenum):

        self.seqin = seqin

        self.eyenum = eyenum



    def iplt(self):

        seq_i = self.seqin

        seq_i = np.reshape(seq_i, (len(seq_i) // 4, 4))

        n = 0

        while n <= 31:

            mplt.plot(seq_i[n], 'r')

            n = n + 1
