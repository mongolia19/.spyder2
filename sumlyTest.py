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

import FileUtils
from textblob import TextBlob
LANGUAGE = "english"
SENTENCES_COUNT = 3


if __name__ == "__main__":
    url = "http://en.wikipedia.org/wiki/Automatic_summarization"
    #parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    # or for plain text files
    passage = FileUtils.OpenFileGBK('./reading/passage.txt')
#    passage = passage.encode("UTF-8")
#    parser = PlaintextParser.from_string(passage, Tokenizer(LANGUAGE))
#    stemmer = Stemmer(LANGUAGE)
#
#    summarizer = Summarizer(stemmer)
#    summarizer.stop_words = get_stop_words(LANGUAGE)
#
#    for sentence in summarizer(parser.document, SENTENCES_COUNT):
#        print(type(sentence))
#        print(sentence)
    blob = TextBlob(passage)
    NoneList = blob.noun_phrases
    print NoneList