import downloaderAndContentExtractor
import nlpExmp
import re
import PatternLoader

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
        return RawText
    else:
        return ''

url = "http://www.cnblogs.com/Ninputer/archive/2011/06/13/2080094.html" 

RawText = getText(url)
exposPattern = loadPatterns()
print exposPattern.patternList
cleanedText = cleanText(RawText)
keyWordsList = ExtractKeyWords(cleanedText,1)
print keyWordsList