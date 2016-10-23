#!/usr/bin/python
# -*- coding:utf8 -*-

import os
allFileNum = 0
import BeautifulSoup
def CleanHTMLTextByBS(RawText):
    tSoup = BeautifulSoup.BeautifulSoup(RawText)
    return tSoup.text
def WriteToFile(path,content):
    f = open(path,'a')
    f.write(content)
    f.close()
def ReturnAllFileOnPath(level, path):
    global allFileNum
    '''
    打印一个目录下的所有文件夹和文件
    '''
    # 所有文件夹，第一个字段是次目录的级别
    dirList = []
    # 所有文件
    fileList = []
    # 返回一个列表，其中包含在目录条目的名称(google翻译)
    files = os.listdir(path)
    # 先添加目录级别
    dirList.append(str(level))
    for f in files:
        if(os.path.isdir(path + '/' + f)):
            # 排除隐藏文件夹。因为隐藏文件夹过多
            if(f[0] == '.'):
                pass
            else:
                # 添加非隐藏文件夹
                dirList.append(f)
        if(os.path.isfile(path + '/' + f)):
            # 添加文件
            fileList.append(path + '/' + f)
    return fileList
def printPath(level, path):
    global allFileNum
    '''
    打印一个目录下的所有文件夹和文件
    '''
    # 所有文件夹，第一个字段是次目录的级别
    dirList = []
    # 所有文件
    fileList = []
    # 返回一个列表，其中包含在目录条目的名称(google翻译)
    files = os.listdir(path)
    # 先添加目录级别
    dirList.append(str(level))
    for f in files:
        if(os.path.isdir(path + '/' + f)):
            # 排除隐藏文件夹。因为隐藏文件夹过多
            if(f[0] == '.'):
                pass
            else:
                # 添加非隐藏文件夹
                dirList.append(f)
        if(os.path.isfile(path + '/' + f)):
            # 添加文件
            fileList.append(f)
    # 当一个标志使用，文件夹列表第一个级别不打印
    i_dl = 0
    for dl in dirList:
        if(i_dl == 0):
            i_dl = i_dl + 1
        else:
            # 打印至控制台，不是第一个的目录
            print '-' * (int(dirList[0])), dl
            # 打印目录下的所有文件夹和文件，目录级别+1
            printPath((int(dirList[0]) + 1), path + '/' + dl)
    for fl in fileList:
        # 打印文件
        print '-' * (int(dirList[0])), fl
        # 随便计算一下有多少个文件
        allFileNum = allFileNum + 1

def getContentStrListFromHTMLPath(path='htmls'):    
    contentStrList=list()    
    fileList = ReturnAllFileOnPath(1,path)
    #print soup.text
    for Onefile in fileList:    
        fileOBJ = open(Onefile)
        html_doc = fileOBJ.read().decode('gbk', 'ignore')
        #html_doc = fileOBJ.read().decode('utf-8', 'ignore').encode('gbk')
        soup = BeautifulSoup.BeautifulSoup(html_doc)  
        contentStrList.append(soup.text)
        fileOBJ.close()
    return contentStrList

def getContentStrListFromRawTextPath(path='text'):
    contentStrList=list()
    fileList = ReturnAllFileOnPath(1,path)
    print "files are :"
    print  fileList
    #print soup.text
    for Onefile in fileList:
        fileOBJ = open(Onefile)
        doc = fileOBJ.read().decode('gbk', 'ignore')
        #html_doc = fileOBJ.read().decode('utf-8', 'ignore').encode('gbk')
        # soup = BeautifulSoup.BeautifulSoup(html_doc)
        contentStrList.append(doc)
        fileOBJ.close()
    return contentStrList

def OpenFileGBK(OnefilePath):
    fileOBJ = open(OnefilePath)
    html_doc = fileOBJ.read().decode('gbk', 'ignore')
    #html_doc = fileOBJ.read().decode('utf-8', 'ignore').encode('gbk') 
    fileOBJ.close()
    return html_doc
def OpenFileUnicode(OnefilePath):
    fileOBJ = open(OnefilePath)
    html_doc = fileOBJ.read()
    #html_doc = fileOBJ.read().decode('utf-8', 'ignore').encode('gbk') 
    fileOBJ.close()
    return html_doc
#if __name__ == '__main__':
#    printPath(1, './htmls')
#    print '总文件数 =', allFileNum

