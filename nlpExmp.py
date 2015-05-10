# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 22:46:27 2015

@author: mongolia19
"""
import nltk
import jieba.analyse
import nltk.tree
#f = open('./nettext.text', 'r')
#text = f.read()
#text=u"The Washington Monument is the most prominent structure in Washington, D.C. and one of the city's early attractions. It was built in honor of George Washington, who led the country to independence and then became its first President."
#sents=nltk.sent_tokenize(text=text)
def keyWordsExtractor(text,keyCount):
    return jieba.analyse.extract_tags(text,topK=(keyCount))
    
#keys=jieba.analyse.extract_tags(text,withWeight=(text.count))
#print keys
#print '\r\n'
#NE_List=[]
#for sen in sents:
#    print sen.join("\r\n")
#    tokens =nltk.word_tokenize(text=sen)
#    tags =nltk.pos_tag(tokens)
#    ners =nltk.ne_chunk(tags)
#    for node in ners.subtrees():
##if node[-1]==("NNP") or node[-1]==("NN") or node[-1]==("NNS"):        
#        if node.height() < ners.height():            
#            #node.draw()
#            print '\r\n'            
#            print '%s:' %node.label()
#            for leaf in node.leaves():
#                print '%s,' % leaf[0]
