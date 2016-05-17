#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 2016-5-14
@author: isunchy
'''

import os

from datatransfer import transfer


for files in os.listdir('origindata'):
    fout = 'fendata/' + files
    transfer('origindata/' + files, fout)


fout = file('total.fen', 'w')
for files in os.listdir('fendata'):
    fin = open('fendata/' + files)
    feninfo = fin.read()
    fout.write(feninfo)
    fin.close()
fout.close()
    

