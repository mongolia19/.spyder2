# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib
import nlpExmp
import re
import PatternLoader
import nltk
import operator
import itertools

import FileUtils
###
##To Do: impliement a function to envalueate the importance of a sentence in an article
##To Do: Extract patterns from a single article,which should remove words that has
##a high tf-idf mark (which means only extract words that have high tf value)
##extract patterns on a group of articles on a "serise of topics",that means the topics
##are simmilar(such as how to make tea, how to make coffe ,how to make ice cream)
## in these cases the program can see how a "how to ..." article always look like
##To Do:Get all two word combinations,and get the combinations that appear most frequently
## in other sentences(cleaned sentences AKA removed key words) 
def getText(httpLink):
    return  urllib.urlopen(httpLink).read(200000)

def loadPatterns():
    return PatternLoader.LoadExpositoryPattern(PatternLoader.CONST_PATTERN_FILE_PATH)

def ExtractKeyWords(text,KeyCount):
    return nlpExmp.keyWordsExtractor(text,KeyCount)

##过滤HTML中的标签
#将HTML中标签等信息去掉
#@param htmlstr HTML字符串.
def filter_tags(htmlstr):
#先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.S|re.I|re.M) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.S|re.I|re.M)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.S|re.I|re.M)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>',re.S|re.I|re.M)#HTML标签
    re_comment=re.compile('<!--[^>]*-->',re.S|re.I|re.M)#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
#去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s

##替换常用HTML字符实体.
#使用正常的字符替换HTML中特殊的字符实体.
#你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
#@param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
'lt':'<','60':'<',
'gt':'>','62':'>',
'amp':'&','38':'&',
'quot':'"','34':'"',}

    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如&gt;
        key=sz.group('name')#去除&;后entity,如&gt;为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
    #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def repalce(s,re_exp,repl_string):
    return re_exp.sub(repl_string,s)
def BScleanText(RawText):
    cText = ''.join(BeautifulSoup(RawText).findAll(text=True))
    return cText

def ImportanceMeasure(sentence,word_dict):
    words_of_sent = nltk.word_tokenize(sentence)
    totalCount = len(words_of_sent)
    print type(words_of_sent)
    count = 0.0
    for word in words_of_sent:
        print word
        if word_dict.has_key(word):
            count = count + 1.0
    return count/totalCount        

def RemoveKeyWordsFromSentence(sentence,keyword_dict):# there is somethine wrong with the method
    for key in keyword_dict.keys():
        sentence = re.sub(key, "",str(sentence))
    return sentence
def getWebPageRawText(query):
    engineUrl = 'http://global.bing.com/search?q='
    return getText(engineUrl+query)

def getKeyWordDictFromQuery(query):
    cleanedText = getCleanTextFromQuery(query)
    print cleanedText
    KeyRatio = 0.1
    sent_list = nltk.sent_tokenize(cleanedText)
    sentCount = len(sent_list)
    keyWordsList = ExtractKeyWords(cleanedText,int(sentCount*KeyRatio))
    print keyWordsList
    patternHashMap = {}
    for key in keyWordsList:
         patternHashMap[key] = key
    return patternHashMap
def getCleanedTextFromFile(filePath):
    file_object = open(filePath) 
    try: 
        RawText = file_object.read( ) 
    finally: 
        file_object.close( ) 
    return cleanText(RawText)
def getSentenceListFromText(t):
    return nltk.sent_tokenize(t)
def getSentenceListFromFile(filePath):
    cleanedText = getCleanedTextFromFile(filePath)
    return nltk.sent_tokenize(cleanedText)
def getKeyWordDictFromFile(filePath):
    file_object = open(filePath) 
    try: 
        RawText = file_object.read( ) 
    finally: 
        file_object.close( ) 
    cleanedText = cleanText(RawText)
    KeyRatio = 0.05
    sent_list = nltk.sent_tokenize(cleanedText)
    sentCount = len(sent_list)
    keyWordsList = ExtractKeyWords(cleanedText,int(sentCount*KeyRatio)+1)
    print keyWordsList
    patternHashMap = {}
    for key in keyWordsList:
         patternHashMap[key] = key
    return patternHashMap
def getKeyWordDictFromCleanedText(cleanedText):
    KeyRatio = 0.05
    sent_list = nltk.sent_tokenize(cleanedText)
    sentCount = len(sent_list)
    keyWordsList = ExtractKeyWords(cleanedText,int(sentCount*KeyRatio)+1)
    patternHashMap = {}
    for key in keyWordsList:
         patternHashMap[key] = key
    return patternHashMap
def getKeyWordDictFromCleanedSentence(sentStr,KeyRatio = 0.35):
    wordList = nltk.word_tokenize(sentStr)
    wCount = len(wordList)
    keyWordsList = ExtractKeyWords(sentStr,int(wCount*KeyRatio))
    patternHashMap = {}
    for key in keyWordsList:
         patternHashMap[key] = key
    return patternHashMap
