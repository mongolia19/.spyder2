# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 13:53:23 2015

@author: mongolia19
"""

from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

# To Do:
# Just take lib Pattern for relation extraction
# !!!

#verb similarity find a sentences with n1 n2 and verb1 verb2
#search "n1 verb1 n2" and "n1 verb2 n2" ,we get two results
#r1 and r2
#if we find in r2 : a sentence contains n1, verb2 and n2, we
#thought verb1 and verb2 are of the same meaning


# print keyA
# print keyB
# print keyC
#

# print keyC.path_similarity(keyB)

# for w in wordBList:
#    print w.path_similarity(key)
#    print w
#    print type(w)
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import re
import nltk
import nltk.corpus
import PipLineTest
import FileUtils
import string
import htmlDownLoader
# from __future__ import absolute_import
# from __future__ import division, print_function, unicode_literals

# from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from textblob import TextBlob


# import FileUtils
from pattern.web import URL, plaintext
import urllib


def getAllLinksFromPage(url):
    try:

        htmlSource = urllib.urlopen(url).read(200000)
    except:
        htmlSource = ''
    # soup = BeautifulSoup.BeautifulSoup(htmlSource)
    head = (url, 'http')
    headlist = list()
    headlist.append(head)
    links = re.findall('"((http|ftp)s?://.*?)"', htmlSource)
    links = headlist + links
    return links


def html_to_plain_text(url_str):
    try:
        s = URL(url_str).download()
        s = plaintext(s)
        s = s.decode('gbk', 'ignore')
        # pattern = re.compile('(?<=\<[h1]\>)[^<,^>](?=\</[h1]\>)')
        result_s = ''
        result_s = s.replace('*', '. ')
        # s = s.encode('raw_unicode_escape').decode('utf8')
    except Exception, ex:
        print "exception found in html_to_plain_text"
        print Exception, ":", ex
        return ''
    return result_s


def measure_similarity_by_search_engine(word1, word2):
    # the similarity is w2 to w1
    word1 = str(word1).strip()
    word2 = str(word2).strip()
    yahooHead = 'http://global.bing.com/search?q='
    yahooTail = '&intlF=1&setmkt=en-us&setlang=en-us&FORM=SECNEN'
    urlList = getAllLinksFromPage(yahooHead + word1 + " " + word2 + yahooTail)
    passage_sentence = html_to_plain_text(urlList[0][0])
    tokens = nltk.word_tokenize(passage_sentence)
    num1 = 0
    num2 = 0
    for t in tokens:
        if t.lower() == word1.lower():
            num1 += 1
        if t.lower() == word2.lower():
            num2 += 1
    if num1 == 0 or num2 == 0:
        return 0
    else:
        if num1 > num2:
            return float(num2) / num1
        else:
            return float(num1) / num2


def getSummaryFromText(passage):
    LANGUAGE = "english"
    SENTENCES_COUNT = 3
    passage = passage.encode("UTF-8")
    parser = PlaintextParser.from_string(passage, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    sentList = list()
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        print(type(sentence))
        sentList.append(sentence)
    return sentList


def listToDict(in_list):
    ret_dict = {}
    for i in in_list:
        ret_dict[i] = i
    return ret_dict


def wordSimilarityToWordDict(w, wordDict):
    sim = 0
    for key in wordDict.keys():
        if str(w) == str(key):
            tSim = 1
        else:
            tSim = getSimilarityByConceptNet(str(w), str(key))
        if None != tSim:
            if tSim > sim:
                sim = tSim
    return sim


def wordDictRelation(MeasuredDict, dictBase):
    length = len(MeasuredDict)
    length_base = len(dictBase)
    if length == 0 or length_base == 0:
        return 0
    sum = 0
    for word in MeasuredDict.keys():
        sum = wordSimilarityToWordDict(word, dictBase) + sum
    return sum / length_base


def MeasureWordSimilarity(wordA, wordB):
    wordAList = wn.synsets(wordA)

    wordBList = wn.synsets(wordB)
    if (len(wordAList) <= 0) or (len(wordBList) <= 0):
        return 0
    keyA = wordAList[0]
    keyB = wordBList[0]
    return keyA.path_similarity(keyB)


def IsNamedEntity(TagStr):
    # p = re.compile('NNP|NN|NNS|NE|PRP|NNPS')
    p = re.compile('NNP|NN|NNS|NE|NNPS')
    m = p.match(TagStr)
    if m:

        return True

    else:

        return False


def IsPronounEntity(TagStr):
    p = re.compile('PRP*')
    m = p.match(TagStr)
    if m:

        return True

    else:

        return False

def IsNumberEntity(TagStr):
    p = re.compile('CD')
    m = p.match(TagStr)
    if m:

        return True

    else:

        return False

def IsProperEntity(TagStr):
    p = re.compile('NNP|NNPS')
    m = p.match(TagStr)
    if m:

        return True

    else:

        return False


def IsVerb(TagStr):
    p = re.compile('V|VB*')
    m = p.match(TagStr)
    if m:

        return True

    else:

        return False


def getAllEntities(TaggedWordList):
    NEList = list()
    for taggedWord in TaggedWordList:
        if IsNamedEntity(taggedWord[1]):
            NEList.append(taggedWord[0])
    return NEList


def getAllNumbers(TaggedWordList):
    NEList = list()
    for taggedWord in TaggedWordList:
        if IsNumberEntity(taggedWord[1]):
            NEList.append(taggedWord[0])
    return NEList


def getAllProperEntities(TaggedWordList):
    NEList = list()
    for taggedWord in TaggedWordList:
        if IsProperEntity(taggedWord[1]):
            NEList.append(taggedWord[0])
    return NEList


def getAllPronounEntities(TaggedWordList):
    NEList = list()
    for taggedWord in TaggedWordList:
        if IsPronounEntity(taggedWord[1]):
            NEList.append(taggedWord[0])
    return NEList


def getAllVerbs(TaggedWordList):
    NEList = list()
    for taggedWord in TaggedWordList:
        if IsVerb(taggedWord[1]):
            NEList.append(taggedWord[0])
    return NEList


def wordInSentStr(word, sentStr):
    sentStr = sentStr.decode('gbk', 'ignore')
    wordsDisctInSent = PipLineTest.getWordDictInSentence(sentStr)
    if wordsDisctInSent.has_key(str(word)):
        return True
    else:
        return False


def get_word_lemma_dict_in_sentence(sent_str):
    word_dict = {}
    wordList = nltk.word_tokenize(sent_str)
    for word in wordList:
        t_word = get_lemma_of_word(word)
        word_dict[t_word] = t_word
    return word_dict


def word_list_in_sentenceStr(word_str_list, sentStr):
    print "the sentence is", sentStr
    sentStr = sentStr.decode('gbk', 'ignore')
    wordsDictInSent = get_word_lemma_dict_in_sentence(sentStr)
    wordsList = wordsDictInSent.keys()
    word_str_lemma_list = list()
    for word_str in word_str_list:
        word_str_lemma_list.append(get_lemma_of_word(word_str))
    print "question nouns ", word_str_lemma_list
    print "sentence words ", wordsDictInSent
    for word in word_str_lemma_list:
        if wordsDictInSent.has_key(str(word)) or (str(word) in wordsList):
            print 'sentence hit!'
            return True
        for k in wordsDictInSent.keys():
            if k in word:
                print 'sentence hit --- key in one synet !'
                return True
    print "sentence pass..."
    return False


def all_word_list_in_sentenceStr(word_str_list, sentStr):
    sentStr = sentStr.decode('gbk', 'ignore')
    wordsDisctInSent = get_word_lemma_dict_in_sentence(sentStr)
    wordsList = wordsDisctInSent.keys()
    word_str_lemma_list = list()
    for word_str in word_str_list:
        word_str_lemma_list.append(get_lemma_of_word(word_str))
    for word in word_str_lemma_list:
        if wordsDisctInSent.has_key(str(word)) or (str(word) in wordsList):
            continue
        else:
            return False
    return True
def hit_percent_in_sentenceStr(word_str_list, sentStr):
    wordList = nltk.word_tokenize(sentStr)
    print 'type of wordlist is ',type(wordList[0])
    wordSet = set(wordList)
    count = 0
    for w in wordSet:
        if unicode(w) in word_str_list:
            print 'one hit'
            count = count + 1
    return count/float(len(word_str_list)+1)

def getMatchSentenceListFromSentenceList(keyWord, sentList):
    RetList = list()
    for sent in sentList:
        wordsDisctInSent = PipLineTest.getWordDictInSentence(sent)
        if wordsDisctInSent.has_key(str(keyWord)):
            RetList.append(sent)
    return RetList


def getSentenceDictMatchingPatternList(keyWords, sentList):
    sentenceDict = {}
    for sent in sentList:
        sentenceDict[sent] = 0
    for sent in sentList:
        for key in keyWords:
            if wordInSentStr(key, sent):
                sentenceDict[sent] = sentenceDict[sent] + 1
    # sentenceDict = sorted(sentenceDict.items(), key=lambda sentenceDict:sentenceDict[1], reverse=True)
    return sentenceDict


def getTopScoredSentenceDict(sentDict):
    Highscore = 0
    ResDict = {}
    for key in sentDict.keys():
        if sentDict[key] > Highscore:
            Highscore = sentDict[key]
    for key in sentDict.keys():
        if sentDict[key] == Highscore:
            ResDict[key] = Highscore
    return ResDict


def questionLoader(filePath):
    f = open(filePath, 'r')
    quesionList = list()
    question = list()
    while True:
        line = f.readline()
        if line:
            if '#####' in str(line):
                quesionList.append(question)
                question = list()
                pass
            else:
                question.append(line.strip()[2:])
        else:
            break
    return quesionList


def getPosTagList(tagTupleList):
    retList = list()
    for tagTuple in tagTupleList:
        retList.append(tagTuple[1])
    return retList


def grammerParser(sentPosList):
    groucho_grammar = nltk.CFG.fromstring("""
    S -> NP VP | NP VP CC VP | NP CC NP VP | CC S
    PP -> P NP
    NP -> N | Det NP | 'PRP$' | 'PRP' | NP NP | 'RP' NP | AD NP | Det AD NP
    VP -> V | VP NP | VP PP | VP ADV | ADV VP | V VP | VP AD
    ADV -> 'RBR' | 'RBS' | 'RB'
    AD -> 'JJ' | 'JJR' | 'JJS'
    Det -> 'DT' | u'-NONE-'
    N -> 'NNP' | 'NN' | 'NNS' | 'NE' | 'CD' | u'CD' | 'WDT' | u'WRB' | u'EX' | 'NNPS'
    V -> 'V' | 'VB' | 'VBS' | 'VBD' | 'VBN' | 'VBG' | 'VBZ' | 'MD' | 'WP' | 'VBP'
    P -> 'in' | 'on' | 'off' | 'TO' | 'IN'
    CC -> 'CC' | u'CC'
    """)
    #    dep_grammar = nltk.grammar.DependencyGrammar.fromstring("""
    #    S -> NP VP | NP VP CC VP | NP CC NP VP
    #    PP -> P NP
    #    NP -> N | Det NP | 'PRP$' | 'PRP' | N NP | 'RP' NP | 'JJ' NP | Det 'JJ' NP
    #    VP -> V | V NP | VP PP | VP 'RB' | 'RB' VP | V V | V 'JJ'
    #    Det -> 'DT'
    #    N -> 'NNP' | 'NN' | 'NNS' | 'NE'
    #    V -> 'V' | 'VB' | 'VBS' | 'VBD' | 'VBN' | 'VBG' | 'VBZ'
    #    P -> 'in' | 'on' | 'off' | 'TO' | 'IN'
    #    CC -> 'CC' | u'CC'
    #    """)
    parser = nltk.TopDownChartParser(groucho_grammar)
    trees = parser.parse(sentPosList)
    treeList = list()
    for tree in trees:
        print(type(tree))
        print(tree.label())
        print(tree)
        treeList.append(tree)
        # print tree.start() ,'-' ,tree.end()
    return treeList


