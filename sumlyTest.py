# -*- coding: utf-8 -*-
"""
Created on Sun Jul 05 14:22:06 2015

@author: mongolia19
"""
#from __future__ import absolute_import
#from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from pattern.en import Sentence
from pattern.en import tree
from pattern.en import parse
from pattern.en import tag
from pattern.en import parsetree
import re,urllib
import nltk
from wordNet import getNPListFromStr
from wordNet import wordInSentStr
from wordNet import getAllEntities,getAllVerbs,getSentenceDictMatchingPatternList,getTopScoredSentenceDict
import PipLineTest
from wordNet import listToDict
import random
HOW = 'how'
WHAT = 'what'
WHO = 'who'
WHERE = 'where'
WHEN = 'when'
DEFAULT = 'default'
LANGUAGE = "english"
TELL_REASON = 0
TELL_DEFINATION = 1
TELL_SIMILAR = 2
TELL_RESULT = 3
GIVE_REMARKS = 4
#Use movie script to talk with human
class RelationTuple:
    SBJ = ''
    OBJ = ''
    VP = ''
    def __init__(self,s,o,v):
        self.SBJ = s
        self.OBJ = o
        self.VP = v
        
SENTENCES_COUNT = 5
lessthan = lambda x, y:x < y;
greaterthan = lambda x, y:x > y;
def minmax(test, *args):
    res = args[0]
    for arg in args[1:]:
        if test(arg, res):
            res = arg
    return res
def getRelationsFromDict(relations):#sub obj verb
    posList = list()
    OBJDict = {}
    SBJDict = {}
    VPDict = {}
    for k in relations.keys():
        posList.append(relations[k])
    for key in range(0,len(posList)):
        t = posList[key]
        if key == 0:
            OBJDict = t
        if key == 2:
            SBJDict = t
        if key == 1:
            VPDict = t

    len_S = len( SBJDict.keys())
    len_O = len( OBJDict.keys())
    len_V = len( VPDict.keys())
    relationNum = minmax(greaterthan, len_S, len_O, len_V)
    relationDict = {}
    for i in range(1,relationNum+1):
        relationDict[i] = RelationTuple('','','')
    if len_S != 0:
        for k in SBJDict.keys():
            print k
            relationDict[k].SBJ = SBJDict[k].string
    if len_O != 0:
        for k in OBJDict.keys():
            print k
            relationDict[k].OBJ = OBJDict[k].string
    if len_V != 0:
        for k in VPDict.keys():
            print k
            relationDict[k].VP = VPDict[k].string
    return relationDict
def filterSentencesByWords(sentenceList, WordsList):
    sentenceDict = {}
    for sent in sentenceList:
        sentenceDict[sent] = 0
    for sent in sentenceDict.keys():
        for word in WordsList:
            if PipLineTest.CombinationInSentence((word,),sent):
                sentenceDict[sent] = sentenceDict[sent] + 1
    return sentenceDict
def readStrToTuple(path):
    resTupleList = list()
    f = open(path,'r')
    strList = f.readlines()
    for s in strList:
        tempTuple = s.strip().strip('\n').split(' ')
        if len(tempTuple)>1:
            resTupleList.append(tempTuple)
    return resTupleList
def tupleToStr(t):#tuple(e1,e2,e3)--->e1 e2 e3
    if len(t) == 0:
        return ''
    resStr = ''
    for e in t:
        resStr = resStr + ' ' + str(e)
    return resStr
def keywithmaxval(d):
  """ a) create a list of the dict's keys and values; 
   b) return the key with the max value""" 
  v=list(d.values())
  k=list(d.keys())
  if len(k) <= 0:
      print 'dict is null'
      return None
  return k[v.index(max(v))]
#for each type define a few words that should be appear in answers,use these words to filter
#the backup sentences ---which sentences are closer to the words  
def getQuestionType(key,sentStr):
    if wordInSentStr(key,sentStr):
        return key
    else:
        return DEFAULT
def getQuestionTypeFromTypeList(questionTypeList,questionWordList):
    for qt in questionTypeList:
        t = getQuestionType(qt,questionWordList)
        if t != DEFAULT:
            return t
    return DEFAULT
