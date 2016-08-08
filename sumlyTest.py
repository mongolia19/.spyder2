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
# give more weight to nouns than to verbs while scoring sentences
# classify questions into every kind of wh-words : who where which when and so on
# use more than one taggers to tag a sentence to increase precision
# Only extract the sentences that do not contain interrogatives such as what how why
# Base on a conversation script to learn talking patterns
# search the web with the first sentence then in the resluts find the sentences that
# are similar to the original answer ,take them as the answer data base to a certain question
# extract specific relations such like is-a,isinstanceOf,After,Before
# to make bodies of Ontology automatically
# if we have already extracted out a relation A r B,how to evaluate the
# relation r ?
# search the web with A and B ,then extract realtions containing A x X
# check how many relation r re-appears this time in all relations{ x }
# the higher the percentage is the more reliable the relation r is.

# before comparing word in sentences and word in question, we should turn them into
# lower case as well as singular form


#Extract answer patterns for each kind of questions
#First we set a group of patterns for each kind of questions
#We use this set of patterns to extract answers
#From the newly extracted answers we get the most frequently
#appeared patterns. Then use the new patterns to update the patterns used in last search

import re

import random

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer_lsa
from sumy.summarizers.lex_rank import LexRankSummarizer as Summarizer_lex
from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer_text
from sumy.summarizers.luhn import LuhnSummarizer as Summarizer_luhn
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk

from pattern.en import parsetree
# import MySqlHelper
from wordNet import wordDictRelation, hit_percent_in_sentenceStr
from wordNet import getVPListFromStr
from wordNet import getNPListFromStr
from wordNet import wordInSentStr
from wordNet import getAllEntities, getAllVerbs, getSentenceDictMatchingPatternList, getTopScoredSentenceDict
from wordNet import getAllNumbers, getAllProperEntities, getAllPronounEntities
from wordNet import sentence_parse
from wordNet import get_synsets
from wordNet import get_verb_list_hit
import PipLineTest
from wordNet import listToDict
from wordNet import getAllLinksFromPage
from wordNet import html_to_plain_text
from wordNet import word_list_in_sentenceStr ,all_word_list_in_sentenceStr
from wordNet import get_lemma_of_word
import textblob
import copy
import Levenshtein
import FileUtils
import threading
from time import ctime,sleep

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
HOWTO = 'how to'
DEFAULT = 'default'
LANGUAGE = "english"
TELL_REASON = 0
TELL_DEFINATION = 1
TELL_SIMILAR = 2
TELL_RESULT = 3
GIVE_REMARKS = 4

articlesFromHtmls = list()  # used to store each article from one search
embeddings = None

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


SENTENCES_COUNT = 10
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


from pattern.search import match

SENTENCES_STRUCT_1 = 'NP VP'
SENTENCES_STRUCT_2 = 'NP VP NP (VP) (NP)'
SENTENCES_STRUCT_3 = 'NP VP NP NP'
SENTENCES_STRUCT_4 = 'NP VP ADJP|PP|VP (NP)'
SENTENCES_STRUCT_5 = '{NP|WP} {VP} {NP} ADJP|VP|PP (NP)'
#boolean
YESNO_QUESTION = ['is','are','or not']
SELECTION_QUESTION = ['or']
#short questions
PERSON_QUESTION = ['who']
LOCATION_QUESTION = ['where']
TIME_QUESTION = ['when','what time']
QUANTITY_QUESTION = ['how much', 'how many', 'how long', 'how far', 'how small', 'how near']
OBJECT_QUESTION  = ['what']
#long questions
METHOD_QUESTION = ['how to']
DEFINITION_QUESTION = ['what is','DEFINITION']
PERSONDEF_QUESTION = ['where']
REASON_QUESTION = ['why']

Loc_Pattern = 'IN (.*)NNP'
Time_Pattern = 'IN (.*)CD'
QUANTITY_Pattern = 'CD (.*)N*'

from pattern.search import Pattern


def sentence_structure_finder(sent_str, pattern_str):
    s = parsetree(sent_str, lemmata=True)
    p = Pattern.fromstring(pattern_str)
    pattern_list = p.search(s)
    if pattern_list is None or len(pattern_list) == 0:
        return None
    if s is None:
        return None
    m = pattern_list[0]
    # try:
    #     if match(pattern_str, s) is None:
    #         return None
    #     else:
    #         m = match(pattern_str, s)
    # except:
    #     return None
    if m is None:
        return None
    for w in m.words:
        print w, '\t =>', m.constraint(w)
    return m.constituents()


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
    text_array = text.split()
    text_str = ''
    for t in text_array:
        try:

            t = t.decode('gbk', 'strict')
            text_str += ' ' + t
        except:
            continue
    PassageContentList = nltk.sent_tokenize(text_str)
    return PassageContentList


def get_sentences_str_from_url(url_str):
    passage_sentence_list = list()
    try:
        plain_txt = html_to_plain_text(url_str)
        if plain_txt == '':
            print 'plain_txt is empty in get_sentences_str_from_url '
            return passage_sentence_list
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


def get_all_entities_by_nltk(sent_string):
    tokens = nltk.word_tokenize(sent_string)
    tags = nltk.pos_tag(tokens)
    ners = getAllEntities(tags)
    return ners


def get_tagged_sentence(sent_string):
    tokens = nltk.word_tokenize(sent_string)
    tags = nltk.pos_tag(tokens)
    return tags

def tagString_of_sentence(sent_string):
    word_tag_pair_list = get_tagged_sentence(sent_string)
    tag_str = ''
    for pair in word_tag_pair_list:
        tag_str = tag_str + " " + pair[1]
    return tag_str

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


def extract_ner_from_str_by_textblob(text):
    blob = textblob.TextBlob(text)
    t_list = list()
    for n in blob.noun_phrases:
        t_list.append(n)
    return t_list


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
        # tList = re.split('(\.\.\.|\', \')|(\|)|(\*)', sentence)
        tList = re.split("(\|)|(\*)|(-+)|(\.)|(\n)|(\?)|(\r\n)", sentence)
        resList = resList + tList
    rlist = list()
    for s in range(0, len(resList)):
        if resList[s] is None:
            continue
        else:
            rlist.append(resList[s])
    return rlist


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
        summarizer = Summarizer_lex(stemmer)
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
        print conversation_with_sent_structure_ansys(inputSentence)
        # if len(tDict.keys()) > 0:
        #     k = ''
        #     print len(tDict.keys())
        #     for r in tDict.keys():
        #         k = r
        #     print 'key is ', k
        #     print conversation_with_relation(tDict[k].OBJ.lower(), tDict[k].VP.lower(), tDict[k].SBJ.lower(),
        #                                      pnp_string)
        # else:
        #     conversation(inputSentence)
    return ''


# def InsertRelationsFromStrArticle(article_str, db_info_list):
#     """
#
#     :param article_str: string
#     :param db_info_list: database connection info
#     """
#     sentenceslist = getSentencesFromPassageText(article_str)
#     sentenceslist = secondSentenceSplitor(sentenceslist)
#     for sent in sentenceslist:
#         relations = getRelation(sent)
#         pnp = get_pnp(sent)
#         pnp_string = ''
#         if len(pnp) >= 1:
#             pnp_string = pnp[0].string
#         if len(relations) > 0:
#             tDict = getRelationsFromDict(relations)
#             for k in tDict.keys():
#                 values = [(k, tDict[k].OBJ.lower(), tDict[k].VP.lower(), tDict[k].SBJ.lower(), pnp_string)]
#                 MySqlHelper.insert(db_info_list, values, "insert into relation values(%s,%s,%s,%s,%s)")
#     MySqlHelper.select(db_info_list, "select * from relation")


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


def muti_sentence_structure_finder(sentence_str):
    match_list = list()
    structlist = [SENTENCES_STRUCT_5,
                  SENTENCES_STRUCT_4,
                  SENTENCES_STRUCT_3,
                  SENTENCES_STRUCT_2,
                  SENTENCES_STRUCT_1]
    for struct in structlist:
        match_list = sentence_structure_finder(sentence_str, struct)
        if match_list is not None and len(match_list) > 0:
            break
    if match_list is not None and len(match_list) > 0:
        return match_list
    else:
        return None


def heuristic_sentence_breaker(sentence_str):
    match_list = list()
    structlist = [SENTENCES_STRUCT_5,
                  SENTENCES_STRUCT_4,
                  SENTENCES_STRUCT_3,
                  SENTENCES_STRUCT_2,
                  SENTENCES_STRUCT_1]
    for struct in structlist:
        match_list = sentence_structure_finder(sentence_str, struct)
        if match_list is not None and len(match_list) > 0:
            break
    res_str = ''
    if len(match_list) >= 2:
        match_list.pop()
        for chunk in match_list:
            res_str = res_str + " " + chunk.string
    else:
        res_str = sentence_str
    return res_str


def replace_part(sbj, vp, obj, means):
    str_list = [sbj, vp, obj, means]
    search_str = sbj + " " + vp + " " + means
    sents_sorted = questionMod(search_str, DEFAULT)
    for sent in sents_sorted:
        if vp in sent:
            continue
        else:
            return sent
    return sents_sorted[0]


def make_topic(sbj, vp, obj, means):
    return replace_part(sbj, vp, obj, means)


def conversation_with_relation(sbj, vp, obj, means):
    return make_topic(sbj, vp, obj, means)


def conversation_with_sent_structure_ansys(sent_str):
    # search_str = heuristic_sentence_breaker(sent_str)
    sents_sorted = questionMod("why " + sent_str, DEFAULT)
    return sents_sorted[0]


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


from wordNet import wordInSentStr


def filter_sentences_containing_interrogatives(sentence_str, filter_list):
    for f in filter_list:
        if wordInSentStr(f, sentence_str):
            return True
    return False


def filter_sentences_containing_string(sentence_str, filter_str):
    if filter_str in sentence_str:
        return True
    else:
        return False