def SentenceFailGrammerParser(sentPosList):
    fail_grammar = nltk.CFG.fromstring("""
    S -> NP VP | NP VP CC VP | NP CC NP VP | CC S
    PP -> P NP
    NP -> N | Det NP | 'PRP$' | 'PRP' | NP NP | 'RP' NP | AD NP | Det AD NP
    VP -> V | VP NP | VP PP | VP ADV | ADV VP | V VP | VP AD
    ADV -> 'RBR' | 'RBS' | 'RB'
    AD -> 'JJ' | 'JJR' | 'JJS'
    Det -> 'DT' | u'-NONE-'
    N -> 'NNP' | 'NN' | 'NNS' | 'NE' | 'CD' | u'CD' | 'WDT'
    V -> 'V' | 'VB' | 'VBS' | 'VBD' | 'VBN' | 'VBG' | 'VBZ' | 'MD' | 'WP' | 'VBP'
    P -> 'in' | 'on' | 'off' | 'TO' | 'IN'
    CC -> 'CC' | u'CC'
    """)
    parser = nltk.ChartParser(fail_grammar)
    trees = parser.chart_parse(sentPosList)
    treeList = list()
    for tree in trees:
        print type(tree)
        print tree.lhs
        print (tree)
        treeList.append(tree)
    return treeList


