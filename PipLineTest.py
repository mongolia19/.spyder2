import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import downloaderAndContentExtractor
import nlpExmp
import re
import PatternLoader
import nltk
###
##To Do: impliement a function to envalueate the importance of a sentence in an article
def getText(httpLink):
    return downloaderAndContentExtractor.ExtractContentFromURL(httpLink)

def loadPatterns():
    return PatternLoader.LoadExpositoryPattern(PatternLoader.CONST_PATTERN_FILE_PATH)

def ExtractKeyWords(text,KeyCount):
    return nlpExmp.keyWordsExtractor(text,KeyCount)

def cleanText(RawText):
    if not (RawText  == None):
        RawText = re.sub('<[^>]+>','',RawText)
        RawText = re.sub('\n+', '\n', RawText)
        RawText = re.sub(('\s+'),' ',RawText)
        RawText = re.sub(" +", " ", RawText)#remove redandant spaces
        return RawText
    else:
        return ''
def ImportanceMeasure(sentence):
    words_of_sent = nltk.word_tokenize(sentence)
    print len(words_of_sent)
    print type(words_of_sent)
    for word in words_of_sent:
        print word
	print type(word)


url = "http://www.wikihow.com/Create-an-Ice-Bowl" 

RawText = getText(url)
exposPattern = loadPatterns()
patternHashMap = {}
for p in exposPattern.patternList:
    patternHashMap[p] = p
print patternHashMap

cleanedText = cleanText(RawText)
sent_list = nltk.sent_tokenize(cleanedText)
ImportanceMeasure( sent_list[0])

keyWordsList = ExtractKeyWords(cleanedText,1)
print keyWordsList