def get_summary_sentences_from_article_text(article_text):
    parser = PlaintextParser.from_string(article_text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer_lex(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    sum_list = list()
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        ks = sentence._text.decode('gbk', 'ignore').encode('utf-8')
        sum_list.append(ks)
    return sum_list

def get_summary_sentences_from_article_text_with_summarizer(article_text, summarizer_f):
    if len(article_text)<10:
        return None
    parser = PlaintextParser.from_string(article_text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = summarizer_f(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    sum_list = list()
# to do
    for sentence in summarizer(parser.document, SENTENCES_COUNT+1):
        ks = sentence._text.decode('gbk', 'ignore').encode('utf-8')
        sum_list.append(ks)
    return sum_list

def get_summary_sentences_by_summarizer_voting(article_text):
    lex_sum_list = (get_summary_sentences_from_article_text_with_summarizer(article_text,Summarizer_lex))
    lsa_sum_list = get_summary_sentences_from_article_text_with_summarizer(article_text, Summarizer_lsa)
    text_sum_list = get_summary_sentences_from_article_text_with_summarizer(article_text, Summarizer_text)
    luhn_sum_list = get_summary_sentences_from_article_text_with_summarizer(article_text, Summarizer_luhn)
    parser = PlaintextParser.from_string(article_text, Tokenizer(LANGUAGE))
    sum_list = list()
    for p in parser.document.sentences:
        sent_str = p._text.decode('gbk', 'ignore').encode('utf-8')
        vote_count = 0
        if sent_str in lex_sum_list:
            vote_count = vote_count + 1
        if sent_str in text_sum_list:
            vote_count = vote_count + 1
        if sent_str in lsa_sum_list:
            vote_count = vote_count + 1
        if sent_str in luhn_sum_list:
            vote_count = vote_count + 1
        if vote_count >=2:
            sum_list.append((sent_str, vote_count))
    return sum_list

def get_summary_sentences_from_article_text_sentiment(article_text):
    import math
    parser = PlaintextParser.from_string(article_text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer_lex(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    sum_list = list()
    sent_list = parser.document.sentences
    last_sent = sent_list[len(sent_list)-1]
    last_sent =last_sent._text.decode('gbk', 'ignore').encode('utf-8')
    for paragraph in parser.document.paragraphs:
        for sent in paragraph.sentences:
            print sent._text.decode('gbk', 'ignore').encode('utf-8')
    # for sentence in summarizer(parser.document, SENTENCES_COUNT):
    #     ks = sentence._text.decode('gbk', 'ignore').encode('utf-8')
    #     sum_list.append(ks)
    sent_with_sentiment = Sentiment(article_text)
    sent_score_list = list()
    for i in range(0,len(sent_with_sentiment)-1):
        sent_score_list.append(math.fabs(sent_with_sentiment[i][1]-sent_with_sentiment[i+1][1]))
    max_index = sent_score_list.index( max(sent_score_list))
    print sent_score_list
    sent_with_sentiment = sorted(sent_with_sentiment, key=lambda d: d[1], reverse=True)
    keySentences= [sent_with_sentiment[0],sent_with_sentiment[len(sent_with_sentiment)-1], sent_with_sentiment[max_index+1],last_sent]

    return keySentences

def summary_article(article_str):
    key_sents = get_summary_sentences_by_summarizer_voting(article_str)
    nerList = list()
    for k_sent in key_sents:
        ners = get_all_entities_by_nltk(k_sent[0])
        nerList = nerList + ners
    nerlist = list(set(nerList))
    return [key_sents,nerlist]

def get_chunks_in_sentence(sent_str):
    if (not sent_str) or (len(sent_str) <=1) or (sent_str == ""):
        return []
    s = parsetree(sent_str, relations=True, lemmata=True)
    sent = s[0]
    chunk_list = list()
    for chunk in sent.chunks:
        chunk_list.append(chunk)
    return chunk_list


def summary_over_article_text(article_text):
    # summary_sentences = get_summary_sentences_from_article_text(article_text)
    parser = PlaintextParser.from_string(article_text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer_lex(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    sum_list = list()
    total_list = list()
    place_sent_list = list()
    time_sent_list = list()
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        ks = sentence._text.decode('gbk', 'ignore').encode('utf-8')
        sum_list.append(ks)
    key_named_entities = list()
    for s in sum_list:
        print "summary", s
        ner_list = get_all_entities_by_nltk(s)
        key_named_entities += ner_list

    # print 'nouns ', ner_list
    for p in parser.document.sentences:
        sent_str = p._text.decode('gbk', 'ignore').encode('utf-8')
        if len(sent_str.strip().split()) > 3:
            total_list.append(sent_str)
            for key in key_named_entities:
                if wordInSentStr(key, sent_str):
                    sum_list.append(sent_str)
            s = parsetree(sent_str, relations=True, lemmata=True)
            # print 'subjects', s[0].subjects
            # print 'verbs', s[0].verbs
            # print 'objects', s[0].objects
            # print 'relations', s[0].relations
            #
            if s[0].pnp is not None and len(s[0].pnp) > 0:
                print 'pnp', s[0].pnp
                pnp_str = s[0].pnp[0].string
                tagged_pnp = get_tagged_sentence(pnp_str)
                if getAllNumbers(tagged_pnp) is not None:
                    time_sent_list.append(sent_str)
                if getAllProperEntities(tagged_pnp) is not None:
                    place_sent_list.append(sent_str)
        print '-------------------------'
    result_tuple = [list(), sum_list, total_list, time_sent_list, place_sent_list]
    return result_tuple
    # for sentence in s:
    #     for chunk in sentence.chunks:
    #         print chunk.type, [(w.string, w.type) for w in chunk.words]
    # temp_dict = getRelation(sent_str)
    # relation_dict = getRelationsFromDict(temp_dict)
    # for k in relation_dict.keys():
    #
    #     print "OBJ ", relation_dict[k].OBJ.lower(), "VP", relation_dict[k].VP.lower(), "SBJ", relation_dict[k].SBJ.lower()



def questionMod(inputSentence, qType):
    # return a tuple list: tuple (str, score)
    patternList = questionPatternLoader(qType)
    print '========== question mod entered ============'
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
                    # print strSent
                    # print '-------extracted---------------------------'
                    # s = parsetree(strSent, relations=True, lemmata=True)
                    # print 'subjects', s[0].subjects
                    # print 'verbs', s[0].verbs
                    # print 'objects', s[0].objects
                    # print 'relations', s[0].relations
                    # print 'pnp', s[0].pnp
    keyDict = listToDict(getVPListFromStr(inputSentence))
    # np_list = getNPListFromStr(inputSentence)
    # np_list1 = extract_ner_from_str_by_textblob(inputSentence)
    filter_list = [HOW, WHAT, WHERE, WHO, WHY, WHEN, 'HyperText', 'RDFa', 'W3C', 'HTML', 'Michael', 'JavaScript']

    print '--------------------    key words  ----------------------'
    print keyDict
    print '--------------------After filtering ---------------------'
    back_sent_list = list()
    for k in backupAnwsersDict.keys():
        if filter_sentences_containing_interrogatives(k, filter_list):
            backupAnwsersDict.pop(k)
            continue
        if filter_sentences_containing_string(k, 'HTML Working Group'):
            continue
        back_sent_list.append(k)
        # corpusSentenceDict = listToDict(getVPListFromStr(k))
        # print 'verbs from text ', corpusSentenceDict
        # print 'verbs form question ', keyDict
        # verbScore = wordDictRelation(corpusSentenceDict, keyDict)
        # corpusSentenceDict = listToDict(getNPListFromStr(k))
        # print 'nouns from text ', corpusSentenceDict
        # print 'nouns form question ', keyNPDict
        # NounScore = wordDictRelation(corpusSentenceDict, keyNPDict)
        # noun_weight = 0.7
        # backupAnwsersDict[k] = (1 - noun_weight) * verbScore + noun_weight * NounScore
    # sentD = filterSentencesByWords(backupAnwsersDict.keys(), keyDict.keys())
    total_txt = ''
    for s in back_sent_list:
        total_txt = total_txt + ' ' + s
    total_txt = total_txt.strip()
    if len(back_sent_list) == 0 or len(total_txt) < 3:
        return list()
    simVal_list = similarity(back_sent_list, total_txt)
    i = 0
    for k in backupAnwsersDict.keys():
        backupAnwsersDict[k] = simVal_list[i]
        i += 1

    sentD = backupAnwsersDict
    sentD = sorted(sentD.iteritems(), key=lambda d: d[1], reverse=True)
    # for s in sentD:
    #     print s
    #     temp_relation = getRelation(s[0])
    #     temp_dict = getRelationsFromDict(temp_relation)
    #     for k in temp_dict.keys():
    #         print temp_dict[k].OBJ.lower(), temp_dict[k].VP.lower(), temp_dict[k].SBJ.lower()
    return sentD


def InputClassifier(InputStr):
    questionType = getQuestionTypeFromTypeList([HOW, WHAT, WHO, WHERE, WHEN, DEFAULT], InputStr.lower())
    if questionType == DEFAULT:
        talkMod(InputStr)
    else:
        questionMod(InputStr, questionType)
def wordListInString(wordList, String):
    for word in wordList:
        if word in String:
            return True
    return False

def questionPatternSelector(questionStr):
    # word_list_in_sentenceStr(TIME_QUESTION, questionStr)
    if wordListInString(TIME_QUESTION, questionStr.lower()):
        print 'question about time'
        return Time_Pattern
    if wordListInString(LOCATION_QUESTION, questionStr.lower()):
        print 'question about location'
        return Loc_Pattern
    if wordListInString(QUANTITY_QUESTION, questionStr.lower()):
        print 'question about quantity'
        return QUANTITY_Pattern
    return ' '

def get_all_sentences_list_from_web(search_content):
    yahooHead = 'http://global.bing.com/search?q='
    yahooTail = '&intlF=1&setmkt=en-us&setlang=en-us&FORM=SECNEN'
    urlList = getAllLinksFromPage(yahooHead + search_content + yahooTail)

    URLNum = 10
    keySentencesText = ''
    all_sentence_List = list()
    for i in range(0, iif(len(urlList) > URLNum, URLNum, len(urlList))):
        passageSentences = html_to_plain_text(urlList[i][0])

        parser = PlaintextParser.from_string(passageSentences, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)
        summarizer = Summarizer_lex(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        if len(parser.document.sentences) == 0:
            continue
        for sentence in parser.document.sentences:
            ks = sentence._text.decode('gbk', 'ignore').encode('utf-8')
            print ks
            all_sentence_List.append(ks)
    return all_sentence_List
ENGLISH_STOP_WORDS = frozenset([
    "a", "about", "above", "across", "after", "afterwards", "again", "against",
    "all", "almost", "alone", "along", "already", "also", "although", "always",
    "am", "among", "amongst", "amoungst", "amount", "an", "and", "another",
    "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
    "around", "as", "at", "back", "be", "became", "because", "become",
    "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
    "below", "beside", "besides", "between", "beyond", "bill", "both",
    "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con",
    "could", "couldnt", "cry", "de", "describe", "detail", "do", "done",
    "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
    "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
    "everything", "everywhere", "except", "few", "fifteen", "fify", "fill",
    "find", "fire", "first", "five", "for", "former", "formerly", "forty",
    "found", "four", "from", "front", "full", "further", "get", "give", "go",
    "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
    "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his",
    "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
    "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
    "latterly", "least", "less", "ltd", "made", "many", "may", "me",
    "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
    "move", "much", "must", "my", "myself", "name", "namely", "neither",
    "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
    "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on",
    "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
    "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
    "please", "put", "rather", "re", "same", "see", "seem", "seemed",
    "seeming", "seems", "serious", "several", "she", "should", "show", "side",
    "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhere", "still", "such",
    "system", "take", "ten", "than", "that", "the", "their", "them",
    "themselves", "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they", "thick", "thin",
    "third", "this", "those", "though", "three", "through", "throughout",
    "thru", "thus", "to", "together", "too", "top", "toward", "towards",
    "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
    "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby",
    "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
    "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
    "within", "without", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves"])
def sentence2wordStr_removeStopWords(sentStr,stopWordList):
    tokens = nltk.word_tokenize(sentStr)
    wordStr = ''
    if len(tokens)<=3:
        return ""
    for token in tokens:
        if token.lower().strip() in stopWordList:
            continue
        wordStr = wordStr + token + ' '
    return wordStr

# import sklearn.feature_extraction.ENGLISH_STOP_WORDS as stop_words_list

def getRelatedSentencesListFromWeb(searchedKeyWords):
    yahooHead = 'http://global.bing.com/search?q='
    yahooTail = '&intlF=1&setmkt=en-us&setlang=en-us&FORM=SECNEN'
    local_search_engine = "http://192.168.0.7:8000/search?content=wikipedia_en_all_simple_nopic_2015-02&pattern="
    # urlList = getAllLinksFromPage(local_search_engine + searchedKeyWords)
    urlList = getAllLinksFromPage(yahooHead + searchedKeyWords + yahooTail)

    URLNum = 10
    keySentencesText = ''
    articleStrList = list()
    for i in range(0, iif(len(urlList) > URLNum, URLNum, len(urlList))):
        passageSentences = html_to_plain_text(urlList[i][0])

        articleStrList.append(passageSentences)

        parser = PlaintextParser.from_string(passageSentences, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)
        summarizer = Summarizer_lex(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        if len(parser.document.sentences) == 0:
            break
        for sentence in parser.document.sentences:
            #            print(type(sentence))
            #            print(sentence)
            ks = sentence._text.decode('gbk', 'ignore').encode('utf-8')
            # print ks
            keySentencesText = keySentencesText + ' ' + ks
    MainSearchResultSentencesList = getSentencesFromPassageText(keySentencesText)
    MainSearchResultSentencesList = secondSentenceSplitor(MainSearchResultSentencesList)
    # write sentences in format w,w,w, to file
    global question_countor
    if question_countor >5:
        question_countor = 0
        writeEmpty = file('./text/rawtext/data.txt', 'w')
        writeEmpty.write('')
        writeEmpty.close()
    read = file('./text/rawtext/data.txt', 'a+')
    for s in MainSearchResultSentencesList:

        lineStr = sentence2wordStr_removeStopWords(s, ENGLISH_STOP_WORDS)
        if len(lineStr)<=1 or len(lineStr)>15:
            continue
        read.write("\r\n")
        read.write(lineStr)
    read.close

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


import logging
from gensim import corpora, models, similarities


def similarity(sent_list, total_corp):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    class MyCorpus(object):
        m_sentence_list = list()

        def fill_sent_list(self, l):
            self.m_sentence_list = l

        def __iter__(self):
            for line in self.m_sentence_list:
                yield line.split()

    Corp = MyCorpus()
    Corp.fill_sent_list(sent_list)
    dictionary = corpora.Dictionary(Corp)
    corpus = [dictionary.doc2bow(text) for text in Corp]

    lsi = models.LsiModel(corpus)

    corpus_lsi = lsi[corpus]

    query = total_corp
    vec_bow = dictionary.doc2bow(query.split())
    vec_lsi = lsi[vec_bow]

    index = similarities.MatrixSimilarity(corpus_lsi)
    sims = index[vec_lsi]

    similarity_list = list(sims)

    return similarity_list
import apriori_norule


def dataFromFile(fname):
    """Function which reads from the file and yields a generator"""
    file_iter = open(fname, 'rU')
    for line in file_iter:
        line = line.strip().rstrip(',')  # Remove trailing comma
        record = frozenset(line.split(','))
        yield record
def sent_word_list_generator(sentenceList, stopWordList):
    for sent in sentenceList:
        sent = sent.rstrip(',')  # Remove trailing comma
        # '\s'
        wordlist = list()
        for w in sent.split(' '):
            if w == '' or len(w)<=1:
                continue
            else:
                wordlist.append(w)
        record = frozenset(wordlist)
        yield record

def sent_word_list_generator_blank(sentenceList, stopWordList):
    recorList = list()
    for sent in sentenceList:
        sent = sent.rstrip(',')  # Remove trailing comma
        # '\s'
        wordlist = list()
        for w in sent.split(' '):
            if w == '' or len(w)<=1:
                continue
            else:
                wordlist.append(w)
        record = (wordlist)
        if len(record)>0:
            recorList.append(record)
    return recorList
def sent_word_list_generator_comma(sentenceList, stopWordList):
    recorList = list()
    for sent in sentenceList:
        sent = sent.rstrip(',')  # Remove trailing comma
        # '\s'
        wordlist = list()
        for w in sent.split(','):
            if w == '' or len(w)<=1:
                continue
            else:
                wordlist.append(w)
        record = (wordlist)
        if len(record) > 0:
            recorList.append(record)
    return recorList

def self_learn_by_apriori(folder_path, out_put_path, stopWordList):
    sent_word_list = list()
    articleStringList = FileUtils.getContentStrListFromRawTextPath(folder_path)

    for article in articleStringList:
        sentenceList = secondSentenceSplitor( getSentencesFromPassageText(article))
        f_set =  sent_word_list_generator_blank(sentenceList, stopWordList)
        if len(f_set)<=0:
            continue
        sent_word_list = sent_word_list + f_set
        # sent_word_list = apriori.dataFromFile()
        # for sent in sentenceList:
        #     sent = sent.strip().rstrip(',')  # Remove trailing comma
        #     record = frozenset(sent.split(','))
        #     yield record
            # sent_word_list.append(frozenset(sentence2wordStr_removeStopWords(sent, stopWordList).split(',')))
    print "finish loading words"
    # apriori.
    # rules = apriori(sent_word_list, 0.07)
    rules = apriori_norule.apriori(sent_word_list, 0.8)

    print "rules:"
    for rule in rules:
        print rule
    return rules
import fp_Growth

def self_learn_by_fp_growth(folder_path, out_put_path, stopWordList):
    sent_word_list = list()
    articleStringList = FileUtils.getContentStrListFromRawTextPath(folder_path)

    for article in articleStringList:
        sentenceList = secondSentenceSplitor( getSentencesFromPassageText(article))
        f_set =  sent_word_list_generator_blank(sentenceList, stopWordList)
        if len(f_set)<=0:
            continue
        sent_word_list = sent_word_list + f_set
        # sent_word_list = apriori.dataFromFile()
        # for sent in sentenceList:
        #     sent = sent.strip().rstrip(',')  # Remove trailing comma
        #     record = frozenset(sent.split(','))
        #     yield record
            # sent_word_list.append(frozenset(sentence2wordStr_removeStopWords(sent, stopWordList).split(',')))
    print "finish loading words"
    # apriori.
    # rules = apriori(sent_word_list, 0.07)
    rules = fp_Growth.tree_builder.tree_builder(sent_word_list, len(sent_word_list)*0.1)
    ruleList = list()
    for r in rules.SortedRoutines:
        ruleList.append(r.strip().split(' '))
    print 'rules are :'
    for r in ruleList:
        print r
    return ruleList


def if_rules_repeated(rule_setA, rule_setB):
    setA = (rule_setA)
    setB = (rule_setB)
    setLen = len(setA)
    if setLen != len(setB):
        return False
    else:
        if len(setA.intersection(setB)) == setLen:
            return True
        else:
            return False

def self_learn_by_question_answer(local_text_seed_article, out_put_path, similarity_tol):
    f = open(local_text_seed_article, 'r')
    raw_text = f.read()
    raw_text = raw_text.decode('gbk', 'ignore').encode('utf-8')
    sent_str_list = getSentencesFromPassageText(raw_text)
    print '--------- after splitting, getSentencesFromPassageText'
    sent_str_list = secondSentenceSplitor(sent_str_list)
    if len(sent_str_list) <= 1:
        return
    for n in range(0, len(sent_str_list) - 1):
        question_str = sent_str_list[n]
        answer_str = sent_str_list[n + 1]
        candidate_sent_list = questionMod(question_str, DEFAULT)
        c_list = list()
        c_list.append(answer_str)
        for c in candidate_sent_list:
            # remove the sentences with pronouns
            if len(c[0]) > 0 and len(getAllPronounEntities(get_tagged_sentence(c[0]))) == 0 and is_sentence_complete(c[0]):
                c_list.append(c[0])
            else:
                continue
        total_txt = ''
        for s in c_list:
            total_txt = total_txt + ' ' + s
        total_txt = total_txt.strip()
        simVal_list = similarity(c_list, total_txt)
        # get the sentences that are most like the answer
        for i in range(1, len(c_list)):
            if float(abs(simVal_list[i] - simVal_list[0])) / simVal_list[0] > similarity_tol:
                match_list = muti_sentence_structure_finder(c_list[i])
                if match_list is not None and len(match_list) > 0:
                    if len(filter_when(c_list[i], question_str)) > 0:
                        FileUtils.WriteToFile(out_put_path, c_list[i] + '\r\n')
                        continue

                    match_str_list = list()
                    for chunk in match_list:
                        match_str_list.append(chunk.string)
                    verb_string = evaluate_verb_in_relation_by_search_web(match_list, 0)
                    if verb_string is None:
                        continue
                    else:
                        rel_chunks_list = discover_entity_relation_by_verb(verb_string, match_list[0].string, ' ')
                        for rel_chunks in rel_chunks_list:
                            rel_str = ''
                            for chunk in rel_chunks:
                                rel_str = rel_str + " " + chunk.string
                            FileUtils.WriteToFile(out_put_path, rel_str + '\r\n')


from copy import deepcopy


def evaluate_verb_in_relation_by_search_web(chunk_type_list, tol_val):
    temp_chunk_list = deepcopy(chunk_type_list)
    verb_chunk = None
    sbj_chunk = None
    obj_chunk = None
    np_chunk_list = list()
    for n in range(0, len(temp_chunk_list)):
        if 'VP' in temp_chunk_list[n].tag:
            verb_chunk = temp_chunk_list.pop(n)
            break
    if len(temp_chunk_list) < 2:
        return None
    for n in range(0, len(temp_chunk_list)):
        if np_chunk_list is None or len(np_chunk_list) < 2:
            if 'NP' in temp_chunk_list[n].tag:
                np_chunk_list.append(temp_chunk_list[n])
        else:
            break
    if len(np_chunk_list) <= 1:
        return None
    verb_with_sbj = [np_chunk_list[0].string, verb_chunk.string, np_chunk_list[1].string]
    if evaluate_relation_by_search_web(verb_with_sbj, 0, 0):
        return verb_chunk.string
    else:
        return None


def evaluate_relation_by_search_web(chunk_list, pop_index=-1, tol_val=0):
    if len(chunk_list) <= 2:
        return False
    else:
        search_list = chunk_list
        if pop_index == -1:
            hidden_str = search_list.pop()
        else:
            hidden_str = search_list.pop(pop_index)
        search_str = ''
        for str in search_list:
            search_str = search_str + " " + str
        sent_list = get_all_sentences_list_from_web(search_str)
        half_relation_list = list()
        total_relation_list = list()
        for s in sent_list:
            for w in search_list:
                if wordInSentStr(w, s) == False:
                    continue
            half_relation_list.append(s)
        if len(half_relation_list) == 0:
            return False
        else:
            for s in half_relation_list:
                if wordInSentStr(hidden_str, s):
                    total_relation_list.append(s)
            if float(len(total_relation_list)) / len(half_relation_list) >= tol_val:
                return True
            else:
                return False


def discover_entity_relation_by_verb(verb_str, seed_sbj, seed_obj):
    sent_list = get_all_sentences_list_from_web(seed_sbj + verb_str + seed_obj)
    chunks_list = list()
    noun1 = ''
    noun2 = ''
    for sent in sent_list:
        match_list = muti_sentence_structure_finder(sent)
        if match_list is None:
            continue
        else:
            length = len(match_list)
            if length <= 2:
                continue
            else:
                for n in range(0, length):
                    if (verb_str.lower() in match_list[n].string.lower()) and 'VP' in match_list[n].tag:
                        if n > 0 and 'NP' in match_list[n - 1].tag:
                            noun1 = match_list[n - 1].string
                        if n + 1 < length and 'NP' in match_list[n + 1].tag:
                            noun2 = match_list[n + 1].string
                        if (noun1 != '' and noun2 != '') and \
                                not (noun1 == seed_sbj and noun2 == seed_obj):
                            chunks_list.append(match_list)
    return chunks_list


def get_articles_withURKL_from_websearch_query(query_string):
    real_yahoo_head = 'http://global.bing.com/search?q='
    real_yahoo_tail = '&setlang=en-us&encoding=utf-8'
    yahooHead = 'http://global.bing.com/search?q='
    yahooTail = '&intlF=1&setmkt=en-us&setlang=en-us&FORM=SECNEN'
    real_bing_search_url = yahooHead + query_string + yahooTail
    real_yahoo_search_url = real_yahoo_head + query_string + real_yahoo_tail

    urlList = getAllLinksFromPage(real_yahoo_search_url)
    print "get_articles_withURKL_from_websearch_query called........."
    URLNum = 10
    keySentencesText = ''
    articleStrList = list()
    for i in range(0, iif(len(urlList) > URLNum, URLNum, len(urlList))):
        passageSentences = html_to_plain_text(urlList[i][0])
        print 'html_to_plain_text called in get_articles_withURKL_from_websearch_query'
        # print 'the text is ', passageSentences
        if passageSentences is None or len(passageSentences) <= 3:
            continue
        articleStrList.append((passageSentences, urlList[i][0]))
    return articleStrList


def topic_to_tuple_list(topic):
    art_tuple_str_list = get_articles_withURKL_from_websearch_query(topic)
    art_list = list()
    art_total_str = ''
    for art in art_tuple_str_list:
        art_list.append(art[0])
        assert isinstance(art, tuple)
        art_total_str += " " + art[0]
    score_list = similarity(art_list, art_total_str)
    temp_dict = {}
    for n in range(0, len(art_list)):
        temp_dict[art_list[n]] = score_list[n]
    temp_dict = sorted(temp_dict.iteritems(), key=lambda d: d[1], reverse=True)

    if len(art_tuple_str_list) >= 3:
        main_article = temp_dict[1][0]
    else:
        main_article = temp_dict[0][0]
    main_art_tuple = summary_over_article_text(main_article)
    other_article_list = list()
    for i in temp_dict:
        if i[0] == main_article:
            continue
        else:
            other_article_list.append(i[0])

    sum_list = filter_where(main_article, topic)
    # sum_list = summary_by_comparing_articles(main_article,other_article_list)
    ner_list = main_art_tuple[0]
    summary_list = main_art_tuple[1]
    all_sent_list = main_art_tuple[2]
    time_sent_list = main_art_tuple[3]
    summary_list = sum_list
    result_tuple_list = list()
    # for ner in ner_list:
    # t = (ner, True, False,'')#(content, if is ner , is key sentence, url string)
    # result_tuple_list.append(t)
    for sent in all_sent_list:
        Is_key_sent = False
        for sum_sent in summary_list:
            if sent in sum_sent:
                # sent in time_sent_list or\
                # sent in place_sent_list:
                Is_key_sent = True
                break
        t = (sent, False, Is_key_sent, '')
        result_tuple_list.append(t)
    return result_tuple_list


def get_synsets_lists_from_sentence(question):
    ners = get_all_entities_by_nltk(question)
    n1 = ''
    n2 = ''
    if len(ners) > 0:
        n1 = ners[0]
        if len(ners) > 1:
            n2 = ners[1]
        else:
            n2 = n1
    n1_syn = list()
    n2_syn = list()
    if n1 != '':
        n1_syn = get_synsets(n1)
    if n1 != n2:
        n2_syn = get_synsets(n2)
    else:
        n2_syn = n1_syn
    return [n1_syn,n2_syn]


def filter_where(article, question):
    ners = get_all_entities_by_nltk(question)
    verbs = getAllVerbs(get_tagged_sentence(question))
    n1 = ''
    n2 = ''
    if ners:
        n1 = ners[0]
        if len(ners) > 1:
            n2 = ners[1]
        else:
            n2 = n1
    n1_syn = list()
    n2_syn = list()
    if n1 != '':
        n1_syn = get_synsets(n1)
        n1_temp_list = list()
        for n in n1_syn:
            n1_temp_list.append(n.lower())
        n1_syn = n1_temp_list
    if n1 != n2:
        n2_syn = get_synsets(n2)
    else:
        n2_syn = n1_syn
    summary_text_list = list()
    main_art_sent_list = getSentencesFromPassageText(article)
    main_art_sent_list = secondSentenceSplitor(main_art_sent_list)
    for sent in main_art_sent_list:
        if (n1 != '' and word_list_in_sentenceStr(n1_syn, sent.lower())) or (
                n2 != '' and word_list_in_sentenceStr(n2_syn, sent.lower())):
            pnp = get_pnp(sent)
            if pnp is not None and len(pnp) >= 1:
                pnp_string = pnp[0].string
                if getAllProperEntities(get_tagged_sentence(pnp_string)) \
                        and len(getAllProperEntities(get_tagged_sentence(pnp_string))) > 0:
                    summary_text_list.append(sent)
    summary_text_list = sort_sentence_by_verb_hit(verbs, summary_text_list)
    return summary_text_list


def filter_when(article, question):
    # relations = getRelation(question)
    # pnp = get_pnp(question)
    # pnp_string = ''
    # if len(pnp) >= 1:
    #     pnp_string = pnp[0].string
    # print type(pnp)
    # values = None
    # if len(relations) > 0:
    #     tDict = getRelationsFromDict(relations)
    #     for k in tDict.keys():
    #         values = (k, tDict[k].OBJ.lower(), tDict[k].VP.lower(), tDict[k].SBJ.lower())
    #         # MySqlHelper.insert(db_list, values, "insert into relation values(%s,%s,%s,%s,%s)")
    ners = get_all_entities_by_nltk(question)
    n1 = ''
    n2 = ''
    if len(ners) > 0:
        n1 = ners[0]
        if len(ners) > 1:
            n2 = ners[1]
        else:
            n2 = n1
    n1_syn = list()
    n2_syn = list()
    if n1 != '':
        n1_syn = get_synsets(n1)
    if n1 != n2:
        n2_syn = get_synsets(n2)
    else:
        n2_syn = n1_syn

    summary_text_list = list()
    main_art_sent_list = getSentencesFromPassageText(article)
    for sent in main_art_sent_list:
        if (n1 != '' and word_list_in_sentenceStr(n1_syn, sent)) or (
                n2 != '' and word_list_in_sentenceStr(n2_syn, sent)):
            if len(getAllNumbers(get_tagged_sentence(sent))) > 0:
                pnp = get_pnp(sent)
                if pnp is not None and len(pnp) >= 1:
                    summary_text_list.append(sent)
    return summary_text_list


def replace_verb_check_similarity(verb_to_replace, sent_string):
    ner_list = get_all_entities_by_nltk(sent_string)
    v_list = getAllVerbs(get_tagged_sentence(sent_string))
    if len(ner_list) <= 1 or len(v_list) <= 0:
        return -1
    else:
        n1 = ner_list[0]
        n2 = ner_list[1]
        raw_sents = get_all_sentences_list_from_web(n1 + " " + verb_to_replace + " " + n2)
        sents_with_n1 = list()
        sents_with_both = list()
        for s in raw_sents:
            if wordInSentStr(n1, s):
                sents_with_n1.append(s)
        for s in sents_with_n1:
            if wordInSentStr(n2, s):
                sents_with_both.append(s)
        n1_count = len(sents_with_n1)
        both_count = len(sents_with_both)
        if n1_count == 0:
            return 0
        else:
            return float(both_count) / n1_count


def str_list_to_string(str_list):
    if str_list is None or len(str_list) == 0:
        return ''
    else:
        whole_str = ''
        for s in str_list:
            whole_str += s + " "
        return whole_str


def str_list_to_lower_case(str_list):
    ret_list = list()
    for s in str_list:
        ret_list.append(s.lower())
    return ret_list


def sort_sentence_by_verb_hit(verbs_list, sentence_list):
    all_sent_dict = {}
    all_verb_str = str_list_to_string(verbs_list)
    for sent in sentence_list:
        print "compare synsets of verbs in sentence ", sent
        sent_verb_list = getAllVerbs(get_tagged_sentence(sent))
        hit_count = get_verb_list_hit(verbs_list, sent_verb_list)
        other_count = replace_verb_check_similarity(all_verb_str, sent)
        if hit_count == 0 and other_count <= 0:
            continue
        all_sent_dict[sent] = other_count
    temp_dict = sorted(all_sent_dict.iteritems(), key=lambda d: d[1], reverse=True)
    sentence_list = list()
    for t in temp_dict:
        sentence_list.append(t[0])
    return sentence_list


def summary_by_comparing_articles(article, other_article_list):
    summary_text_list = list()
    main_art_sent_list = getSentencesFromPassageText(article)
    total_sent_list = list()
    for art in other_article_list:
        other_art_sent_list = getSentencesFromPassageText(art)
        total_sent_list += other_art_sent_list
    threshhold = 2
    for main_sent in main_art_sent_list:
        if len(main_sent) <= 3:
            continue
        else:
            hit = 0
            ner_list = get_all_entities_by_nltk(main_sent)
            for ner in ner_list:
                for other_sent in total_sent_list:
                    if wordInSentStr(ner, other_sent):
                        hit += 1
                    if hit >= threshhold:
                        summary_text_list.append(main_sent)
                        break
                if hit >= threshhold:
                    break
    return summary_text_list


from pyh import *


def tuple_to_html_page(tuple_list, title='TestDoc', output_file='./testHtml.html'):
    ner_str = ''
    sent_list = list()
    for t in tuple_list:
        if t[1] == True and len(t[0]) < 30:
            ner_str = ner_str + " " + t[0]
        else:
            sent_list.append(t)

    page = PyH(title)
    page << h2('key words: ' + ner_str, c1='center')
    for sent_tuple in sent_list:
        if not sent_tuple[2]:
            page << (h3(sent_tuple[0]))
        else:
            page << (h2(sent_tuple[0], style='color:red'))
    page.printOut(output_file)


def summary_to_html(topic):
    tuple_list = topic_to_tuple_list(topic)
    tuple_to_html_page(tuple_list, topic)


def answer_by_summary(question_string):
    summary_to_html(question_string)
    return


def interrogative_filter(sent_list):
    # remove sentences with "?"
    question_symbol_list = ['when','how','what','which','?']
    temp_sent_list = sent_list[:]
    
    for sent in temp_sent_list:
        for question_symbol in question_symbol_list:
            if question_symbol in str(sent).lower():
                sent_list.remove(sent)
                break
    del temp_sent_list
    return sent_list


def filter_proper_noun(sent_str_list, noun_list): # an answer should contain other proper nouns,
    # if not, it means this one did not tell us anything useful
    ret_list = list()
    for s in sent_str_list:
        print 'sentence is ', s
        proper_list = getAllProperEntities(get_tagged_sentence(s))
        print 'and the proper nouns are ', proper_list
        noun_list_lower = str_list_to_lower_case(noun_list)
        for pn in proper_list:
            if pn.lower() not in noun_list_lower:
                ret_list.append(s)
                break
            else:
                continue
    return ret_list


def nuggets_finder(sub_sent_string):
    SCANNING_SBJ = 0
    SCANNING_OBJ = 1
    SCANNING_VP = 2
    VP = 'VP'
    NP = 'NP'
    OBJ = 'OBJ'
    SBJ = 'SBJ'
    scan_state = SCANNING_SBJ

    chunks = get_chunks_in_sentence(sub_sent_string)
    sub_relation_list = list()
    relation = list()
    tempSBJ = ''
    tempOBJ = ''
    tempVP = ''
    for i in range(0,len(chunks)):
        if scan_state == SCANNING_SBJ:
            #DO things
            #Change state
            if chunks[i].tag != VP:
                tempSBJ += " " + chunks[i].string
                #------
                #no state change
                continue
            else:
                relation.append((tempSBJ,SBJ))
                tempVP += " " + chunks[i].string
                #------
                scan_state = SCANNING_VP
                continue
        if scan_state == SCANNING_VP:
            if chunks[i].tag != NP:
                tempVP += " " + chunks[i].string
                continue
            else:
                relation.append((tempVP, VP))
                tempOBJ += " " + chunks[i].string
                #-------
                scan_state = SCANNING_OBJ
                continue
        if scan_state == SCANNING_OBJ:
            if chunks[i].tag != VP:
                tempOBJ += " " + chunks[i].string
                continue
            else:
                relation.append((tempOBJ,OBJ))
                sub_relation_list.append(relation)
                relation = list()
                tempSBJ = copy.deepcopy(tempOBJ)
                tempOBJ = ''
                tempVP = ''
                tempVP += " " + chunks[i].string
                relation.append((tempSBJ,SBJ))
                scan_state = SCANNING_VP
                continue
    if scan_state == SCANNING_OBJ:
        relation.append((tempOBJ,OBJ))
    if scan_state == SCANNING_SBJ:
        relation.append((tempSBJ,SBJ))
    if scan_state == SCANNING_VP:
        relation.append((tempVP,VP))
    if len(relation)>0:
        sub_relation_list.append(relation)
    return sub_relation_list


def sub_relation_finder(sub_sent_string):
    VP = 'VP'
    NP = 'NP'
    OBJ = 'OBJ'
    SBJ = 'SBJ'
    chunks = get_chunks_in_sentence(sub_sent_string)
    sub_relation_list = list()
    relation = list()
    tempSBJ = ''
    tempOBJ = ''
    tempVP = ''
    SEARCH_FOR_SBJ = -3
    SEARCH_FOR_VP = -2
    SEARCH_FOR_OBJ = -1
    search_state = SEARCH_FOR_OBJ
    for i in range(len(chunks)-1, -1, -1):
        if chunks[i].tag == VP:
            if search_state == SEARCH_FOR_OBJ:
                tempVP = chunks[i].string + " " + tempVP
                relation.append((tempVP,VP))
                search_state = SEARCH_FOR_SBJ
                continue
            if search_state == SEARCH_FOR_VP:
                tempVP = chunks[i].string + " " + tempVP
                continue
            if search_state == SEARCH_FOR_SBJ:
                relation.append((tempSBJ,SBJ))
                sub_relation_list.append(relation)
                relation = list()
                tempSBJ = ''
                tempOBJ = ''
                tempVP = ''
                tempVP = chunks[i].string + " " + tempVP
                search_state = SEARCH_FOR_OBJ
                continue
        if chunks[i].tag != VP:
            if search_state == SEARCH_FOR_SBJ:
                tempSBJ = chunks[i].string +  " " + tempSBJ
                continue
            if search_state == SEARCH_FOR_OBJ:
                tempOBJ = chunks[i].string + " " + tempOBJ
                continue
            if search_state == SEARCH_FOR_VP:
                relation.append((tempVP, VP))
                search_state = SEARCH_FOR_SBJ
                tempSBJ = chunks[i].string +  " " + tempSBJ
                continue
        if i == 0:
            if search_state == SEARCH_FOR_OBJ:
                relation.append((tempOBJ,OBJ))
            if search_state == SEARCH_FOR_SBJ:
                relation.append((tempSBJ,SBJ))
            if search_state == SEARCH_FOR_VP:
                relation.append((tempVP,VP))
            if len(relation)>0:
                sub_relation_list.append(relation)
    return sub_relation_list


def nugget_builder(tuple_list):
    base_sbj = ''
    base_vp = ''
    base_obj = ''
    for n in tuple_list:
        if n[1] == 'SBJ':
            base_sbj = n[0]
        elif n[1] == 'OBJ':
            base_obj = n[0]
        elif n[1] == 'VP':
            base_vp = n[0]
    return (base_sbj, base_vp, base_obj)

def get_last_word(str_chunk):
    count =  len(str_chunk)
    if count>0:
        str_list = str(str_chunk).split()
        size = len(str_list)
        return str_list[size-1]
    else:
        return str_chunk

def compare_sentence_by_nugget_with_all_words(sent1, sent2, embeddings, sim_dict):
    nuggets1_list = nuggets_finder(sent1)
    words_list = sent2.split()
    score_list = list()
    for nug in nuggets1_list:
        base_sbj = ''
        base_vp = ''
        base_obj = ''
        t = nugget_builder(nug)
        base_sbj = str(t[0])
        base_vp = str(t[1])
        base_obj = str(t[2])
        base_sbj_head = get_last_word(base_sbj)
        base_obj_head = get_last_word(base_obj)
        base_vp_head = get_last_word(base_vp)
        # print 'the type of base_sbj_head is ', type(base_sbj_head)
        # print base_sbj_head
        h_score = 0
        for word in words_list:
            s = similarityByEmbedding(base_sbj_head, word, embeddings, sim_dict)
            v = similarityByEmbedding(base_vp_head, word, embeddings, sim_dict)
            # o = Levenshtein.ratio(base_obj, obj)
            o = similarityByEmbedding(base_obj_head, word, embeddings, sim_dict)
            score = float(0.4*s + 0.4*v + 0.2*o)/3

            if h_score < score:
                h_score = score
        score_list.append(h_score)
    sum = 0
    for s in score_list:
        sum += s
    # avg = sum/len(score_list)
    avg = max(score_list)
    return avg

def compare_sentence_by_nuggets(sent1, sent2):
    nuggets1_list = nuggets_finder(sent1)
    nuggets2_list = nuggets_finder(sent2)
    score_list = list()
    for nug in nuggets1_list:
        base_sbj = ''
        base_vp = ''
        base_obj = ''
        t = nugget_builder(nug)
        base_sbj = str(t[0])
        base_vp = str(t[1])
        base_obj = str(t[2])
        base_sbj_head = get_last_word(base_sbj)
        base_obj_head = get_last_word(base_obj)
        base_vp_head = get_last_word(base_vp)
        print 'the type of base_sbj_head is ', type(base_sbj_head)
        print base_sbj_head
        h_score = 0
        for nug_2 in nuggets2_list:
            t2 = nugget_builder(nug_2)
            sbj = str(t2[0])
            vp = str(t2[1])
            obj = str(t2[2])
            sbj_head = get_last_word(sbj)
            obj_head = get_last_word(obj)
            vp_head = get_last_word(vp)
            print "base_sbj is ", base_sbj," sbj is ", sbj
            print "base_sbj type is ", type(base_sbj), " sbj type is ", type(sbj)
            if base_sbj == '' or sbj == '' or len(base_sbj)<1 or len(sbj)<1:
                s = 0
            else:
                # s = Levenshtein.ratio(base_sbj, sbj)
                s = similarityByEmbedding(base_sbj_head,sbj_head)
            if base_vp == '' or vp == '' or  len(base_vp) <1 or len(vp) <1:
                v = 0
            else:
                # v = Levenshtein.ratio(base_vp, vp)
                v = similarityByEmbedding(base_vp_head, vp_head)
            if base_obj == '' or obj == '' or len(base_obj) <1 or len(obj) <1:
                o = 0
            else:
                # o = Levenshtein.ratio(base_obj, obj)
                o = similarityByEmbedding(base_obj_head, obj_head)
            if s == 0:
                s1 = 0
            else:
                s1 = similarityByEmbedding(base_sbj_head, sbj_head)
            if o == 0:
                o1 = 0
            else:
                o1 = similarityByEmbedding(base_obj_head, obj_head)
            score = float(0.5*s + v + 0.5*o + 0.5*s1 + 0.5*o1)/3

            if h_score < score:
                h_score = score
        score_list.append(h_score)
    sum = 0
    for s in score_list:
        sum += s
    avg = sum/len(score_list)
    return avg


def is_sentence_complete(sent):
    nuggets = nuggets_finder(sent)
    if len(nuggets)>1:
        return True
    else:
        nugget = nuggets[0]
        t = nugget_builder(nugget)
        sbj = str(t[0])
        vp = str(t[1])
        obj = str(t[2])
        if sbj == '' or vp == '' or obj == '':
            # print 'Nugget is not complete, return false'
            return False
        else:
            return True

def answer_by_a_few_sentence(question_string, question_type, embeddings,sim_dict):
    # This is only suitable for "what is" and "who is " questions
    # first search the certain question by "silly" word-by-word strategy
    # that is find a sentence hit all the name-entities and main-verbs in the question
    # if the first "silly" strategy does not work, get a list of synsets of named entities in the question
    # and the origin main verbs in the question
    # then use the list to search in the corpus
    # if the candidate sentences still does not contain the origin main verbs
    # try the third strategy:
    # in the candidate sentences, check if the verbs in candidate sentences are of the same
    # meaning with the origin main verbs
    print "answer_by_a_few_sentence called"
    ner_tuple = get_synsets_lists_from_sentence(question_string)
    sent_str_list = getRelatedSentencesListFromWeb(question_string)
    # sent_str_list = questionMod(question_string, DEFAULT)
    temp_str_list = list()
    for t in sent_str_list:
        temp_str_list.append(t)
    # sent_str_list = secondSentenceSplitor(temp_str_list)
    sent_str_list = interrogative_filter(temp_str_list)
    # ner_tuple = get_synsets_lists_from_sentence(question_string)
    n1_list = ner_tuple[0]
    n2_list = ner_tuple[1]
    n1_list = str_list_to_lower_case(n1_list)
    n2_list = str_list_to_lower_case(n2_list)
    # verbs = str_list_to_lower_case(getAllVerbs(get_tagged_sentence(question_string)))
    candidate_noun_sentence_list = list()
    # for sent in sent_str_list:
    #     if word_list_in_sentenceStr(n1_list, sent.lower()) and\
    #         word_list_in_sentenceStr(n2_list, sent.lower()):
    #         candidate_noun_sentence_list.append(sent)
    # if len(candidate_noun_sentence_list) <=0:
    #     candidate_noun_sentence_list = sent_str_list
    candidate_noun_sentence_list = sent_str_list
    print 'candidate_noun_sentence_list are ', candidate_noun_sentence_list
    candidate_verb_sentence_list = list()
    candidate_only_noun_sentence_list = list() # sentences only hit noun but failed with verb match
    # for sent in candidate_noun_sentence_list:
    #     if all_word_list_in_sentenceStr(verbs, sent.lower()):
    #         candidate_verb_sentence_list.append(sent)
    #     else:
    #         candidate_only_noun_sentence_list.append(sent)

    # sentences_with_different_verb = sort_sentence_by_verb_hit(verbs, candidate_only_noun_sentence_list)
    # if len(candidate_verb_sentence_list)==0:
    #     noun_verb_hit_sentences_list = sort_sentence_by_verb_hit(verbs, candidate_only_noun_sentence_list)
    # else:
    #     noun_verb_hit_sentences_list = candidate_verb_sentence_list
    # total_txt = ''
    # for s in sent_str_list:
    #     total_txt = total_txt + ' ' + s
    # total_txt = total_txt.strip()
    # simVal_list = similarity(noun_verb_hit_sentences_list, total_txt)
    # score_list = list()
    # for i in range(0,len(noun_verb_hit_sentences_list)):
    #     score_list.append((noun_verb_hit_sentences_list[i],simVal_list[i]))
    # print score_list
    # print 'The following only hit the nouns ', noun_verb_hit_sentences_list

    #further filters which should be implemented in each kind of question filter
    # if question_type == WHO:
    #     print "In branch who ..."
    #     noun_verb_hit_sentences_list = filter_proper_noun((noun_verb_hit_sentences_list), n1_list)
    #     sentences_with_different_verb = filter_proper_noun((sentences_with_different_verb), n1_list)
    sent_eval = list()
    similar_level = 0.8
    # if len(candidate_verb_sentence_list)>0:
    #     scored_list = candidate_verb_sentence_list
    # else:
    #     scored_list = candidate_only_noun_sentence_list
    scored_list = candidate_noun_sentence_list
    for sent in scored_list:

        if (Levenshtein.ratio(str(question_string.lower()), str(sent.lower()))>similar_level):
            continue
        sc = (compare_sentence_by_nugget_with_all_words(question_string, sent, embeddings, sim_dict)*0.9\
            + compare_sentence_by_nugget_with_all_words(sent, question_string, embeddings, sim_dict)*0.1)
        sent_eval.append((sent, sc))
    print "Now will do the sorting length is ", len(sent_eval)
    # sorted_l=sorted(sent_eval,key=lambda t:t[1],reverse=True)
    sorted_l = sent_eval
    # complete_l = []
    # for s in sorted_l:
    #     sent = s[0]
    #     nuggets = nuggets_finder(sent)
    #     if len(nuggets)>1:
    #         complete_l.append(s)
    #     else:
    #         nugget = nuggets[0]
    #         t = nugget_builder(nugget)
    #         sbj = str(t[0])
    #         vp = str(t[1])
    #         obj = str(t[2])
    #         if sbj == '' or vp == '' or obj == '':
    #
    #             continue
    #         else:
    #             complete_l.append(s)
    # total_txt = ''
    # only_text_list = []
    # for s in complete_l:
    #     total_txt = total_txt + ' ' + s[0]
    #     only_text_list.append(s[0])
    # total_txt = total_txt.strip()
    # simVal_list = similarity(only_text_list, total_txt)
    # last_list = []
    # for n in range(0,len(only_text_list)):
    #     last_list.append((only_text_list[n],simVal_list[n]))
    # last_list = sorted(last_list,key=lambda t:t[1],reverse=True)
    return sorted_l


def question_classifier(input_string):
    return HOW


QUESTION = 0
FUNCTION = 1
CHAT = 2


def function_classifier(input_string):
    return QUESTION


def raw_input_process(input_string):
    function_type = function_classifier(input_string)
    if function_type == QUESTION:
        input_question_process(input_string)
    elif function_type == FUNCTION:
        FunctionMod(input_string)
    elif function_type == CHAT:
        conversation_with_sent_structure_ansys(input_string)


def input_question_process(input_string):
    question_type = question_classifier(input_string)
    if question_type == HOW:
        answer_by_a_few_sentence(input_string, question_type)
    elif question_type == WHAT:
        answer_by_a_few_sentence(input_string, question_type)
    elif question_type == WHEN:
        answer_by_a_few_sentence(input_string, question_type)
    elif question_type == WHERE:
        answer_by_a_few_sentence(input_string, question_type)
    elif question_type == WHO:
        answer_by_a_few_sentence(input_string, question_type)
    elif question_type == WHY:
        answer_by_summary(input_string)
    elif question_type == HOWTO:
        answer_by_summary(input_string)


def getDistance(v1_index,v2_index):
    import math
    if v1_index is None or v2_index is None:
        return -10000000
    if len(v1_index.shape)!=len(v2_index.shape):
        return -10000000
    else:
        # print " Indexs are ", (v1_index.shape), " ", (v2_index.shape)

        sum = 0
        for i in range(len(v1_index)-1):
            v1_i = v1_index[i]
            v2_i = v2_index[i]
            sum += (v1_i-v2_i)*(v1_i-v2_i)
            # sum += (v1[i]-v2[i])*(v1[i]-v2[i])
        dist = math.sqrt(sum)
        return dist

def Distance2Similarity(value):
    if value <0:
        return 0
    elif value == 0:
        return 1
    else:
        # print 'Distance2Similarity is ',(value/(1+value))
        return (value/(1+value))

def similarityByEmbedding(w1,w2, embeddings, sim_dict):
    # global embeddings
    v1index = sim_dict.get(w1.lower())
    v2index = sim_dict.get(w2.lower())
    # print "v1index is ", v1index
    # print "v2index is ", v2index
    embeds1 = embeddings[v1index,:]
    embeds2 = embeddings[v2index,:]
    dis = getDistance(embeds1, embeds2)
    # print 'distance is ', dis
    return Distance2Similarity(dis)

def Sentiment(article_str):
    from pattern.en import sentiment
    sent_list = getSentencesFromPassageText(article_str)
    scoreList = list()
    for sent in sent_list:
        polar = sentiment(str(sent))
        scoreList.append((sent, polar[0]))
    return scoreList


def answerQuestion(question):
    # question = "how big is an atom"
    art_list = get_articles_withURKL_from_websearch_query(question)
    str_word = ''
    print "finish getting all the articles"
    for art in art_list:
        str_word += art[0]
        # out = get_summary_sentences_by_summarizer_voting(art[0])
        # print 'Results are '
        # for sent in out :
        #     print sent
        #     print "\r\n"
    str_word = str_word.split()
    word_list = list()
    for w in str_word:
        post_w = str(w).strip().lower()
        word_list.append(post_w)
    global embeddings
    print "Will now call full_cycle()"
    embeddings, sim_dict = full_cycle(word_list)
    print "full_cycle() end"
    ansList = answer_by_a_few_sentence(question, WHO)
    ansList = list(set(ansList))
    # ansList = sorted(ansList, key=lambda t: (-t[1], t[0]))
    ner_list = list()
    print 'The last anwsers are: '
    for ans in ansList:
        print ans, type(ans)
        ner_list = ner_list + get_all_entities_by_nltk(ans[0])
        print "\r\n"
    ner_list = list(set(ner_list))
    print "the related nouns are "
    for ner in ner_list:
        print ner, "\r\n"

def checkPatternByRe(search_str, pattern_str):
    p = re.compile(pattern_str)
    m = p.search(search_str)
    # print m.group()
    if m:
        return True
    else:
        return False
def getRulesByApriori(RawFilePath, stopWordsList):
    # sentences = read_file('data.text')
    # assrules = associationRule(sentences)
    # assrules.apriori()
    # assrules.generateRules()
    rules = self_learn_by_apriori(RawFilePath, '', stopWordsList)
    ruleSetList = list()
    for rule in rules:
        rule_set = set(list(rule[0][0]) +list(rule[0][1]))
        ruleSetList.append(rule_set)
    print '======rule sets===='

    # ruleSetList = set(ruleSetList)
    ruleSetList = removeSameSet(ruleSetList)
    for r in ruleSetList:
        print r,'\r\n'
    return ruleSetList
    # print (ruleSetList[0] == ruleSetList[1])


def removeSameSet(setList):
    for i in range(len(setList)):
        for j in range(len(setList)):
            if (i<len(setList)) and (j<len(setList))and (i != j):
                print "i = " ,i , "j = " ,j
                if if_rules_repeated(setList[i],setList[j]):
                    setList.pop(j)
    return setList

def scoreSentenceByFreqRules(ruleList,sent):
    score = 0
    for rule in ruleList:
        percent = hit_percent_in_sentenceStr(rule, sent)
        # if all_word_list_in_sentenceStr(rule, sent):
        score = percent + score
    return score

def noun_related_score_to_sentences(noun_list, sent_list, embeddings, sim_dict):
#     sort nouns by how close to the iven sentences
    result = list()
    # length = len(sent_list)
    for noun in noun_list:
        score = 0
        for sent in sent_list:
            print "sent[0] is " , sent[0]
            s = compare_sentence_by_nugget_with_all_words(noun, sent[0], embeddings, sim_dict)
            score += s
        result.append((noun, score))
    result = sorted(result, key=lambda t: (-t[1], t[0]))
    return result

def sentences_has_connection(sent1, sent2):
    print "In sentences_has_connection"
    threshold = 0.8
    limitLen = 3
    nuglist1 = nuggets_finder(sent1)
    nuglist2 = nuggets_finder(sent2)
    for nug1 in nuglist1:
        (sbj1, vp, obj1) = nugget_builder(nug1)
        for nug2 in nuglist2:
            (sbj2, vp, obj2) = nugget_builder(nug2)
            sbj1 = str(sbj1)
            sbj2 = str(sbj2)
            obj1 = str(obj1)
            obj2 = str(obj2)
            if wordInSentStr("his",sbj2.lower()) or wordInSentStr("her",sbj2.lower()) or wordInSentStr("these",sbj2.lower()) \
                   or wordInSentStr("it", sbj2.lower()) or wordInSentStr("this", sbj2.lower()) or wordInSentStr("that", sbj2.lower()) :
                print ("pronoun found")
                return True
            # sbj1 = str(sbj1)
            # sbj1 = str(sbj1)
            if (len(sbj1) < limitLen) or (len(sbj2) < limitLen) \
                    or (len(obj1) < limitLen) or (len (obj2) < limitLen):
                continue
            simScore1 = Levenshtein.ratio(sbj1, sbj2)
            if (simScore1 > threshold):
                print sbj1 + " simi to " + sbj2
            simScore2 = Levenshtein.ratio(sbj1, obj2)
            if (simScore2 > threshold):
                print sbj1 + " simi to " + obj2
            simScore3 = Levenshtein.ratio(obj1, sbj2)
            if (simScore3 > threshold):
                print obj1 + " simi to " + sbj2
            simScore4 = Levenshtein.ratio(obj1, obj2)
            if (simScore4 > threshold):
                print obj1 + " simi to " + obj2
            if (simScore1> threshold) or (simScore2> threshold)\
                    or (simScore3> threshold) or (simScore4> threshold):
                return True
    return False
def summary_by_wordEmbedding():
    filehandler = open('./text/tosummary/text', 'r')
    # what does ... mean
    question_sentence_part_start = 'what is '
    question_sentence_part_end = ' '

    SHORT_SENT = 3
    rawtext = filehandler.read()
    sent_list = getSentencesFromPassageText(rawtext)
    # sent_list = secondSentenceSplitor(sent_list)
    print " test sentences conectivity:"
    for i in range(len(sent_list)-1):
        print (" " + str((sent_list[i])) + " --and-- " + str((sent_list[i+1])) + ":")
        print sentences_has_connection(str(sent_list[i]), str(sent_list[i+1]))
    keysent_NERs = summary_article(rawtext)
    writeSummaries = file('./text/summaries.txt', 'a+')
    keysents = keysent_NERs[0]
    nerList = keysent_NERs[1]

    for keysent in keysents:
        nuggets = nuggets_finder(keysent[0])
        print("original: " + keysent[0])
        for nug in nuggets:
            (sbj,vp,obj) = nugget_builder(nug)
            (keyword_explation, e, d) = answer_by_a_few_sentences_by_embedding("why and how " + sbj + " " + vp + " " + obj, 3)
            if keyword_explation is None:
                continue
            for exp in keyword_explation:
                writeSummaries.write("explination for " + keysent[0] + " is:-- " + exp[0])
                print "explination for " + keysent[0] + " is:-- " + exp[0]
        writeSummaries.write(str(keysent))
        writeSummaries.write('\r\n')
    NERs = get_all_entities_by_nltk(keysent[0])

    # writeSummaries.write('-------------key words------\r\n')
    # for ner in nerList:
    #     writeSummaries.write(ner + ': \r\n')
    #     keyword_explation = answer_by_a_few_sentences_by_embedding(ner + " is what",1)
    #     if keyword_explation is None:
    #         continue
    #     writeSummaries.write(str(keyword_explation[0]) + '\r\n')
    # writeSummaries.write('\r\n===================\r\n')
    writeSummaries.close()
    # questionList = filehandler.readlines()
    questionList = keysent_NERs[1]
    ner_list = list()

    for q in questionList:

        question = keysents[0][0]
        print 'will search question ', question
        art_list = get_articles_withURKL_from_websearch_query(question)

        str_word = ''
        print "finish getting all the articles"
        for art in art_list:
            str_word += art[0]

        str_word = str_word.split()
        word_list = list()
        for w in str_word:
            # if len(str(w).strip())<3:
            #     continue
            post_w = str(w).strip().lower()
            word_list.append(post_w)

            # Write to the bag of words file
            # FileUtils.WriteToFile('bag_of_words.txt', word_str_buff)
            # Read words out from bag of words
            # str_word = FileUtils.OpenFileUnicode('bag_of_words.txt')

            # word_list = list()
            # for w in str_word:
            # if len(str(w).strip())<3:
            # continue
            # post_w = str(w).strip().lower()
            # word_list.append(post_w)
            # word_str_buff = word_str_buff + " " + post_w
        # global embeddings
        embeddings = None
        sim_dict = {}
        print "Will now call full_cycle()"
        try:
            embeddings, sim_dict = full_cycle(word_list)
        except:
            print 'failed to get embeddings'
            return
        print "full_cycle() end"
        ansList = answer_by_a_few_sentence(question, WHO, embeddings, sim_dict)
        # extract freq words combinations
        common_combination_rules = self_learn_by_fp_growth('./text/rawtext', '.', ENGLISH_STOP_WORDS)
        # rules = getRulesByApriori('data.txt', ENGLISH_STOP_WORDS)
        ansList = list(set(ansList))
        ansList = sorted(ansList, key=lambda t: (-t[1], t[0]))
        ner_list = list()
        selected_sentences_string = ""
        print 'The last answers are: '
        for ans in ansList:
            print ans, type(ans)
            ner_list = ner_list + get_all_entities_by_nltk(ans[0])
            selected_sentences_string = selected_sentences_string + ans[0] + "."
            print "\r\n"

        # get summary sentences from the last selected sentences
        summarized_sentences = get_summary_sentences_by_summarizer_voting(selected_sentences_string)
        print " summarized answers are: "
        for sent in summarized_sentences:
            print sent, "\r\n"
            print get_tagged_sentence(sent[0])
            print "====================="

        key_noun_list = noun_related_score_to_sentences(nerList, summarized_sentences, embeddings, sim_dict)
        print("key_noun_list scored by relation")
        print key_noun_list
        # explatnations_for_key_sents = list()
        writeSummaries = file('./text/summaries.txt', 'a+')
        for sent in summarized_sentences:
            # writeSummaries.write("explination for " + sent[0] + ': \r\n')
            nuggets = nuggets_finder(sent[0])
            nugget_str = ''
            for nug in nuggets:
                (sbj, vp, obj) = nugget_builder(nug)
            (keyword_explation, e, d) = answer_by_a_few_sentences_by_embedding("why and how " + sbj + " " + vp + " " + obj,3)
            if keyword_explation is None:
                continue
            for exp in keyword_explation:
                writeSummaries.write("explination for " + sent[0] + " is:-- " + exp[0])
                print "explination for " + sent[0] + " is:-- " + exp[0]
        writeSummaries.write('\r\n===================\r\n')
        writeSummaries.close()
        # Score the last extracted backup sentences by its presence in summarized_sentences
        Voting_summarier_number = 4
        word_black_list = ['do', 'does', 'why', 'when', 'how', 'what', 'which', 'who', 'where', '?', 'html',
                           'ocols and Formats Working Group (PFWG'.lower() \
            , 'Semantic Web Deployment Working Group'.lower(), 'Microsoft'.lower(), 'your browser',
                           'JavaScript'.lower()]
        backupAnswerAfterScoreBySummary = []
        # ansList =getSentencesFromPassageText()
        # envaluate the article
        ansList = getSentencesFromPassageText(rawtext)
        ansList = secondSentenceSplitor(ansList)
        for str_score_pair in ansList:
            ans_str = str_score_pair
            if (not is_sentence_complete(ans_str)) or wordListInString(word_black_list, ans_str.lower()):
                continue
            mean_score = compare_sentence_by_nugget_with_all_words(question, ans_str, embeddings, sim_dict)
            summaryScore = 0.0
            # length factor: we tend to extract longer sentences, they describes more clearly
            # sent_length = len(ans_str)
            # lengthFactor = sent_length/float(1+sent_length)
            tag_str = tagString_of_sentence(ans_str)
            # print '-----------', tag_str
            # check if sentence meets question pattern
            # questionPatternScore = float(0)
            # if checkPatternByRe(tag_str, question_pattern):
            #     questionPatternScore = 1
            # else:
            #     questionPatternScore = 0
            common_combination_score = scoreSentenceByFreqRules(common_combination_rules, ans_str) \
                                       / (len(common_combination_rules) + 1)
            # print "Common_combination_score is ", common_combination_score
            # print 'summaryScore is ', summaryScore
            # print 'mean_score is ', mean_score
            mean_score = 0.020 * summaryScore + \
                         0.88 * mean_score + \
                         0.1 * common_combination_score
            # 0.1 * questionPatternScore
            # 0.01 * lengthFactor
            # + 0.35 * compare_sentence_by_nuggets(question, ans_str)
            # mean_score = mean_score/2
            backupAnswerAfterScoreBySummary.append((ans_str, mean_score))
        backupAnswerAfterScoreBySummary = sorted(backupAnswerAfterScoreBySummary, key=lambda t: (-t[1], t[0]))
        TopScoredSentences = list()
        sent_num = len(backupAnswerAfterScoreBySummary)
        percent = 0.05
        for i in range(sent_num):
            if i<= sent_num*percent:
                TopScoredSentences.append(backupAnswerAfterScoreBySummary[i])
            else:
                break
        print 'passage total num: ', sent_num
        print 'summary num: ', len(TopScoredSentences)
        backupAnswerAfterScoreBySummary = TopScoredSentences
        print "For Question : ", question
        print "Scored by both word relation "
        writeAnswers = file('./text/summaries.txt', 'a+')
        writeAnswers.write("\r\n")
        writeAnswers.write(question + "?")
        for sent_pair in backupAnswerAfterScoreBySummary:
            print sent_pair, "\r\n"
            print "+++++++++++++++++++++++++++++"
            writeAnswers.write(sent_pair[0])
            writeAnswers.write('\r\n')
        writeAnswers.close()

def answer_by_a_few_sentences_by_embedding(question_str, ans_num=1):
    question = question_str

    print 'will search question in function answer_by_a_few_sentences_by_embedding ', question
    art_list = get_articles_withURKL_from_websearch_query(question)

    str_word = ''
    print "finish getting all the articles"
    for art in art_list:
        str_word += art[0]

    str_word = str_word.split()
    word_list = list()
    for w in str_word:
        post_w = str(w).strip().lower()
        word_list.append(post_w)

    # embeddings = None
    # sim_dict = {}
    print "Will now call full_cycle()"
    try:
        embeddings, sim_dict = full_cycle(word_list)
    except:
        return None
    print "full_cycle() end"
    ansList = answer_by_a_few_sentence(question, WHO, embeddings, sim_dict)
    # extract freq words combinations
    common_combination_rules = self_learn_by_fp_growth('./text/rawtext', '.', ENGLISH_STOP_WORDS)

    ansList = list(set(ansList))

    ner_list = list()
    selected_sentences_string = ""
    print 'The last answers are: '
    for ans in ansList:
        print ans, type(ans)
        # ner_list = ner_list + get_all_entities_by_nltk(ans[0])
        selected_sentences_string = selected_sentences_string + ans[0] + "."
        print "\r\n"

    summarized_sentences = get_summary_sentences_by_summarizer_voting(selected_sentences_string)


    Voting_summarier_number = 4
    word_black_list = ['do', 'does', 'why', 'when', 'how', 'what', 'which', 'who', 'where', '?', 'html',
                       'ocols and Formats Working Group (PFWG'.lower() \
        , 'Semantic Web Deployment Working Group'.lower(), 'Microsoft'.lower(), 'your browser',
                       'JavaScript'.lower()]
    backupAnswerAfterScoreBySummary = []
    for str_score_pair in ansList:
        ans_str = str_score_pair[0]
        if (not is_sentence_complete(ans_str)) or wordListInString(word_black_list, ans_str.lower()):
            continue
        mean_score = str_score_pair[1]
        summaryScore = 0.0
        for summaryStr_score_pair in summarized_sentences:
            if str_score_pair[0] in summaryStr_score_pair[0]:
                summaryScore = summaryStr_score_pair[1] / float(Voting_summarier_number)
                break

        common_combination_score = scoreSentenceByFreqRules(common_combination_rules, ans_str) \
                                   / (len(common_combination_rules) + 1)

        mean_score = 0.020 * summaryScore + \
                     0.88 * mean_score + \
                     0.1 * common_combination_score

        backupAnswerAfterScoreBySummary.append((ans_str, mean_score))
    backupAnswerAfterScoreBySummary = sorted(backupAnswerAfterScoreBySummary, key=lambda t: (-t[1], t[0]))
    print "For Question : ", question
    print "Scored by both word relation and summary answers are: "

    length = len(backupAnswerAfterScoreBySummary)
    ret = None
    if ans_num>= length:
        ret = backupAnswerAfterScoreBySummary
    else:
        retList = list()
        i = 0
        for sent_pair in backupAnswerAfterScoreBySummary:
            print sent_pair, "\r\n"
            retList.append(sent_pair)
            i = i + 1
            if i >=ans_num:
                break
            print "+++++++++++++++++++++++++++++"
        ret = retList
    return (ret, embeddings, sim_dict)

def answer_by_a_few_sentences_by_embedding_with_context(question_str, ans_num=1):
    question = question_str

    print 'will search question in function answer_by_a_few_sentences_by_embedding ', question
    art_list = get_articles_withURKL_from_websearch_query(question)
    print ("articles are ")
    for art in art_list:
        print art[0]
    print("article ends")
#     art is make of two parts: one is article string, the other is its url
    (ansList,embed,dict) = answer_by_a_few_sentences_by_embedding(question_str, ans_num)
    reslist = list()
    for ans in ansList:
        findFlag = False
        for art in art_list:
            if ans[0] in art[0]:
                print (" In answer with embedding: sentence is " + str(ans[0]) + " context is " + str(art[0]))
                reslist.append((ans[0],ans[1],art[0]))
                findFlag = True
                break
        if findFlag == False:
            reslist.append((ans[0],ans[1],""))
    return (reslist, embed,dict)
def get_paragraph_from_article(article):
    return None

class question_option_pair:
    def __init__(self,question, option_tuple):
        self.question_str = question
        self.options = option_tuple

class readingWithProblems:
    def __init__(self, text, question_option_list):
        self.textStr = text
        self.question_option_pair_list = question_option_list

def read_in_one_comprehension(filePath):
    TEXT = 0
    QUESTION = 1
    OPTION = 2
    state = TEXT
    f = open(filePath, 'r')
    strList = f.readlines()
    text = list()
    question_option_list = list()
    length = len(strList)
    for i in range(0,length-1):
        q_o = question_option_pair("",None)
        question = ""
        if re.match("[1-9]\d*\.",strList[i].strip()[0:2]) is None and ("A)" in strList[i+1]):
            state = QUESTION
            question = strList[i]
            A = strList[i+1]
            B = strList[i+2]
            C = strList[i+3]
            D = strList[i+4]
            option = (A,B,C,D)
            q_o.question_str = question
            q_o.options = option
            question_option_list.append(q_o)
        else:
            if state == TEXT:
                text.append(strList[i])
    ret = readingWithProblems(text, question_option_list)
    return ret

def get_connectied_sentences(sentence, context):
    print "get_connectied_sentences"
    print "sentence is ", sentence
    print "context is ", context
    resList = list()
    sentence_list = getSentencesFromPassageText(context)
    index = -1
    length = len(sentence_list)

    for i in range(0,length):
        if sentence in sentence_list[i]:
            index = i
            break
    if length==1 or index == -1:
        resList.append(sentence)
        return resList
    if index == 0 and index+1<length:
        resList.append(sentence_list[index])
        if sentences_has_connection(sentence_list[index], sentence_list[index + 1]):

            resList.append(sentence_list[index + 1])
    else:
        print ("get_connectied_sentences: index is " + str(index )+ " length is " + str(length))
        if sentences_has_connection(sentence_list[index-1], sentence_list[index]):
            resList.append(sentence_list[index-1])
        resList.append(sentence_list[index])
        if index+1<length:
            if sentences_has_connection(sentence_list[index], sentence_list[index + 1]):
                resList.append(sentence_list[index + 1])
    return resList

def answer_by_embedding_with_complete_sentences(question_str):
    (ansList, embed, dict) = answer_by_a_few_sentences_by_embedding_with_context(question_str, 5)
    topAnsText = ansList[0][2]
    print "topAnsText", topAnsText

    keySent_NerList = summary_article(topAnsText)
    keySentList = keySent_NerList[0]
    summarized_sentences = get_summary_sentences_by_summarizer_voting(topAnsText)

    print keySentList
    nerList = keySent_NerList[1]
    print nerList
    sortedNerList = noun_related_score_to_sentences(nerList, summarized_sentences, embed, dict)
    print "Ners: ", sortedNerList
    print ("original answers:")
    for ans in ansList:
        print ans[0]
    print "answers are :"
    for ans_pair in ansList:
        print ans_pair[0]
        connecntList = get_connectied_sentences(ans_pair[0], ans_pair[2])
        print "comlete answer is"
        print "".join(connecntList)

def get_wordembedding_simdict(text2search):
    # question = "how big is an atom"
    art_list = get_articles_withURKL_from_websearch_query(text2search)
    str_word = ''
    print "finish getting all the articles"
    for art in art_list:
        str_word += art[0]
        # out = get_summary_sentences_by_summarizer_voting(art[0])
        # print 'Results are '
        # for sent in out :
        #     print sent
        #     print "\r\n"
    str_word = str_word.split()
    word_list = list()
    for w in str_word:
        post_w = str(w).strip().lower()
        word_list.append(post_w)
    global embeddings
    print "Will now call full_cycle()"
    embeddings, sim_dict = full_cycle(word_list)
    return (embeddings, sim_dict)

def do_one_reading_comprehension_by_embedding(article_with_problems):
    textlist = article_with_problems.textStr
    full_passage = ""
    for sent in textlist:
        full_passage += sent
    sentences = getSentencesFromPassageText(full_passage)
    text2search = full_passage[0:250]
    (embedding, dict) = get_wordembedding_simdict(text2search)
    q_list = article_with_problems.question_option_pair_list
    for q in q_list:
        question = list()
        question.append((q.question_str,""))
        # sentences = getSentencesFromPassageText(full_passage)
        sentence_sorted_list = noun_related_score_to_sentences(sentences, question, embeddings, dict)
        for sent in sentence_sorted_list:
            print sent
        # Then sort the sentences from the text by similarity to the question
        # pick up the most related sentence
        sentences_can_answer = sentence_sorted_list[0:4]
        options = [q.options[0],
                   q.options[1],
                   q.options[2],
                   q.options[3]]
        sentence_sorted_list = noun_related_score_to_sentences(options, sentences_can_answer, embeddings, dict)
        for sent in sentence_sorted_list:
            print sent
        print "question ends"

question_countor = 0
from word2vec_basic import full_cycle
if __name__ == "__main__":

    # summary_by_wordEmbedding()
    art_with_problems = read_in_one_comprehension("./text/tosummary/text")
    do_one_reading_comprehension_by_embedding(art_with_problems)
    # try to answer question with given text
    # first search the given text from the web to get the embedding

    # question = list()
    # question.append(("The significance of Brocklehurst’s research is that ",""))
    # filehandler = open('./text/tosummary/text', 'r')
    # SHORT_SENT = 3
    # full_passage = filehandler.read()
    # sentences = getSentencesFromPassageText(full_passage)
    # text2search = full_passage[0:250]
    # (embedding, dict) = get_wordembedding_simdict(text2search)
    # sentences = getSentencesFromPassageText(full_passage)
    #
    # sentence_sorted_list = noun_related_score_to_sentences(sentences, question,embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # # Then sort the sentences from the text by similarity to the question
    # # pick up the most related sentence
    # sentences_can_answer = sentence_sorted_list[0:4]
    # options = [ "it suggested a way to keep some foods fresh without preservatives",
    #             "it discovered tiny globules in both cream and butter",
    #             "it revealed the secret of how bacteria multiply in cream and butter",
    #             "it found that cream and butter share the same chemical composition"]
    # sentence_sorted_list = noun_related_score_to_sentences(options, sentences_can_answer, embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # print "question ends"
    # # //////////////////////////
    # question = list()
    # question.append(("According to the researchers, cream sours fast than butter because bacteria",""))
    # sentence_sorted_list = noun_related_score_to_sentences(sentences, question,embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # # Then sort the sentences from the text by similarity to the question
    # # pick up the most related sentence
    # sentences_can_answer = sentence_sorted_list[0:4]
    # options = [ "are more evenly distributed in cream",
    #             "multiply more easily in cream than in butter",
    #             "live on less fat in cream than in butter",
    #             "produce less waste in cream than in butter"]
    # sentence_sorted_list = noun_related_score_to_sentences(options, sentences_can_answer, embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # # //////////////////////////
    # print "question ends"
    # question = list()
    # question.append(("According to Brocklehurst, we can keep cream fresh by ", ""))
    # sentence_sorted_list = noun_related_score_to_sentences(sentences, question, embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # # Then sort the sentences from the text by similarity to the question
    # # pick up the most related sentence
    # sentences_can_answer = sentence_sorted_list[0:4]
    # options = ["removing its fat",
    #            "killing the bacteria",
    #            "reducing its water content",
    #            "altering its structure"]
    # sentence_sorted_list = noun_related_score_to_sentences(options, sentences_can_answer, embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # # //////////////////////////
    # question = list()
    # question.append(("The word “colonies” (Line 2, Para. 4) refers to",""))
    # sentence_sorted_list = noun_related_score_to_sentences(sentences, question,embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # # Then sort the sentences from the text by similarity to the question
    # # pick up the most related sentence
    # sentences_can_answer = sentence_sorted_list[0:4]
    # options = [ "tiny globules",
    #             "watery regions",
    #             "bacteria communities",
    #             "little compartments"]
    # sentence_sorted_list = noun_related_score_to_sentences(options, sentences_can_answer, embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # print "question ends"
    # # //////////////////////////
    # question = list()
    # question.append(("Commercial application of the research finding will be possible if salad cream can be made resistant to bacterial attack",""))
    # sentence_sorted_list = noun_related_score_to_sentences(sentences, question,embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # # Then sort the sentences from the text by similarity to the question
    # # pick up the most related sentence
    # sentences_can_answer = sentence_sorted_list[0:4]
    # options = [ "by varying its chemical composition",
    #             "by turning it into a solid lump",
    #             "while keeping its structure unchanged",
    #             "while retaining its liquid form"]
    # sentence_sorted_list = noun_related_score_to_sentences(options, sentences_can_answer, embeddings, dict)
    # for sent in sentence_sorted_list:
    #     print sent
    # print "question ends"
    print '----------summary ends-------'



#@ToDO
#Check a sentence by its center word of NPs
#if the center words match the center words in question,
#the answer should be scored high

#Make summary of an article:
        # Get the important sentences,
    # Get word definations in important sentences
    # Get sub-tiltes
    # Get word definations in sub-titles

# generate an article for a given subject
# extract paraghs with different subtitles(defination, structure,
# history, future, related concepts) of sentences which should be related to each other