# -*- coding: utf-8 -*-
"""
Created on Mon Jun 01 23:55:17 2015

@author: mongolia19
"""

import urllib
#import BeautifulSoup
import re, os
import string, urllib2
def getAllLinksFromPage(url):
    htmlSource = urllib.urlopen(url).read(200000)
    #soup = BeautifulSoup.BeautifulSoup(htmlSource)
    links = re.findall('"((http|ftp)s?://.*?)"',htmlSource)

    return links

 
#定义百度函数
def urlsToFile(url_list):   
    i = 0
    for url in url_list:
        i = i + 1        
        sName = string.zfill(i,5) + '.html'#自动填充成六位的文件名
        print '正在下载第' + str(i) + '个网页，并将其存储为' + sName + '......'
        dirName = 'htmls'
        f = open( dirName + "/"+ sName,'w+')
        try:
            m = urllib2.urlopen(url[0]).read()
        except Exception:
            print 'URL opening Error'
            f.close()
            continue
        f.write(m)
        f.close()
        
searchedKeyWord = 'How to make fried fish and potatos' 
urlsToFile( getAllLinksFromPage('http://global.bing.com/search?q='+searchedKeyWord))