def removePunctuation(s):
    s = s.replace(':', ' ')
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    s = regex.sub(' ', s)
    return s


def getVBFromNoneSentence(posTupleList):
    endPos = len(posTupleList) - 1
    VBEnd = 0
    retList = list()
    i = 0
    j = 0
    if endPos == 0:
        return posTupleList[0][0]
    while i <= endPos:
        i = j
        vbStr = ''
        if i == endPos:
            if IsVerb(posTupleList[i][1]):
                vbStr = vbStr + (' ' + posTupleList[i][0])
                retList.append(vbStr)
                break
            else:
                break
        else:
            if IsVerb(posTupleList[i][1]):
                j = i + 1
                while j <= endPos:
                    vbStr = vbStr + (' ' + posTupleList[j - 1][0])
                    if j == endPos:
                        vbStr = vbStr + (' ' + posTupleList[j][0])
                        retList.append(vbStr)
                        break
                    if posTupleList[j][1] == 'CC' or (
                                IsVerb(posTupleList[j][1]) and IsNamedEntity(posTupleList[j - 1][1])):
                        j = j + 1
                        retList.append(vbStr)
                        break
                    else:
                        j = j + 1
            else:
                i = i + 1
                j = i
    return retList


def getDeepestNPFromChartParser(tree, posTupleList):
    retList = list()
    name = str(tree.lhs())
    right = str(tree.rhs())
    print right
    if name == 'VP':
        t1 = tree.start()
        t2 = tree.end()
        if len(posTupleList) < t2:
            t2 = t2 - 1
        for i in range(t1, t2):
            retList.append(posTupleList[i][0])
    return retList


