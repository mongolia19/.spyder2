__author__ = 'idroid'



f = open("./reading/passage.txt",'r')
str_article = (f.read())
f.close()

from sumlyTest import get_all_entities_by_nltk, get_summary_sentences_from_article_text_sentiment, get_summary_sentences_by_summarizer_voting
out = get_summary_sentences_from_article_text_sentiment(str_article)
out1 = get_summary_sentences_by_summarizer_voting(str_article)
# sent_list = Sentiment(str_article)
ner_list = list()
print "=========================================="
for sent in out + out1:
    print sent
    ner_list = ner_list + get_all_entities_by_nltk(sent[0])
    print "\r\n"
print "*******************************************"
# ner_list = get_all_entities_by_nltk(str_article)
ner_list = list(set(ner_list))
for ner in ner_list:
    print ner, "\r\n"
# extract nouns
# search sentences with key sentences