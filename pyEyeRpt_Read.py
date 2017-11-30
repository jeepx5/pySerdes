import os
from bs4 import BeautifulSoup
import re
import pandas as pd



def ptRemove(pt):
    p=re.sub(r'<font size="2">', '', pt)
    restmp=re.sub(r'</font>', '', p)
    restmp2 = re.sub(r' Edges =&gt; Signal Type: AUTO, Clock Edge: Rising | Clock Recovery =&gt; ', '', restmp)
    restmp3=re.sub(r"Known Data Pattern: Off, Pattern Filename: C:\\Users\\Public\\Tektronix\\Tekapplications\\DPOJET\\Patterns\\", '', restmp2)
    restmp4=re.sub(r'Max: 1ns, Min: -1ns, Custom Measurement Name: --', '', restmp3)
    restmp5 = re.sub(r' General =&gt; Measurement Range Limits: Off,', '', restmp4)
    res = re.sub(r'Filters =&gt; F1: Spec: No Filter, F2: Spec: No Filter', '', restmp5)
    return res

def getData(soup, fname):
    i = 0
    dataStructure = {}
    dataStructure['corner'] = fname
    for item in soup.findAll('font'):
        # print(item)
        if (i == 2):
            pt = ptRemove(str(item))
            dataStructure['Scope Model'] = pt
        if (i == 73):
            pt = ptRemove(str(item))
            dataStructure['CDR_Setting'] = pt
        if (i == 347):
            pt = ptRemove(str(item))
            dataStructure['Tie_PP'] = pt
        if (i == 348):
            pt = ptRemove(str(item))
            dataStructure['Cycle_num'] = pt
        if (i == 367):
            pt = ptRemove(str(item))
            dataStructure['RJstd'] = pt
        if (i == 423):
            pt = ptRemove(str(item))
            dataStructure['TJpp'] = pt
        if (i == 451):
            pt = ptRemove(str(item))
            dataStructure['DJpp'] = pt

        if (i == 563):
            pt = ptRemove(str(item))
            dataStructure['DCD'] = pt
        # print(i)
        i = i + 1

    return dataStructure


def getDataAcc(soup, fname):
    i = 0
    dataStructure = {}
    dataStructure['corner'] = fname
    for item in soup.findAll('font'):
        #print(item)
        if (i == 2):
            pt = ptRemove(str(item))
            dataStructure['Scope Model'] = pt
        if (i == 73):
            pt = ptRemove(str(item))
            dataStructure['CDR_Setting'] = pt
        if (i == 347):
            pt = ptRemove(str(item))
            dataStructure['Tie_PP'] = pt
        if (i == 348):
            pt = ptRemove(str(item))
            dataStructure['Cycle_num'] = pt
        if (i == 367):
            pt = ptRemove(str(item))
            dataStructure['RJstd'] = pt
        if (i == 423):
            pt = ptRemove(str(item))
            dataStructure['TJpp'] = pt

        if (i == 451):
            pt = ptRemove(str(item))
            dataStructure['DJpp'] = pt
        if (i == 563):
            pt = ptRemove(str(item))
            dataStructure['DCD'] = pt
        if ('Scope Model' in str(item)):
            print('in scope')
            i = 2
            continue
        elif('TJ@BER1,' in str(item)):
            print('in TJ')
            i=423
            continue
        elif ('RJ1,' in str(item)):
            print('in RJ')
            i = 367
            continue
        elif ('DJ1,' in str(item)):
            print('in DJ')
            i = 451
            continue
        elif ('DCD1,' in str(item)):
            print('in DCD')
            i = 563
            continue
        elif ('TIE1,' in str(item)):
            print('in tie')
            i = 347
            continue
        elif ('p-p,' in str(item)):
            print('pp')
            i = 348
            continue
        elif ('Clock Recovery' in str(item)):
            print('in cdr')
            pt = ptRemove(str(item))
            dataStructure['CDR_Setting'] = pt
            continue
        #i=i+1
    return dataStructure


#home='D:\\proj\\rf40\\navajo\\3595d eye\\3595d eye\\SR3595D_AB'