def getDeepestNP(tree, posTupleList):
    name = tree.label()
    h = tree.height()
    print name, h
    posList = tree.leaves()
    retList = list()
    t = tree
    for s in t.subtrees():  # for s in t.subtrees(lambda t: t.height() <= 4):
        if s.label() == 'NP':
            npStr = ''
            for leave in (s.leaves()):
                for i in range(0, len(posList)):
                    if leave is posList[i]:
                        npStr = npStr + ' ' + str(posTupleList[i][0])
            retList.append(npStr)
    return retList


def getDeepestVP(tree, posTupleList):
    name = tree.label()
    h = tree.height()
    print name, h
    posList = tree.leaves()
    retList = list()
    t = tree
    for s in t.subtrees():
        if s.label() == 'VP':
            vpStr = ''
            for leave in (s.leaves()):
                for i in range(0, len(posList)):
                    if leave is posList[i]:
                        vpStr = vpStr + ' ' + str(posTupleList[i][0])
            retList.append(vpStr)
    return retList


from pattern.en import Sentence
from pattern.en import tree
from pattern.en import parsetree
from pattern.en import tag


def getRelation(SentStr):
    # get verb phrase
    # get the noun before it ,get the none after it
    # return the none verb none tuple


    # taggedstring = parse(SentStr)
    # relationList = list()
    # sentence = Sentence(taggedstring, token=['WORD', 'POS', 'CHUNK', 'PNP', 'REL', 'LEMMA'])
    s = parsetree(SentStr, relations=True, lemmata=True)
    return (s[0]).relations


def getSubSentence(posTrees, posTupleList):
    subSentDict = {}
    print "inside getSubSentence ", posTrees
    for tree in posTrees:
        print "getSubSentence", tree
        root = (tree.label())
        if root == 'S':
            subSent = ''
            PosStr = ''
            t1 = tree.start()
            t2 = tree.end()
            if t2 <= len(posTupleList) - 1:
                tx = t2
            else:
                tx = t2 - 1
            for i in range(t1, tx + 1):
                w = str(posTupleList[i][0])
                p = str(posTupleList[i][1])
                subSent = subSent + ' ' + w
                PosStr = PosStr + ' ' + p
            if subSentDict.has_key(subSent):
                continue
            else:
                subSentDict[subSent] = subSent
                print 'in getSubSentence: get a sub sentence', tree
                print 'the sub sentence is ', subSent
                print 'the pos is ', PosStr
    return subSentDict