def questionPatternLoader(key):
    headStr = './'
    tailStr = '_tuple_patterns.txt'
    types = (HOW,WHAT,WHO,WHERE,WHEN,DEFAULT,LANGUAGE)
    switchDict = {}
    for t in types:
        switchDict[t] = headStr + t + tailStr
    pList = readStrToTuple(switchDict[key])
    return pList
def getRelation( SentStr):
    
    #get verb phrase
    #get the noun before it ,get the none after it 
    #return the none verb none tuple
    #relationList = list()
    s = parsetree(SentStr, relations=True, lemmata=True)
    return (s[0]).relations
    #sentence = Sentence(taggedstring, token=['WORD', 'POS', 'CHUNK', 'PNP', 'REL', 'LEMMA'])
    #return sentence.relations
def getAllLinksFromPage(url):
    htmlSource = urllib.urlopen(url).read(200000)
    #soup = BeautifulSoup.BeautifulSoup(htmlSource)
    head = (url,'http')
    headlist = list()
    headlist.append(head)
    links = re.findall('"((http|ftp)s?://.*?)"',htmlSource)
    links = headlist + links
    return links
def getSentencesFromPassageText(text):
    PassageContentList = nltk.sent_tokenize(text)
    return PassageContentList
def getSentencesFromPassage(urlStr):
    PassageContentList = list()
    try:
        parser = HtmlParser.from_url(urlStr, Tokenizer(LANGUAGE))
    except Exception,ex:  
        print Exception,":",ex
        return PassageContentList
    try:
        if parser.document and parser.document != '':
            if parser.document.sentences and len(parser.document.sentences)>0:
                for h in parser.document.sentences:
                    PassageContentList.append(h._text.decode('gbk', 'ignore').encode('utf-8'))
                return PassageContentList
    except Exception,ex:
        print Exception,":",ex
    return PassageContentList
def getPassageFromUrl(urlStr):
    PassageContentList = ''
    try:
        parser = HtmlParser.from_url(urlStr, Tokenizer(LANGUAGE))
    except Exception,ex:  
        print Exception,":",ex
        return PassageContentList
    if parser.document:
        if parser.document.sentences and len(parser.document.sentences)>0:
            for h in parser.document.sentences:
                PassageContentList = PassageContentList + (h._text)
    return PassageContentList
def getSentencesDictFromPassageByQuestion(question,passage_sentList):
    tokens = nltk.word_tokenize(question)
    tags = nltk.pos_tag(tokens)
    ners = getAllEntities(tags)
    verbs = getAllVerbs(tags)
    sentDict = getSentenceDictMatchingPatternList(ners,passage_sentList)
    sentDict = getTopScoredSentenceDict(sentDict)
    sentDict = getSentenceDictMatchingPatternList(verbs,sentDict)
    return sentDict
def getTopCombinations(combinationDict):
    CombList = list()
    maxComb = keywithmaxval(combinationDict)
    maxCombVal = combinationDict[maxComb]    
    while True and len(combinationDict.keys())>0:
        combinationDict.pop(maxComb)
        t_maxComb = keywithmaxval(combinationDict)
        print maxComb , ':' , combinationDict[t_maxComb]
        CombList.append(maxComb)
        if combinationDict[t_maxComb] != maxCombVal:
            
            break
        else:
            maxComb = t_maxComb
    return CombList
def getTopPercentCombinations(combinationDict ,keepPercent):
    originalLength = len(combinationDict.keys())
    removePercent = 1 - keepPercent
    resList = list()
    while len(combinationDict.keys())>0 and originalLength*removePercent<len(combinationDict.keys()):
        tempList = getTopCombinations(combinationDict)
        resList = resList + tempList
    return resList
import FileUtils
from textblob import TextBlob
def getQuestionPatternsToFile(path,strContent):
    FileUtils.WriteToFile(path,strContent)
def WriteTupleToFile(path,t):
    s = tupleToStr(t)
    FileUtils.WriteToFile(path,s+'\r\n')
def iif(condition, true_part, false_part):  
    return (condition and [true_part] or [false_part])[0] 
