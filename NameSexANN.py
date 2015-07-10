# -*- coding: utf-8 -*-
"""
Created on Tue Jul 07 21:47:45 2015

@author: mongolia19
"""
import nltk
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.xml import networkwriter
from pybrain.tools.xml import networkreader
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import TanhLayer

#names = nltk.corpus.names
#print names.fileids()
#male_names = names.words('male.txt')
#female_names = names.words('female.txt')
#labelALength = len(male_names)
#labelBLength = len(female_names)
#print labelALength
#print labelBLength
#print [w for w in male_names if w in female_names]

from pybrain.datasets import SupervisedDataSet
def strToIntList(rawStr,MaxLen=15):
    rawStr = list(rawStr)
    chrList = list()
    for c in rawStr:
        chrList.append(ord(c))
    while len(chrList) < MaxLen:
        chrList.append(int(0))
    return chrList
InDem = 3
ds = SupervisedDataSet(InDem,1)

for j in range(0,10):  
    inputArray = [0,0,0]
    for i in range(0,len(inputArray)):
        inputArray[i] = j
    ds.addSample(inputArray,(-1)^j)
#for w in male_names:
#    w = list(w)
#    chrList = list()
#    for c in w:
#        chrList.append(ord(c))
#    while len(chrList) < InDem:
#        chrList.append(int(0))
#    ds.addSample(chrList,0)
#for w in female_names:
#    w = list(w)
#    chrList = list()
#    for c in w:
#        chrList.append(ord(c))
#    while len(chrList) < InDem:
#        chrList=[int(0)] + chrList
#    ds.addSample(chrList,1)
#['Abbey', 'Abbie', 'Abby', 'Addie', 'Adrian', 'Adrien', 'Ajay', 'Alex', 'Alexis',
#'Alfie', 'Ali', 'Alix', 'Allie', 'Allyn', 'Andie', 'Andrea', 'Andy', 'Angel',
#'Angie', 'Ariel', 'Ashley', 'Aubrey', 'Augustine', 'Austin', 'Averil', ...]
net = buildNetwork(InDem,8,6,2,1,bias=True, hiddenclass=TanhLayer)
print 'start training'
trainer = BackpropTrainer(net, ds,momentum=0., verbose=True, batchlearning=False,
                 weightdecay=0.)

trainer.trainUntilConvergence()
networkwriter.NetworkWriter.writeToFile(net, 'testNet.xml')
net = networkreader.NetworkReader.readFrom('testNet.xml')
for j in range(0,20):    
    print net.activate([j,j,j])
