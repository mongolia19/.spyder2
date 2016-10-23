# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 22:14:04 2015

@author: mongolia19
"""

from nltk.corpus import wordnet as wn
wordAList = wn.synset('thin.a.02')
print wordAList
#keyA = wordAList[0]
wordBList = wn.synsets('fat')
print wordBList
keyB = wordBList[0]
wordCList = wn.synsets('people')
keyC = wordCList[0]

#print keyA
#print keyB
#print keyC

score = wordAList.path_similarity(keyB)
print wn.lemma('fat.a.01.fat').antonyms()
#scoreA = keyC.path_similarity(keyB)
print score