#===========Data Cleaning======================
#url = "http://www.chinadaily.com.cn/world/2015xiattendwwii/2015-04/29/content_20627695.htm"

#RawText = getText(url)


#===========Pattern Loading================================
exposPattern = loadPatterns()

#for p in exposPattern.patternList:
#    patternHashMap[p] = p
#print patternHashMap
#============sentence stemming===============================
#sent_list = nltk.sent_tokenize(cleanedText)
#sentCount = len(sent_list)

#============Key word Extraction===============================
#KeyRatio = 0.1
#keyWordsList = ExtractKeyWords(cleanedText,int(sentCount*KeyRatio))
#print keyWordsList
#for key in keyWordsList:
#    patternHashMap[key] = key

#============Sentence sortting===============================
def sentenceSortingByKeyWords(sent_list,patternHashMap):
    
    impDict = {}
    for sent in sent_list:
        imp = ImportanceMeasure( sent,patternHashMap)
        impDict[sent] = imp
    sorted_imp = sorted(impDict.iteritems(), key=operator.itemgetter(1),reverse=True)  
    return sorted_imp

#########################
def getWordCombinationDict(wordNum,sent_list,patternHashMap):#patternHashMap is a dict of keywords
    Max_Sentence_Length = 100
    combination_Dict = {}
    CombWordNum = wordNum
    for sent in sent_list:
        sent = re.sub('[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+', "",str(sent))
        #remove the keywords first
        #sent = RemoveKeyWordsFromSentence(sentence=sent,keyword_dict=patternHashMap)
        words_in_sent = nltk.word_tokenize(sent)
        if len(words_in_sent) > Max_Sentence_Length:
            continue
        comb = list(itertools.permutations(words_in_sent,CombWordNum))
        #print comb
        for OneComb in comb:
            if combination_Dict.has_key(OneComb):
                combination_Dict[OneComb] = combination_Dict[OneComb] + 1
            else:
                combination_Dict[OneComb] = 1
        print "All possiable combinations in a sentence."
#    for OneComb in combination_Dict.keys():
#        if combination_Dict[OneComb] == 1:
#            combination_Dict.pop(OneComb)
    return combination_Dict
def getWordDictInSentence(sentenceStr):
	word_dict = {}
	wordList = nltk.word_tokenize(sentenceStr)
	for word in wordList:
	    word_dict[word]=word
	return word_dict
def CombinationInSentence(OneComb,sentenceStr):#if combination is in return 1
    #goal = len (OneComb)
    mark = 0
    wordsInSentDict = getWordDictInSentence(sentenceStr)
    for word in OneComb:

        if wordsInSentDict.has_key(str(word)):
            mark = mark + 1
    if mark >=len(OneComb):
        return 1
    else:
        return 0

def GradeCombinationOverArticle(OneComb,article):
    mark = 0
    sentenceList = nltk.sent_tokenize(article)
    for sent in sentenceList:
        mark = mark + CombinationInSentence(OneComb,sent)
    return mark
def GradeCombinationOverCorpus(OneComb,articleStrList):
    mark = 0    
    for article in articleStrList:
        if GradeCombinationOverArticle(OneComb,article) > 0:
            mark = mark + 1
    return mark
def getFileContentListFromPath(path):
    fileContentList = list()
    fileNameList = FileUtils.ReturnAllFileOnPath(1,path)
    for fileName in fileNameList:    
        fileContent = getCleanedTextFromFile(fileName)
        fileContentList.append(fileContent)
    return fileContentList
def StrElementInTuple(e,t):
    for e_t in t:
        if str(e_t) == str(e):
            return True
    return False
def tupleContains(A,B):#B contains A
    for element in A:
        if not StrElementInTuple( element,B):
            return False
    return True
def IsCombinationInDict(comb,CombDict):
    for entry in CombDict.keys():
        if tupleContains( entry,comb):
            return True
    return False
def ExtractSentencesByCombination(ArticleStr,CombDict):
    KSentenceList = list()
    sentenceList = nltk.sent_tokenize(ArticleStr)
    for sentence in sentenceList:
        for comb in CombDict:
            if CombinationInSentence(comb,sentence):
                KSentenceList.append(sentence)
                break
    return KSentenceList            
############# key sentences selected by tf-idf ##############
#extractedTXT = ''
#i = 0
#totalCount = len(sorted_imp)
#threshold = int(totalCount*0.1)
#for sent in sorted_imp:
#    if i<threshold:
#        extractedTXT = extractedTXT + sent[0]
#    i = i + 1
#print extractedTXT
#patternHashMap[0] = keyWordsList[0][0]

#imp = ImportanceMeasure( sent_list[0],patternHashMap)
#print imp
