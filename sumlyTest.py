# -*- coding: utf-8 -*-
"""
Created on Sun Jul 05 14:22:06 2015

@author: mongolia19
"""
# from __future__ import absolute_import
# from __future__ import division, print_function, unicode_literals
# One entry of knowledge should contains (subject) (verb) (object) (on what condition | by what means)
# (at what time ) (in waht place)

# Do more pre-processing after get question :
# classify questions into more types
# change the question into normal order
# remove interrogatives (like what ,how ,when)
# Maybe computer should know what does "before" "after" relation-words mean
# eg. after means it should search ansers in sentences that appear after where the question mentioned
#give more weight to nouns than to verbs while scoring sentences
#classify questions into every kind of wh-words : who where which when ans so on
#use more than one taggers to tag a sentence to increase precision
#Only extract the sentences that do not contain interrogatives such as what how why
import re

import random

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk


from pattern.search import Pattern
from pattern.en import parsetree
import MySqlHelper
from wordNet import wordDictRelation
from wordNet import getVPListFromStr
from wordNet import getNPListFromStr
from wordNet import wordInSentStr
from wordNet import getAllEntities, getAllVerbs, getSentenceDictMatchingPatternList, getTopScoredSentenceDict
import PipLineTest
from wordNet import listToDict
from wordNet import getAllLinksFromPage
from wordNet import html_to_plain_text
from wordNet import measure_similarity_by_search_engine
db_list = ['', '8313040', 'python']
HOW = 'how'
WHAT = 'what'
WHICH = 'which'
WHO = 'who'
WHOM = 'whom'
WHOSE = 'whose'
WHERE = 'where'
WHEN = 'when'
WHY = 'why'
DEFAULT = 'default'
LANGUAGE = "english"
TELL_REASON = 0
TELL_DEFINATION = 1
TELL_SIMILAR = 2
TELL_RESULT = 3
GIVE_REMARKS = 4

articlesFromHtmls = list()  # used to store each article from one search


# Use movie script to talk with human
class slot:
    ACTION = ''
    OBJ = ''

    def __init__(self, a, o):
        self.ACTION = a
        self.OBJ = o

    def __str__(self):
        return self.ACTION + '---' + self.OBJ


class body:
    NAME = ''
    SLOTList = list()

    def __init__(self, n):
        self.NAME = n

    def __str__(self):
        properties = ''
        for p in self.SLOTList:
            properties = properties + str(p)
        return self.NAME + ':' + properties


class RelationTuple:
    SBJ = ''
    OBJ = ''
    VP = ''

    def __init__(self, s, o, v):
        self.SBJ = s
        self.OBJ = o
        self.VP = v

    def __str__(self):
        return 'SBJ:' + self.SBJ + ' VP: ' + self.VP + ' OBJ: ' + self.OBJ


SENTENCES_COUNT = 4
lessthan = lambda x, y: x < y;
greaterthan = lambda x, y: x > y;


def minmax(test, *args):
    res = args[0]
    for arg in args[1:]:
        if test(arg, res):
            res = arg
    return res


def getRelationsFromDict(relations):  # key is numbers value is self-defined RelationTuple obj verb
    posList = list()
    OBJDict = {}
    SBJDict = {}
    VPDict = {}
    for k in relations.keys():
        posList.append(relations[k])
    for key in range(0, len(posList)):
        t = posList[key]
        if key == 0:
            OBJDict = t
        if key == 2:
            SBJDict = t
        if key == 1:
            VPDict = t

    len_S = len(SBJDict.keys())
    len_O = len(OBJDict.keys())
    len_V = len(VPDict.keys())
    relationNum = minmax(greaterthan, len_S, len_O, len_V)
    relationDict = {}
    for i in range(1, relationNum + 1):
        relationDict[i] = RelationTuple('', '', '')
    if len_S != 0:
        for k in SBJDict.keys():
            print k
            if relationDict.has_key(k):
                relationDict[k].SBJ = SBJDict[k].string
    if len_O != 0:
        for k in OBJDict.keys():
            print k
            if relationDict.has_key(k):
                relationDict[k].OBJ = OBJDict[k].string
    if len_V != 0:
        for k in VPDict.keys():
            print k
            if relationDict.has_key(k):
                relationDict[k].VP = VPDict[k].string
    return relationDict


def filterSentencesByWords(sentenceList, WordsList):
    sentenceDict = {}
    for sent in sentenceList:
        sentenceDict[sent] = 0
    for sent in sentenceDict.keys():
        for word in WordsList:
            if PipLineTest.CombinationInSentence((word,), sent):
                sentenceDict[sent] = sentenceDict[sent] + 1
    return sentenceDict


