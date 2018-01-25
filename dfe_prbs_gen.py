from prbs_gen import prbs_gen
import matplotlib.pyplot as mplt
from scipy import fft
import numpy as np
import math


seed = [0, 1, 0, 0, 1, 1, 0]
pgen = prbs_gen(seed)
seqs = pgen.prbs7()
seqs = [i * 2 - 1 for i in seqs]
#seqs = seqs * 12
t=[i*200e-12 for i in range(0,len(seqs))]
#print(math.floor(np.log2(len(t))))
seq_f=(fft(seqs,len(t)))
mplt.plot(seq_f)
#mplt.hist(seqs, bins=100, color='g', alpha=.3)
#mplt.hist(sj, bins=100, color='k', alpha=.3)
mplt.grid(True)

mplt.show()

