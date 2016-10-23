# -*- coding: utf-8 -*-
"""
Created on Mon Jun 01 23:55:17 2015
To Do : add entity recognation in information extraction
@author: mongolia19
"""

import urllib
#import BeautifulSoup
import re
import string, urllib2
import PipLineTest
import FileUtils
def getAllLinksFromPage(url):
    htmlSource = urllib.urlopen(url).read(200000)
    #soup = BeautifulSoup.BeautifulSoup(htmlSource)
    links = re.findall('"((http|ftp)s?://.*?)"',htmlSource)

    return links

 

def urlsToFile(url_list,folder='htmls'):   
    i = 0
    for url in url_list:
        i = i + 1        
        sName = string.zfill(i,5) + '.html'#自动填充成六位的文件名
        print '正在下载第' + str(i) + '个网页，并将其存储为' + sName + '......'
        dirName = folder
        f = open( dirName + "/"+ sName,'w+')
        try:
            m = urllib2.urlopen(url[0]).read()
        except Exception:
            print 'URL opening Error'
            f.close()
            continue
        f.write(m)
        f.close()

PATH_CONST = 'htmls'
fileList = FileUtils.ReturnAllFileOnPath(1,PATH_CONST)
ScoreBase = int( 0.6 * len(fileList))

#key_dict = PipLineTest.getKeyWordDictFromQuery('How to make fried fish and potatos')
combination_dict = {}
for oneFile in fileList:
#    raw_text = FileUtils.OpenFileGBK(oneFile)
#    cleaned_text = FileUtils.CleanHTMLTextByBS(raw_text)
#    key_dict = PipLineTest.getKeyWordDictFromCleanedText(cleaned_text)
    key_dict = PipLineTest.getKeyWordDictFromFile(oneFile)
    sentList = PipLineTest.getSentenceListFromFile(oneFile)
    combList = PipLineTest.getWordCombinationDict(3,sentList,key_dict)#get all combinations in one file
    print 'combiination number is %d',len(combList)    
    for comb in combList:# grade one combination over all articles
        #fileContent = PipLineTest.getCleanedTextFromFile(oneFile)
        if len(combination_dict.keys())>4:
            break
        if not PipLineTest.IsCombinationInDict(comb,combination_dict):         
            fileContentList = FileUtils.getContentStrListFromHTMLPath(PATH_CONST)
            score = PipLineTest.GradeCombinationOverCorpus(comb,fileContentList)
            if score > ScoreBase :
                combination_dict[comb] = score
                print comb
print combination_dict

#fileContentList = PipLineTest.getFileContentListFromPath(PATH_CONST)
fileContentList = FileUtils.getContentStrListFromHTMLPath(PATH_CONST)
for fileContent in fileContentList:
    keySentList = PipLineTest.ExtractSentencesByCombination(fileContent,combination_dict)
    fl=open('result.txt', 'w')
    for keyS in keySentList:
        fl.write(keyS)
        fl.write("\r\n")
    fl.close()