def getSimilarityByConceptNet(wordA, wordB):
    import json
    if wordA == '' or wordB == '':
        return 0
    wordA = str(wn.morphy(wordA))
    wordB = str(wn.morphy(wordB))
    queryUrl = 'http://conceptnet5.media.mit.edu/data/5.2/assoc/c/en/' + wordA + '?filter=/c/en/' + wordB + '&limit=1'
    try:
        jsonText = htmlDownLoader.getTextFromURL(queryUrl)
        print jsonText
        sim = json.loads(jsonText)
        if not sim.get("similar"):
            return 0
        if sim["similar"] != None and len(sim["similar"]) != 0:
            return sim["similar"][0][1]
        else:
            return 0
    except:
        return 0


def getLongestVP(strList):
    max_length = len(strList[0])
    longVP = strList[0]
    for vp in strList:
        if len(vp) > max_length:
            longVP = vp
    return longVP


def removePunctuationInStrList(StrList):
    retList = list()
    for strSent in StrList:
        retList.append(removePunctuation(strSent))
    return retList


def getNPListFromStr(SentenceStr):
    tokens = nltk.word_tokenize(SentenceStr)
    tags = nltk.pos_tag(tokens)
    ners = getAllEntities(tags)
    return ners


def getVPListFromStr(SentenceStr):
    tokens = nltk.word_tokenize(SentenceStr)
    tags = nltk.pos_tag(tokens)
    vbs = getAllVerbs(tags)
    return vbs


def parse_sentence(sent):
    tokens = nltk.word_tokenize(removePunctuation(sent))
    tags = nltk.pos_tag(tokens)
    posTags = getPosTagList(tagTupleList=tags)
    temp_trees = grammerParser(posTags)
    return temp_trees
    # # getSubSentence(tempTrees,tags)
    # nList = list()
    # vList = list()
    # LastIndex = len(tempTrees) - 1
    # if LastIndex == -1:
    #     vList = getVBFromNoneSentence(tags)
    # else:
    #     nList = getDeepestNP(tempTrees[LastIndex], tags)
    #     vList = getDeepestVP(tempTrees[LastIndex], tags)
    # if len(vList) > 0:
    #     longVP = getLongestVP(vList)
    # else:
    #     longVP = getLongestVP(nList)
    # tagsFromVP = longVP.strip().split(' ')
    # related_passage_sentence_ner_dict = listToDict(tagsFromVP)


def sentence_parse(sent_str):
    opt = sent_str.decode('gbk', 'ignore')
    tokens = nltk.word_tokenize(removePunctuation(opt))
    tags = nltk.pos_tag(tokens)
    posTags = getPosTagList(tagTupleList=tags)
    tempTrees = grammerParser(posTags)
    if len(tempTrees)==0:
        return False
    else:
        return True


def get_synsets(noun_str):
    syn_str_list = list()
    syn_list = wn.synsets(noun_str)
    for s in syn_list:
        n_str = (s._name).split('.')[0].replace('_', ' ')
        if n_str not in syn_str_list:
            syn_str_list.append(n_str)
    syn_str_list.append(noun_str)
    return syn_str_list


def get_verb_list_hit(verb_list, sent_verb_list):
    hit = 0
    verb_lemma = list()
    lmtzr = WordNetLemmatizer()
    sent_lemma = list()
    for v in verb_list:
        verb_lemma.append(lmtzr.lemmatize(v))
    for sv in sent_verb_list:
        sent_lemma.append(lmtzr.lemmatize(sv))
    for vl in verb_lemma:
        if vl in sent_lemma:
            hit += 1
    return hit


def get_lemma_of_word(word_str):
    if word_str is None or word_str == "":
        return word_str
    lmtzr = WordNetLemmatizer()
    lemma = lmtzr.lemmatize(word_str)
    return lemma

# Answer steps
# 1. Get key words in the question
# 2. Search the key words in the article(search NE first if found then check if Verbs match )
# 3. If not found measure the word similartiy between words in question and the ones in
# article.Try to get the most closely relatied sentence in the article to the question 
# 4. Compare it the the options.
# 5. Choose the closiest option to the sentence(s) in the article


