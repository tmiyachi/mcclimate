#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import numpy as np
import csv
import getamedas
import pickle

getamedas.setproxy()

spotname = ["abashiri", "suttsu", "nemuro", "ishinomaki", "yamagata", "mito", "choshi", "iida", "nagano", "fushiki", "hikone", "sakai", "hamada", "tadotsu", "miyazaki", "naze", "ishigakijima"]
spotnum = [47409, 47421, 47420, 47592, 47588, 47629, 47648, 47637, 47610, 47606, 47761, 47742, 47755, 47890, 47830, 47909, 47918]

data = []
for i in range(17):
    print spotname[i]   
    templist = []
    templist.append(spotname[i])
    for yyyy in range(1979, 2011):
        for mm in range(6, 10):
            rec = getamedas2.getdaily(spotnum[i], yyyy, mm, 7)
            templist += [float(num) for num in rec]
    data.append(templist)
    
pickle.dump(data,open("dump.dump","w"))

#write csv
csvw = csv.writer(open('temp.csv', 'w'), lineterminator='\n')
csvw.writerow(zip(*data))
csvw.close()



