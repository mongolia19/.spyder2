# -*- coding: GBK -*-
import sys
import imp
"""
Created on Wed Jun 10 23:52:14 2015

@author: mongolia19
"""
import urllib.request, urllib.parse, urllib.error
import re
import string, urllib.request, urllib.error, urllib.parse
def getTextFromURL(url):
    return  urllib.request.urlopen(url).read(200000)
def getAllLinksFromPage(url):
    htmlSource = urllib.request.urlopen(url).read(200000)
    #soup = BeautifulSoup.BeautifulSoup(htmlSource)
    links = re.findall('"((http|ftp)s?://.*?)"',htmlSource)

    return links
def urlsToFile(url_list,folder='pics'):
    i = 0
    for url in url_list:
        i = i + 1        
        sName = string.zfill(i,5) + '.html'#自动填充成六位的文件名
        print('正在下载第' + str(i) + '个网页，并将其存储为' + sName + '......')
        dirName = folder
        f = open( dirName + "/"+ sName,'w+')
        try:
            m = urllib.request.urlopen(url[0]).read()
        except Exception:
            print('URL opening Error')
            f.close()
            continue
        f.write(m)
        f.close()
#searchedKeyWord = 'How to make fried chicken'
#urlsToFile(url_list = getAllLinksFromPage('http://global.bing.com/search?q='+searchedKeyWord))
