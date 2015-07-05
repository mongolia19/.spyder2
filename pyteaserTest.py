# -*- coding: utf-8 -*-
"""
Created on Sun Jul 05 15:11:29 2015

@author: mongolia19
"""
#from pyteaser import SummarizeUrl
#url = "http://en.wikipedia.org/wiki/Automatic_summarization"
#summaries = SummarizeUrl(url)
#print summaries
from snownlp import SnowNLP
import FileUtils
passage = FileUtils.OpenFileGBK('./reading/passage.txt')
passage = passage.encode("UTF-8")
s = SnowNLP(passage)
print s.keywords(5)
print s.summary(1)