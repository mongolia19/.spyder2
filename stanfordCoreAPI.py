# -*- coding: utf-8 -*-
import sys
"""
Created on Thu Jun 11 21:49:58 2015

@author: mongolia19
"""
import os
from nltk.tokenize import sent_tokenize
import corenlp
import requests

class dep_pair:
    def __init__(self, former, latter, dep_type):
        self.former = former
        self.latter = latter
        self.dep_type = dep_type


def get_nugget_from_dep_list(dep_list):
    dep_dict = dict()
    nugget_list = list()
    for i in range(0, len(dep_list)-1):
        num = len(set([dep_list[i].former, dep_list[i].latter, dep_list[i + 1].former, dep_list[i + 1].latter]))
        if num <4:
        # if dep_list[i].latter == dep_list[i+1].former:
            nugget = list(set([dep_list[i].former, dep_list[i].latter, dep_list[i+1].former, dep_list[i+1].latter ]))
            nugget_list.append(nugget)
        # if dep.former not in dep_dict.keys():
        #     dep_dict[dep.former] = dep
        # if dep.former in dep_dict.values():
        #     if dep.dep_type != dep_dict[dep.former].dep_type:
        #         nugget = list(set([dep_dict[dep.former].former, dep_dict[dep.former].latter, dep.former, dep.latter]))
        #         nugget_list.append(nugget)
        # if dep.latter in dep_dict.keys():
        #     if dep.dep_type != dep_dict[dep.latter].dep_type:
        #         nugget = list(set([dep_dict[dep.latter].former, dep_dict[dep.latter].latter, dep.former, dep.latter]))
        #         nugget_list.append(nugget)
    del dep_dict
    return nugget_list

text  ="who is the founding father of USA"


def dep_pair_from_stanford_server(sent_string):
    url = 'http://127.0.0.1:9000'
    properties = {'annotators': 'tokenize,ssplit,parse', 'outputFormat': 'json'}
    # properties 要转成字符串, requests包装URL的时候貌似不支持嵌套的dict
    params = {'properties': str(properties)}
    data = "Our experience is that this simple,\
uniform representation is quite accessible to non-linguists thinking about tasks involving information\
 extraction from text and is effective in relation extraction applications."
    # data = "I sat on the chair"
    import chardet
    # encode = chardet.detect(sent_string)
    #
    data = sent_string.encode('utf-8')
    resp = requests.post(url, data, params=params)
    json_str = resp.content
    import json
    json_str = json_str.decode("utf-8")
    json_obj = json.loads(json_str)
    print(len(list(json_obj.keys())))
    dep_list = list()
    for k in list(json_obj.keys()):
        print(data, " contains ", len(json_obj[k]), "sentences")
        if len(json_obj[k])<=0:
            return list()
        print(json_obj[k][0]["basicDependencies"])
        dep_list = json_obj[k][0]["basicDependencies"]
        break
        # print len(json_obj[k][0]["basicDependencies"])
    dep_obj_list = list()
    for dep_obj in dep_list:
        if "sub" in str(dep_obj['dep']):
            print(dep_obj['dependentGloss'], dep_obj['governorGloss'])
            dep_obj_list.append(dep_pair(dep_obj['dependentGloss'], dep_obj['governorGloss'], "sub"))
        if "obj" in str(dep_obj['dep']):
            print(dep_obj['governorGloss'], dep_obj['dependentGloss'])
            dep_obj_list.append(dep_pair(dep_obj['governorGloss'], dep_obj['dependentGloss'], "obj"))
        if "cop" in str(dep_obj['dep']):
            print(dep_obj['governorGloss'], dep_obj['dependentGloss'])
            dep_obj_list.append(dep_pair(dep_obj['governorGloss'], dep_obj['dependentGloss'], "obj"))
        if "mod" in str(dep_obj['dep']):
            print(dep_obj['governorGloss'], dep_obj['dependentGloss'])
            dep_obj_list.append(dep_pair(dep_obj['governorGloss'], dep_obj['dependentGloss'], "obj"))
        if "prep" in str(dep_obj['dep']):
            print(dep_obj['governorGloss'], dep_obj['dependentGloss'])
            dep_obj_list.append(dep_pair(dep_obj['governorGloss'], dep_obj['dependentGloss'], "obj"))
        if "xcomp" in str(dep_obj['dep']):
            print(dep_obj['governorGloss'], dep_obj['dependentGloss'])
            dep_obj_list.append(dep_pair(dep_obj['governorGloss'], dep_obj['dependentGloss'], "obj"))

    return dep_obj_list


def get_nuggets_by_coreNLp(sent_string):
    if len(str(sent_string).split(" "))>100:
        return list()
    print( "get_nuggets_by_coreNLp: " + sent_string)
    dep_obj_list = dep_pair_from_stanford_server(sent_string)
    print("nuggets==============")
    nuggets = get_nugget_from_dep_list(dep_obj_list)
    print(nuggets)
    return nuggets


# with corenlp.CoreNLPClient(annotators='tokenize ssplit pos'.split()) as client:
#     ann = client.annotate(text)
#     sentence = ann.sentence[0]
#
#     for token in sentence.token:
#         print token.word, token.pos
# def write_parse_products(self, parse):
# 	words = parse['words']
#
# 	word_objects = []
# 	text = ""
# 	for i, word_info in enumerate(words):
# 		properties = word_info[1]
# 		token = word_info[0].lower().strip()
# 		surface = word_info[0].strip()
# 		pos = properties['PartOfSpeech']
# 		space_before = ""
# 		if i > 0:
# 			after_previous_word = int(words[i-1][1]['CharacterOffsetEnd'])
# 			space_before = " "*(int(properties['CharacterOffsetBegin']) -
# 				after_previous_word)
# 		text += space_before + surface
#
# 	raw_sentence = text.replace("(", "(").replace(")", ")").replace("``", "\"").replace("\"\"", "\"")
#
# 	for dependency_info in parse['dependencies']:
# 		relation_name = dependency_info[0]
# 		gov_index = int(dependency_info[2]) - 1
# 		gov = word_objects[gov_index]
# 		dep_index = int(dependency_info[4]) - 1
# 		dep = word_objects[dep_index]

# The directory in which the stanford core NLP .jar is located -- you have to
# download this from their website.
# CORE_NLP_DIR = "/home/idroid/Downloads/stanford-corenlp-full-2017-06-09"
# PARSER = StanfordCoreNLP(CORE_NLP_DIR)
#
# in_file = "./text/summaries.txt"
# text = open(in_file, 'r').read()
# sentences = sent_tokenize(text)  # Break the text into sentences.
# for i, sentence in enumerate(sentences):
# 	try:
# 		parse = PARSER.raw_parse(sentence)
# 		if i%50 == 0:
# 			print " Entered sentence " + str(i) + " of " + str(len(sentences))
# 		write_parse_products(parse['sentences'][0])
# 	except Exception:
# 		print "Error on sentence:\n\t " + sentence + " \n "
# 		pass
