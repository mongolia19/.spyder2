# -*- coding: GBK -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
"""
Created on Wed Jun 10 23:52:14 2015

@author: mongolia19
"""
import urllib
import re
import string, urllib2
def getTextFromURL(url):
    return  urllib.urlopen(url).read(200000)
def getAllLinksFromPage(url):
    htmlSource = urllib.urlopen(url).read(200000)
    #soup = BeautifulSoup.BeautifulSoup(htmlSource)
    links = re.findall('"((http|ftp)s?://.*?)"',htmlSource)

    return links
def urlsToFile(url_list,folder='htmls'):   
    i = 0
    for url in url_list:
        i = i + 1        
        sName = string.zfill(i,5) + '.html'#�Զ�������λ���ļ���
        print u'�������ص�' + str(i) + u'����ҳ��������洢Ϊ' + sName + '......'
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
#searchedKeyWord = 'How to make fried chicken'
#urlsToFile(url_list = getAllLinksFromPage('http://global.bing.com/search?q='+searchedKeyWord))