# Get summary sentence
# Get main points for each segment
# Get time- place -person -for an event
# Answer questions about this article
if __name__ == '__main__':
    # score = MeasureWordSimilarity('diary','career')
    # print score
    stemmer = PorterStemmer
    passage = FileUtils.OpenFileGBK('./reading/passage1.txt')
    blob = TextBlob(passage)
    NoneList = blob.noun_phrases
    for sentence in blob.sentences:
        print(sentence.sentiment.polarity)
    passage_sentList = PipLineTest.getSentenceListFromText(passage)
    qList = questionLoader('./reading/questions1.txt')
    temp_qestion = qList[3]  # the question number

    question = temp_qestion[0].decode('gbk', 'ignore')
    tokens = nltk.word_tokenize(question)
    tags = nltk.pos_tag(tokens)
    ners = getAllEntities(tags)
    verbs = getAllVerbs(tags)
    keyWordsDict = PipLineTest.getKeyWordDictFromCleanedSentence(question)
    sentDict = getSentenceDictMatchingPatternList(ners, passage_sentList)
    sentDict = getTopScoredSentenceDict(sentDict)
    sentDict = getSentenceDictMatchingPatternList(verbs, sentDict)
    related_passage_sentence_ner_dict = {}
    for sent in sentDict.keys():
        tokens = nltk.word_tokenize(removePunctuation(sent))
        tags = nltk.pos_tag(tokens)
        relation = getRelation(sent)
        relationStr = ''
        if relation:
            for k in relation:
                print type(relation[k])
                print k, relation[k]
                for s in relation[k]:
                    print relation[k][s].string
                    relationStr = relationStr + " " + relation[k][s].string
        print relationStr
        posTags = getPosTagList(tagTupleList=tags)
        tempTrees = grammerParser(posTags)
        # getSubSentence(tempTrees,tags)
        nList = list()
        vList = list()
        LastIndex = len(tempTrees) - 1
        if LastIndex == -1:
            vList = getVBFromNoneSentence(tags)
        # tempTrees = SentenceFailGrammerParser(posTags)
        #            for tree in tempTrees:
        #                tList = getDeepestNPFromChartParser(tree,tags)
        #                if tList:
        #                    vList = vList.extend(tList)
        else:
            nList = getDeepestNP(tempTrees[LastIndex], tags)
            vList = getDeepestVP(tempTrees[LastIndex], tags)
        # t_ners = getAllEntities(tags)
        if len(vList) > 0:

            longVP = getLongestVP(vList)
        else:
            longVP = getLongestVP(nList)
        tagsFromVP = longVP.strip().split(' ')
        related_passage_sentence_ner_dict = listToDict(tagsFromVP)
        # t_verbs = getAllVerbs(tags)

    option_score_list_for_similarity = list()
    for i in range(1, 5):
        opt = temp_qestion[i].decode('gbk', 'ignore')
        tokens = nltk.word_tokenize(removePunctuation(opt))
        tags = nltk.pos_tag(tokens)
        posTags = getPosTagList(tagTupleList=tags)
        tempTrees = grammerParser(posTags)
        # nltk.tree.Tree
        print type(tempTrees)
        print 'options'
        nList = list()
        vList = list()
        LastIndex = len(tempTrees) - 1
        if LastIndex == -1:
            vList = getVBFromNoneSentence(tags)
        # tempTrees = SentenceFailGrammerParser(posTags)
        #            for tree in tempTrees:
        #                tList = getDeepestNPFromChartParser(tree,tags)
        #                if tList:
        #                    vList = vList.extend(tList)
        else:
            nList = getDeepestNP(tempTrees[LastIndex], tags)
            vList = getDeepestVP(tempTrees[LastIndex], tags)

        t_ners = getAllEntities(tags)
        t_verbs = getAllVerbs(tags)
        if len(vList) > 0:

            longVP = getLongestVP(vList)
        else:
            if len(nList) > 0:

                longVP = getLongestVP(nList)
            else:
                longVP = removePunctuation(opt)
        tagsFromVP = longVP.split(' ')
        KeyWordsDictFromOption = listToDict(tagsFromVP)
        # KeyWordsDictFromOption = PipLineTest.getKeyWordDictFromCleanedSentence(opt)
        option_score_list_for_similarity.append(
            wordDictRelation(KeyWordsDictFromOption, related_passage_sentence_ner_dict))
    print question
    print sentDict
    print option_score_list_for_similarity
    # ners = nltk.ne_chunk(tags)
    # print '%s --- %s' % (str(ners),str(ners.label))
