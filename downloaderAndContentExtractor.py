# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 00:41:11 2015

@author: mongolia19
"""

import urllib,urllib2,re
import BeautifulSoup
#url = "http://www.jb51.net/article/43466.htm"  
#
#print "getting url:",url
#content = urllib.urlopen(url).read()
#
#title = re.findall(r'<title>.*</title>',content)
#print "\r\n %s" %(title)
#links = re.findall('"((http|ftp)s?://.*?)"', content)
#print links
#soup = BeautifulSoup.BeautifulSoup(content)
#print soup.p
#print soup.title
#print soup.a['href']


def ExtractContentFromURL(httpLink):
    content = urllib.urlopen(httpLink).read()
    return content
    
    #soup = BeautifulSoup.BeautifulSoup(content)
    #print soup.title.string
    #return soup.title.string
    #return [p.next_sibling.strip() for p in soup.findAll('p')]