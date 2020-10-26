#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 23:55:25 2020

@author: jguterl
"""

filename='/home/jguterl/Dropbox/UEDGEdev/UEDGE/ppp/ListVariableThreadPrivate_final.txt'
file='/home/jguterl/Dropbox/UEDGEdev/UEDGE/com/com.v'
#file='/home/jguterl/Dropbox/UEDGEdev/UEDGE/com/com.v'
fd=open(filename, 'r+')
listVar = fd.readlines()
listVar=[c.strip() for c in listVar]
fd.close()
with open(file, 'r+') as fd:
    contents = fd.readlines()
    cts=[]
    for c in contents:
        print(">>>",c)
        s=c.strip(' ').split()
        if len(s)!=0:
           s=s[0].split('(')
           if len(s)!=0:
               s=s[0]
        if s in listVar:
            idx=c.find('#')
            c = c[:idx] + ' threadprivate ' + c[idx:]
        cts.append(c)
    fd.seek(0)
    fd.writelines(cts)