def readStrToTuple(path):
    resTupleList = list()
    f = open(path, 'r')
    strList = f.readlines()
    for s in strList:
        tempTuple = s.strip().strip('\n').split(' ')
        if len(tempTuple) > 1:
            resTupleList.append(tempTuple)
    return resTupleList


def tupleToStr(t):  # tuple(e1,e2,e3)--->e1 e2 e3
    if len(t) == 0:
        return ''
    resStr = ''
    for e in t:
        resStr = resStr + ' ' + str(e)
    return resStr


def keywithmaxval(d):
    """ a) create a list of the dict's keys and values;
   b) return the key with the max value"""
    v = list(d.values())
    k = list(d.keys())
    if len(k) <= 0:
        print 'dict is null'
        return None
    return k[v.index(max(v))]


# for each type define a few words that should be appear in answers,use these words to filter
# the backup sentences ---which sentences are closer to the words
def getQuestionType(key, sentStr):
    if wordInSentStr(key, sentStr):
        return key
    else:
        return DEFAULT


def getQuestionTypeFromTypeList(questionTypeList, questionWordList):
    for qt in questionTypeList:
        t = getQuestionType(qt, questionWordList)
        if t != DEFAULT:
            return t
    return DEFAULT


def questionPatternLoader(key):
    headStr = './'
    tailStr = '_tuple_patterns.txt'
    types = (HOW, WHAT, WHO, WHERE, WHEN, DEFAULT, LANGUAGE)
    switchDict = {}
    for t in types:
        switchDict[t] = headStr + t + tailStr
    pList = readStrToTuple(switchDict[key])
    return pList


def getRelation(SentStr):
    # get verb phrase
    # get the noun before it ,get the none after it
    # return the none verb none tuple
    # relationList = list()
    s = parsetree(SentStr, relations=True, lemmata=True)
    return (s[0]).relations
    # sentence = Sentence(taggedstring, token=['WORD', 'POS', 'CHUNK', 'PNP', 'REL', 'LEMMA'])
    # return sentence.relations


def get_pnp(sent_str):
    # get verb phrase
    # get the noun before it ,get the none after it
    # return the none verb none tuple
    # relationList = list()
    s = parsetree(sent_str, relations=True, lemmata=True)
    return (s[0]).pnp
    # sentence = Sentence(taggedstring, token=['WORD', 'POS', 'CHUNK', 'PNP', 'REL', 'LEMMA'])
    # return sentence.relations




def getSentencesFromPassageText(text):
    PassageContentList = nltk.sent_tokenize(text)
    return PassageContentList


def get_sentences_str_from_url(url_str):
    passage_sentence_list = list()
    try:
        plain_txt = html_to_plain_text(url_str)

    except Exception, ex:
        print Exception, ":", ex
        return passage_sentence_list
    sent_list = getSentencesFromPassageText(plain_txt)
    try:
        for sent in sent_list:
            if len(sent) > 0:
                passage_sentence_list.append(sent)
            return passage_sentence_list
    except Exception, ex:
        print Exception, ":", ex
    return passage_sentence_list


def getSentencesFromPassage(urlStr):
    PassageContentList = list()
    try:
        parser = HtmlParser.from_url(urlStr, Tokenizer(LANGUAGE))
    except Exception, ex:
        print Exception, ":", ex
        return PassageContentList
    try:
        if parser.document and parser.document != '':
            if parser.document.sentences and len(parser.document.sentences) > 0:
                for h in parser.document.sentences:
                    PassageContentList.append(h._text.decode('gbk', 'ignore').encode('utf-8'))
                return PassageContentList
    except Exception, ex:
        print Exception, ":", ex
    return PassageContentList


def getPassageFromUrl(urlStr):
    PassageContentList = ''
    try:
        parser = HtmlParser.from_url(urlStr, Tokenizer(LANGUAGE))
    except Exception, ex:
        print Exception, ":", ex
        return PassageContentList
    if parser.document:
        if parser.document.sentences and len(parser.document.sentences) > 0:
            for h in parser.document.sentences:
                PassageContentList = PassageContentList + (h._text)
    return PassageContentList


def getSentencesDictFromPassageByQuestion(question, passage_sentList):
    tokens = nltk.word_tokenize(question)
    tags = nltk.pos_tag(tokens)
    ners = getAllEntities(tags)
    verbs = getAllVerbs(tags)
    sentDict = getSentenceDictMatchingPatternList(ners, passage_sentList)
    sentDict = getTopScoredSentenceDict(sentDict)
    sentDict = getSentenceDictMatchingPatternList(verbs, sentDict)
    return sentDict


