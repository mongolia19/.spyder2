# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 11:51:52 2015

@author: mongolia19
"""

import numpy as np

X = np.array([[-1, -1,0], [-2, -1,0], [1, 1,1], [2, 1,1]])
y = np.array([1, 1, 2, 2])
from sklearn.svm import NuSVC
clf = NuSVC()
clf.fit(X, y) #doctest: +NORMALIZE_WHITESPACE

res=clf.predict([0.8, 1,1])
print res


import ystockquote

print ystockquote.get_price('002099.sz')
print ystockquote.get_all('002250.sz')
print "\r\n"

lis= ystockquote.get_historical_prices('002500.sz', "2014-09-19","2014-09-23")
print lis