# -*- coding: GBK -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
"""
Created on Thu Jun 11 21:49:58 2015

@author: mongolia19
"""
import BeautifulSoup  
import FileUtils
PATH_CONST = 'htmls'
fileList = FileUtils.ReturnAllFileOnPath(1,PATH_CONST)
#print soup.text
for Onefile in fileList:
    print 'processing file ' + Onefile
    fileOBJ = open(Onefile)
    html_doc = fileOBJ.read().decode('gbk', 'ignore')
    #html_doc = fileOBJ.read().decode('utf-8', 'ignore').encode('gbk')
    soup = BeautifulSoup.BeautifulSoup(html_doc)  
    extStr = (soup.text)
    print extStr
    fileOBJ.close()
#    fileOBJ = open( Onefile,'w+')
#    fileOBJ.write(extStr)
#    fileOBJ.close()
    #for string in soup.strings:  
    #    print(repr(string))  
        #print(soup.prettify()) 