def getTopCombinations(combinationDict):
    CombList = list()
    maxComb = keywithmaxval(combinationDict)
    maxCombVal = combinationDict[maxComb]
    while True and len(combinationDict.keys()) > 0:
        combinationDict.pop(maxComb)
        t_maxComb = keywithmaxval(combinationDict)
        print maxComb, ':', combinationDict[t_maxComb]
        CombList.append(maxComb)
        if combinationDict[t_maxComb] != maxCombVal:

            break
        else:
            maxComb = t_maxComb
    return CombList


def getTopPercentCombinations(combinationDict, keepPercent):
    originalLength = len(combinationDict.keys())
    removePercent = 1 - keepPercent
    resList = list()
    while len(combinationDict.keys()) > 0 and originalLength * removePercent < len(combinationDict.keys()):
        tempList = getTopCombinations(combinationDict)
        resList = resList + tempList
    return resList


import FileUtils


def getQuestionPatternsToFile(path, strContent):
    FileUtils.WriteToFile(path, strContent)


def WriteTupleToFile(path, t):
    s = tupleToStr(t)
    FileUtils.WriteToFile(path, s + '\r\n')


def iif(condition, true_part, false_part):
    return (condition and [true_part] or [false_part])[0]


def secondSentenceSplitor(sentenceList):
    resList = list()
    for sentence in sentenceList:
        tList = re.split('\.\.\.|\', \'', sentence)
        resList = resList + tList
    return resList


def questionPatternMining(firstHalf, secondHalf, var, fileName):
    searchedKeyWords = firstHalf + var + secondHalf
    yahooHead = 'http://global.bing.com/search?q='
    yahooTail = '&intlF=1&setmkt=en-us&setlang=en-us&FORM=SECNEN'
    urlList = getAllLinksFromPage(yahooHead + searchedKeyWords + yahooTail)
    URLNum = 5
    keySentencesText = ''
    for i in range(0, iif(len(urlList) > URLNum, URLNum, len(urlList))):
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
    getQuestionPatternsToFile(fileName, '\n' + keySentencesText)


def talkMod(inputSentence):
    FunctionFlag = False
    SelfFlag = False
    relations = getRelation(inputSentence)
    pnp = get_pnp(inputSentence)
    pnp_string = ''
    if len(pnp) >= 1:
        pnp_string = pnp[0].string
    print type(pnp)
    if len(relations) > 0:

        tDict = getRelationsFromDict(relations)
        for k in tDict.keys():
            values = [(k, tDict[k].OBJ.lower(), tDict[k].VP.lower(), tDict[k].SBJ.lower(), pnp_string)]
            # MySqlHelper.insert(db_list, values, "insert into relation values(%s,%s,%s,%s,%s)")

            if tDict[k].SBJ.lower() == 'me'.lower():
                #            FunctionFlag = True
                break
            if tDict[k].OBJ.lower() == 'I'.lower():
                #            FunctionFlag = True
                break
        # MySqlHelper.select(db_list, "select * from relation")
    if FunctionFlag == True:
        FunctionMod(inputSentence)
    elif SelfFlag == True:
        LocalSearch(inputSentence)
    else:
        if len(relations) > 0:
            print conversation_with_relation(tDict[k].OBJ.lower(), tDict[k].VP.lower(), tDict[k].SBJ.lower(), pnp_string)
        else:
            conversation(inputSentence)
    return ''


def InsertRelationsFromStrArticle(article_str, db_info_list):
    """

    :param article_str: string
    :param db_info_list: database connection info
    """
    sentenceslist = getSentencesFromPassageText(article_str)
    sentenceslist = secondSentenceSplitor(sentenceslist)
    for sent in sentenceslist:
        relations = getRelation(sent)
        pnp = get_pnp(sent)
        pnp_string = ''
        if len(pnp) >= 1:
            pnp_string = pnp[0].string
        if len(relations) > 0:
            tDict = getRelationsFromDict(relations)
            for k in tDict.keys():
                values = [(k, tDict[k].OBJ.lower(), tDict[k].VP.lower(), tDict[k].SBJ.lower(), pnp_string)]
                MySqlHelper.insert(db_info_list, values, "insert into relation values(%s,%s,%s,%s,%s)")
    MySqlHelper.select(db_info_list, "select * from relation")


def LocalSearch():
    print 'LocalSearch'


def FunctionMod(inputSentence):
    print 'FunctionMod'


def WebSearch(inputSentence):
    print 'WebSearch'


WHAT_IS_STR = "what is"
GIVE_REMARKS_STR = "what do you think of "


def processInputSentence(inputSentence, searchExtraStr):
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
    inputSentence = processInputSentence(inputSentence, SearchExtraStr)
    questionMod(SearchExtraStr + inputSentence, DEFAULT)


def replace_part(sbj, vp, obj, means):
    str_list = [sbj, vp, obj, means]
    search_str = sbj + " " + obj + means
    sents_sorted = questionMod(search_str,DEFAULT)
    for sent in sents_sorted:
        if vp in sent:
            continue
        else:
            return sent
    return  sents_sorted[0]