def secondSentenceSplitor(sentenceList):
    resList = list()
    for sentence in sentenceList:
        tList = re.split('\.\.\.|\', \'', sentence)
        resList = resList + tList
    return resList
def questionPatternMining(firstHalf , secondHalf ,var,fileName):
    searchedKeyWords = firstHalf + var + secondHalf
    yahooHead = 'http://global.bing.com/search?q='
    yahooTail = '&intlF=1&setmkt=en-us&setlang=en-us&FORM=SECNEN'
    urlList = getAllLinksFromPage( yahooHead + searchedKeyWords + yahooTail)
    URLNum = 6
    keySentencesText = ''
    for i in range(0,iif(len(urlList)>URLNum,URLNum,len(urlList))):
        passageSentences = getSentencesFromPassage(urlList[i][0])
        parser = PlaintextParser.from_string(passageSentences, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        for sentence in summarizer(parser.document, SENTENCES_COUNT):
#            print(type(sentence))
#            print(sentence)
            ks = sentence._text.decode('gbk', 'ignore').encode('utf-8')
            print ks
            keySentencesText = keySentencesText + ' ' + ks
    getQuestionPatternsToFile(fileName,'\n'+keySentencesText)
def talkMod(inputSentence):
    FunctionFlag = False
    SelfFlag = False
    relations = getRelation(inputSentence)
    tDict = getRelationsFromDict(relations)
    for k in tDict.keys():
        if tDict[k].SBJ.lower() == 'me'.lower():
#            FunctionFlag = True
            break
        if tDict[k].OBJ.lower() == 'I'.lower():
#            FunctionFlag = True
            break
        
        print tDict[k].VP
    if FunctionFlag == True:
        FunctionMod(inputSentence)
    elif SelfFlag == True:
        LocalSearch(inputSentence)
    else:
        conversation(inputSentence)
    return ''
def LocalSearch():
    print 'LocalSearch'
def FunctionMod(inputSentence):
    print 'FunctionMod'
def WebSearch(inputSentence):
    print 'WebSearch'
WHAT_IS_STR = "what is"
GIVE_REMARKS_STR = "what do you think of "
def processInputSentence(inputSentence,searchExtraStr):
    if searchExtraStr == WHAT_IS_STR or searchExtraStr == GIVE_REMARKS_STR:
        npList = getNPListFromStr(inputSentence)
        npstr = ''
        for np in npList:
            npstr = npstr + " " + np
        return npstr
    else:
        return inputSentence
        
def conversation(inputSentence):
    SearchExtraStr = getSearchExtraStr(inputSentence)
    inputSentence = processInputSentence(inputSentence,SearchExtraStr)
    questionMod(SearchExtraStr + inputSentence,DEFAULT)
def TopicSelector():
    r = random.randint(TELL_REASON, GIVE_REMARKS)
    MapDict ={
    TELL_REASON:"why ",
    TELL_DEFINATION:"what is",
    TELL_SIMILAR:" and ",
    TELL_RESULT:" so ",
    GIVE_REMARKS:"what do you think of "
    }
    print MapDict[r]
    return MapDict[r]
def getSearchExtraStr(inputSentence):
    return TopicSelector()
    
def questionMod(inputSentence,qType):
    patternList = questionPatternLoader(qType)
    print '====================================================='
    backupAnwsersDict = {}
    SentencesList = getRelatedSentencesListFromWeb(inputSentence)
    for sentence in SentencesList:
        strSent = sentence
        for pat in patternList:
            if PipLineTest.CombinationInSentence(pat,strSent):
                if backupAnwsersDict.has_key(strSent):
                    continue
                else:
                    backupAnwsersDict[strSent] = strSent
                    print strSent
                    print '-------extracted---------------------------'
                    s = parsetree(strSent, relations=True, lemmata=True)
                    print 'subjects', s[0].subjects
                    print 'verbs', s[0].verbs
                    print 'objects', s[0].objects
                    print 'relations', s[0].relations
                    print 'pnp', s[0].pnp
    keyDict = listToDict(nltk.word_tokenize(searchedKeyWords))
    print '--------------------    key words  ----------------------'
    print keyDict
    print '--------------------After filtering ---------------------'    
    sentD = filterSentencesByWords(backupAnwsersDict.keys(), keyDict.keys())
    for k in sentD.keys():
        score = sentD[k]
        if score ==0:
            continue
        print k ,":" , score
def InputClassifier(InputStr):
    questionType = getQuestionTypeFromTypeList([HOW,WHAT,WHO,WHERE,WHEN,DEFAULT],InputStr.lower())
    if questionType == DEFAULT:
        talkMod(InputStr)
    else:    
        questionMod(InputStr,questionType)
def getRelatedSentencesListFromWeb(searchedKeyWords):
    yahooHead = 'http://global.bing.com/search?q='
    yahooTail = '&intlF=1&setmkt=en-us&setlang=en-us&FORM=SECNEN'
    urlList = getAllLinksFromPage( yahooHead + searchedKeyWords + yahooTail)

    URLNum = 6
    keySentencesText = ''

    for i in range(0,iif(len(urlList)>URLNum,URLNum,len(urlList))):
        passageSentences = getSentencesFromPassage(urlList[i][0])

        parser = PlaintextParser.from_string(passageSentences, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        for sentence in summarizer(parser.document, SENTENCES_COUNT):
#            print(type(sentence))
#            print(sentence)
            ks = sentence._text.decode('gbk', 'ignore').encode('utf-8')
            print ks
            keySentencesText = keySentencesText + ' ' + ks
    MainSearchResultSentencesList = getSentencesFromPassageText(keySentencesText)
    MainSearchResultSentencesList = secondSentenceSplitor(MainSearchResultSentencesList)
    return MainSearchResultSentencesList
if __name__ == "__main__":
#    url = "http://en.wikipedia.org/wiki/Automatic_summarization"
#    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
#    noneList = list(['table','coffee','ashtray','vacuum','door knob','safety','elevator','chair','processor','arm','space-time'])
#    for n in noneList:
#        questionPatternMining('what does ',' mean',n,'./what_patterns_txt.txt',)
    while True:
        searchedKeyWords = raw_input('You :')
        if searchedKeyWords == 'quit\n':
            break
        InputClassifier(searchedKeyWords)
#    relations = getRelation(searchedKeyWords)
#    tDict = getRelationsFromDict(relations)
#    for k in tDict.keys():
#        print tDict[k].SBJ
#        print tDict[k].OBJ
#        print tDict[k].VP
#    print '........'
#    for r in relations.keys():
#        print type(relations[r])
#        print relations[r]
#    keyDict = PipLineTest.getKeyWordDictFromCleanedSentence(searchedKeyWords)
#    searchedKeyWords = ''
#    for k in keyDict:
#        searchedKeyWords = searchedKeyWords + " " + k



#    qDict = {}
#    combinationDict = PipLineTest.getWordCombinationDict(3,MainSearchResultSentencesList,qDict)

#    getQuestionPatternsToFile('./what_patterns_txt.txt','\n'+keySentencesText)


    # or for plain text files
#    passage = FileUtils.OpenFileGBK('./reading/passage.txt')
#    passage = passage.encode("UTF-8")



#    print '.....................what questions patterns ..........................'
#    whatTxt = FileUtils.OpenFileUnicode('./what_patterns_txt.txt')
#    MainSearchResultSentencesList = getSentencesFromPassageText(whatTxt)
#
#    combinationDict = PipLineTest.getWordCombinationDict(3,MainSearchResultSentencesList,qDict)
#
#    patternList = getTopPercentCombinations(combinationDict,0.0001)
#    for p in patternList:
#        print p
#        WriteTupleToFile('./what_tuple_patterns.txt',p)
#    for k in combinationDict.keys():
#        if combinationDict[k] > 50:
#            print k , ":" , combinationDict[k]
#    print type(keywithmaxval(combinationDict))        
#    blob = TextBlob(passage)
#    NoneList = blob.noun_phrases
#    print NoneList
#    sent = 'Punctuation marks are stripped from words, and n-grams will not run over sentence delimiters'

