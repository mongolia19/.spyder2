import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import downloaderAndContentExtractor
import nlpExmp
import re
import PatternLoader
import nltk
from BeautifulSoup import BeautifulSoup
###
##To Do: impliement a function to envalueate the importance of a sentence in an article
def getText(httpLink):
    return downloaderAndContentExtractor.ExtractContentFromURL(httpLink)

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
def cleanText(RawText):
    if not (RawText  == None):
        RawText = re.sub('\n+', ' ', RawText)
        RawText = re.sub(('\s+'),' ',RawText)
        RawText = re.sub(" +", " ", RawText)#remove redandant spaces

        genPattern = re.compile("<[^>]*?>",re.S|re.I|re.M)
        RawText = genPattern.sub('',RawText)#remove all <....>    

        RawText = BScleanText(RawText)
        RawText = filter_tags(RawText)
    
        RawText = RawText.lower()
        return RawText
    else:
        return ''
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
	


url = "http://www.chinadaily.com.cn/world/2015xiattendwwii/2015-04/29/content_20627695.htm"

RawText = getText(url)
exposPattern = loadPatterns()
patternHashMap = {}
for p in exposPattern.patternList:
    patternHashMap[p] = p
print patternHashMap

cleanedText = cleanText(RawText)

keyWordsList = ExtractKeyWords(cleanedText,1)
print keyWordsList
patternHashMap[0] = keyWordsList[0][0]
sent_list = nltk.sent_tokenize(cleanedText)
imp = ImportanceMeasure( sent_list[0],patternHashMap)
print imp