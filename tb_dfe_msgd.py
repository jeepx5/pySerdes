from dfe_prbs_gen import prbs_gen
from dfe_prbs_gen import eyeplt
import numpy as np
from scipy import signal
import matplotlib.pyplot as mplt
from dfe import dfe

seed = [0, 1, 0, 0, 1, 1, 0]
pgen = prbs_gen(seed)
seqs = pgen.prbs7()
seqs = [i * 2 - 1 for i in seqs]
seqs = seqs * 12
sig = seqs
# chtaps = [0, 0, 0, 0, 0, 0.0, 0.6, 0.26, 0.18, 0.028, -0.026, 0, 0, 0.000 -0.000]
chtaps = [0, 0, 0, 0, 0, 0, 0.6, 0.2, 0.12, 0.008, -0.006, 0.003, -0.001, 0.001 - 0.006]

# chtaps = [0, 0.65, 0.4, 0 ]
filtered = signal.convolve(seqs, chtaps, mode='same')
n = 15
htaps = [[0.45] * (n + 1), [0.2] * (n + 1), [0.00] * (n + 1), [0.00] * (n + 1), [0.0] * (n + 1), [0.0] * (n + 1),
         [0.0] * (n + 1), [0.0] * (n + 1)]

vtaps = [[0.45] * (n + 1), [0.2] * (n + 1), [0.00] * (n + 1), [0.00] * (n + 1), [0.0] * (n + 1), [0.0] * (n + 1),
         [0.0] * (n + 1), [0.0] * (n + 1)]

do = [0] * n
ek = [0] * n
dsume = [0] * n
dsumo = [0] * (n + 1)
# dine=[filtered[i] for i in range(len(filtered)) if i%2==0]
# dino=[filtered[i] for i in range(len(filtered)) if i%2==1]

while n < len(filtered) - 4:
    if n % 2 == 0:
        dfe4tape = dfe(filtered[n], do[n - 9:n], htaps)
        dfe4tapeo = dfe(filtered[n + 1], do[n - 9:n], htaps)
        i = 1
        while i <= 7:
            vtap = dfe4tape.msgd(ek[-1], vtaps)
            #print(vtap[1], htaps[1][-1])
            vtaps[i].append(vtap[i])
            htaps[i].append(htaps[i][-1]-vtap[i])
            i = i + 1
        htaps[0].append( vtap[0])
        vtaps[0].append(vtap[0])
        dsume.append(dfe4tape.summer())
        dsume.append(dfe4tapeo.summer())
        do.append(dfe4tape.cmp(dsume[-2], 0))
        ek.append(dfe4tape.cmp(dsume[-2], htaps[0][n]) * (do[n] + 1) / 2)

    elif n % 2 == 1:
        dfe4tapo = dfe(filtered[n], do[n - 9:n], htaps)
        dfe4tapoe = dfe(filtered[n + 1], do[n - 9:n], htaps)
        i = 1
        while i <= 7:
            vtap = dfe4tapo.msgd(ek[-1], vtaps)
            vtaps[i].append(vtap[i])
            htaps[i].append(htaps[i][-1] - vtap[i])
            i = i + 1
        vtaps[0].append(vtap[0])
        htaps[0].append(vtap[0])
        dsumo.append(dfe4tapo.summer())
        dsumo.append(dfe4tapoe.summer())
        do.append(dfe4tapo.cmp(dsumo[-2], 0))
        ek.append(dfe4tapo.cmp(dsumo[-2], htaps[0][n]) * (do[n] + 1) / 2)
    #print(htaps[0][-1])
    #print(htaps[0][-1])
    n = n + 1

fig, (ax_win, ax_filt) = mplt.subplots(2, 1, sharex=True)
ax_win.plot(htaps[0])
ax_win.text(len(htaps[0]) - 100, htaps[0][-1], "vp:" + str(htaps[0][-200]))
ax_win.plot(htaps[1])
ax_win.text(len(htaps[0]) - 100, htaps[1][-1], "h1:" + str(htaps[1][-200]))
ax_win.plot(htaps[2])
ax_win.text(len(htaps[0]) - 100, htaps[2][-1], "h2:" + str(htaps[2][-200]))
ax_win.plot(htaps[3])
ax_win.text(len(htaps[0]) - 100, htaps[3][-1], "h3:" + str(htaps[3][-200]))
ax_win.plot(htaps[4])
ax_win.text(len(htaps[0]) - 100, htaps[4][-1], "h4:" + str(htaps[4][-200]))
'''
ax_win.plot(htaps[5])
ax_win.text(len(htaps[0])-100, htaps[5][-1], "h5:"+str(htaps[5][-200]))
ax_win.plot(htaps[6])
ax_win.text(len(htaps[0])-100, htaps[6][-1], "h6:"+str(htaps[6][-200]))
'''
ax_win.set_title('htaps:' + 'vp=' + str(chtaps[6]) + ' h1=' + str(chtaps[7]) \
                 + ' h2=' + str(chtaps[8]) + ' h3=' + str(chtaps[9]) \
                 + ' h4=' + str(chtaps[10]) + ' h5=' + str(chtaps[11]) \
                 + ' h6=' + str(chtaps[12]))
ax_win.margins(0, 0.1)
ax_win.grid(True)
ax_filt.plot(filtered)
ax_filt.plot(dsume)
ax_filt.set_title('far-end signal')
ax_filt.margins(0, 0.1)
fig.tight_layout()
fig.show()

f2 = mplt.figure(2)
seq_i = dsumo[-257:-1]
# print( len(seq_i)%4)
f2 = eyeplt(seq_i, 4)
f2.iplt()
mplt.show()
mplt.close('all')

'''
f3=mplt.figure(3)
seq_i=filtered[-257:-1]
#print( len(seq_i)%4)
f3=eyeplt(seq_i, 4)
f3.iplt()
mplt.show()
mplt.close('all')
'''
