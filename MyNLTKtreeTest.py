# -*- coding: utf-8 -*-
"""
Created on Mon Apr 06 23:32:43 2015

@author: mongolia19
"""

#import nltk.tree
import  xml.dom.minidom
from articaleClassification import expository
CONST_PATTERN = 'pattern'
#nltk.tree.demo()
#dom = xml.dom.minidom.parse("expositoryFormat.xml")
#root = dom.documentElement
#patternList = root.getElementsByTagName(CONST_PATTERN)
##print bb.nodeName
#
#expos= expository('','',list())#.title=''
#for p in patternList:
#    print p.nodeName
#    expos.patternList.append(p.firstChild.data)
#    print p.firstChild.data
#print "============"
#for p in expos.patternList:
#    print p
def LoadExpositoryPattern(patternPath):
    dom = xml.dom.minidom.parse(patternPath)
    root = dom.documentElement
    patternList = root.getElementsByTagName(CONST_PATTERN)
    expos= expository('','',list())
    for p in patternList:
        print p.nodeName
        expos.patternList.append(p.firstChild.data)    
    return expos