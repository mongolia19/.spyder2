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
from wordNet import wordInSentStr
from wordNet import getAllEntities,getAllVerbs,getSentenceDictMatchingPatternList,getTopScoredSentenceDict
import PipLineTest
HOW = 'how'
WHAT = 'what'
WHO = 'who'
WHERE = 'where'
WHEN = 'when'
DEFAULT = 'default'
LANGUAGE = "english"
SENTENCES_COUNT = 5
def getQuestionType(key,questionWordList):
    if wordInSentStr(key,questionWordList):
        return key
    else:
        return DEFAULT
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
    if parser.document:
        if parser.document.sentences and len(parser.document.sentences)>0:
            for h in parser.document.sentences:
                PassageContentList.append(h._text)
            return PassageContentList
    return list()
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
def iif(condition, true_part, false_part):  
    return (condition and [true_part] or [false_part])[0] 
import FileUtils
from textblob import TextBlob


if __name__ == "__main__":
    url = "http://en.wikipedia.org/wiki/Automatic_summarization"
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    searchedKeyWords = 'who invented the iPhone'
#    keyDict = PipLineTest.getKeyWordDictFromCleanedSentence(searchedKeyWords)
#    searchedKeyWords = ''
#    for k in keyDict:
#        searchedKeyWords = searchedKeyWords + " " + k
    yahooHead = 'http://global.bing.com/search?q='
    yahooTail = '&intlF=1&setmkt=en-us&setlang=en-us&FORM=SECNEN'
    searchURL = yahooHead + searchedKeyWords + yahooTail
    urlList = getAllLinksFromPage( yahooHead + searchedKeyWords + yahooTail)
#    PassageContentList = list()
#    for i in range(0,iif(len(urlList)>5,5,len(urlList))):
#        try:
#            parser = HtmlParser.from_url(urlList[i][0], Tokenizer(LANGUAGE))
#        except Exception,ex:  
#            print Exception,":",ex
#            continue
#        if parser.document:
#            
#            if parser.document.sentences and len(parser.document.sentences):
#                content = ''
#                for h in parser.document.sentences:
#                    content = content + h._text                
#                    print type(h)
#                    print h
#                PassageContentList.append(content)
#    print PassageContentList
    URLNum = 6
    SentDict = list()
    keySentencesText = ''
    MainSearchResultText = ''
    for i in range(0,iif(len(urlList)>URLNum,URLNum,len(urlList))):
        passageSentences = getSentencesFromPassage(urlList[i][0])
        if passageSentences and len (passageSentences):            
            for sent in passageSentences:
                MainSearchResultText = MainSearchResultText + sent
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
    # or for plain text files
#    passage = FileUtils.OpenFileGBK('./reading/passage.txt')
#    passage = passage.encode("UTF-8")
    parser = PlaintextParser.from_string(keySentencesText, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    
    
#    for h in parser.document.sentences:
#        print type(h)
#        print h
    print '====================================================='
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        print(type(sentence))
        print(sentence)
    print '----------------------------------'
    print MainSearchResultText
    print '-----------------------------------'
    MainSearchResultSentencesList = getSentencesFromPassageText(MainSearchResultText)
    questionWords = nltk.word_tokenize(searchedKeyWords)
    qDict = {}
    for q in questionWords:
        qDict[q] = q
    combinationDict = PipLineTest.getWordCombinationDict(3,MainSearchResultSentencesList,qDict)
    for k in combinationDict.keys():
        if combinationDict[k]>=24:
            print k ,':',combinationDict[k]
            
#    blob = TextBlob(passage)
#    NoneList = blob.noun_phrases
#    print NoneList
#    sent = 'Punctuation marks are stripped from words, and n-grams will not run over sentence delimiters'
#    s = parsetree(sent, relations=True, lemmata=True)
#    print s[0].subjects
#    print s[0].verbs
#    print s[0].objects
#    print s[0].pnp