def make_topic(sbj, vp, obj, means):
    return replace_part(sbj, vp, obj, means)

def conversation_with_relation(sbj, vp, obj, means):
    return make_topic(sbj, vp, obj, means)

def TopicSelector():
    r = random.randint(TELL_REASON, GIVE_REMARKS)
    MapDict = {
        TELL_REASON: "why ",
        TELL_DEFINATION: "defination of ",
        TELL_SIMILAR: " also ",
        TELL_RESULT: " so ",
        GIVE_REMARKS: "what do you think of "
    }
    print MapDict[r]
    return MapDict[r]


def getSearchExtraStr(inputSentence):
    return TopicSelector()


def questionMod(inputSentence, qType):
    patternList = questionPatternLoader(qType)
    print '====================================================='
    backupAnwsersDict = {}
    SentencesList = getRelatedSentencesListFromWeb(inputSentence)
    for sentence in SentencesList:
        strSent = sentence
        for pat in patternList:
            if PipLineTest.CombinationInSentence(pat, strSent):
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
    keyDict = listToDict(getVPListFromStr(inputSentence))
    keyNPDict = listToDict(getNPListFromStr(inputSentence))
    print '--------------------    key words  ----------------------'
    print keyDict
    print '--------------------After filtering ---------------------'
    for k in backupAnwsersDict.keys():
        corpusSentenceDict = listToDict(getVPListFromStr(k))
        print 'verbs from text ', corpusSentenceDict
        print 'verbs form question ', keyDict
        verbScore = wordDictRelation(corpusSentenceDict, keyDict)
        corpusSentenceDict = listToDict(getNPListFromStr(k))
        print 'nouns from text ', corpusSentenceDict
        print 'nouns form question ', keyNPDict
        NounScore = wordDictRelation(corpusSentenceDict, keyNPDict)
        noun_weight = 0.7
        backupAnwsersDict[k] = (1-noun_weight)*verbScore + noun_weight*NounScore
    # sentD = filterSentencesByWords(backupAnwsersDict.keys(), keyDict.keys())
    sentD = backupAnwsersDict
    sentD = sorted(sentD.iteritems(), key=lambda d: d[1], reverse=True)
    for s in sentD:
        print s
    return sentD

def InputClassifier(InputStr):
    questionType = getQuestionTypeFromTypeList([HOW, WHAT, WHO, WHERE, WHEN, DEFAULT], InputStr.lower())
    if questionType == DEFAULT:
        talkMod(InputStr)
    else:
        questionMod(InputStr, questionType)


def getRelatedSentencesListFromWeb(searchedKeyWords):
    yahooHead = 'http://global.bing.com/search?q='
    yahooTail = '&intlF=1&setmkt=en-us&setlang=en-us&FORM=SECNEN'
    urlList = getAllLinksFromPage(yahooHead + searchedKeyWords + yahooTail)

    URLNum = 3
    keySentencesText = ''
    articleStrList = list()
    for i in range(0, iif(len(urlList) > URLNum, URLNum, len(urlList))):
        passageSentences = html_to_plain_text(urlList[i][0])

        articleStrList.append(passageSentences)

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
    # for a single article remove the summary sentences,leaving only the details.
    # then extract patterns from only the details
    return MainSearchResultSentencesList








def getOntologyKnowledge(relationTupleList):
    OntoList = list()
    for r in relationTupleList:
        OntologyBody = body(r.SBJ)
        name = r.SBJ
        OntologyBody.SLOTList.append(slot(r.VP, r.OBJ))
        for rt in relationTupleList:
            if rt.SBJ.lower() == name.lower():
                OntologyBody.SLOTList.append(slot(rt.VP, rt.OBJ))
                print OntologyBody
                relationTupleList.remove(rt)
        if len(OntologyBody.SLOTList) > 1:
            OntoList.append(OntologyBody)

    return OntoList


if __name__ == "__main__":
    txt = '''jill is a nice name. Pick up fresh fruit from the farmer's market or your local grocery store
    and make sure that they are nice and ripe and ready to be made into a salad.
    If they are not ripe enough, then the salad will be a bit tough to chew.
     It is better for them to be a bit overripe than unripe so that the flavors blend.
     For this simple fruit salad, you'll need strawberries, cherries, blueberries, red apples, peaches, and a kiwi.'''
    txt = txt.lower()
    # entity_List = getNPListFromStr(txt)
    # InsertRelationsFromStrArticle(txt, db_list)

    question = 'an iphone is better than an android phone'
    tokens = nltk.word_tokenize(question)
    tags = nltk.pos_tag(tokens)
    print tags
    talkMod(question)
