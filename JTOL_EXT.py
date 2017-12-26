import csv
import pandas as pd
import xlrd
import codecs



def extData(line):
    rst=[]
    freq=''
    data = line.decode('utf-8').split(',')
    if len(data) >3 and '\x00"\x00P\x00A\x00S\x00S\x00"\x00\n' in data:
        for item in data[0]:
            if not(item=='\x00'):
                din = (item.encode("utf-8", "replace")).decode("utf-8", "replace")
                freq = freq+din
            #rst.append(din)
        amp=''
        for item in data[1]:
            if not(item=='\x00'):
                din = (item.encode("utf-8", "replace")).decode("utf-8", "replace")
                amp = amp+din
            #rst.append(din)
        rst=[int(freq), float(amp)]
        print(rst)
        return rst


def csv2msk(cfile):
    msk = {
        'freq': [],
        'amp': []
    }
    with open(cfile) as fin:
        for line in fin:
            if line == None or line.find('\x00'):
                continue
            else:
                rst = extData(line.encode('utf-8'))
                if rst == None:
                    continue
                msk['freq'].append(rst[0])
                msk['amp'].append(rst[1])
        #print(msk)
        return msk

def filABpoint(din, lst):
    for freq in lst:
        pos = din['freq'].index(freq)
        din['freq'].remove(din['freq'][pos])
        din['amp'].remove(din['amp'][pos])
    return din



if __name__ == '__main__':
    cfile = "D:\proj\CPHY_12FF\LVDS_TEST\LVDS_BERT\LVDS_5P2G\VGAEQ00_CDR7_ber-10_500M_5mUIRJ5mUIBUJ.csv"
    dfile = "D:\proj\CPHY_12FF\LVDS_TEST\LVDS_BERT\LVDS_5P2G\VGAEQ00_CDR7_ber-10_500M_5mUIRJ5mUIBUJ_T.csv"

    m={}
    m=csv2msk(cfile)
    #print(m)
