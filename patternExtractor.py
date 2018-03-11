# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 00:08:18 2015

@author: mongolia19
"""
import OpenAnswer
import PipLineTest
import FileUtils
def isSameCombination(tupleA ,tupleB):
    listA = list(tupleA)
    listB = list(tupleB)
    listA.sort(reverse=False)
    listB.sort(reverse=False)
    print '-------------    isSameCombination  -------------'
    print listA
    print listB
    if cmp(listA,listB) != 0:
        return False
    else:
        return True
def removeDiffArrangeMents(Tuplelist):
    for i in range(0,len(Tuplelist)):
        for j in range(i+1,len(Tuplelist)):
            if j>=len(Tuplelist):
                break
            if isSameCombination(Tuplelist[i],Tuplelist[j]):
                del Tuplelist[j]
    return Tuplelist
if __name__ == "__main__":
    noneList = list(['some stories about albert einstein','the world shall be destroied'])

    for n in noneList:
        OpenAnswer.questionPatternMining('', '', n, './default_patterns_txt.txt')

    print '.....................default questions patterns ..........................'
    whatTxt = FileUtils.OpenFileUnicode('./default_patterns_txt.txt')
    MainSearchResultSentencesList = OpenAnswer.getSentencesFromPassageText(whatTxt)

    qDict = {}
    combinationDict = PipLineTest.getWordCombinationDict(3,MainSearchResultSentencesList,qDict)

    patternList = OpenAnswer.getTopPercentCombinations(combinationDict, 0.0001)
    patternList = removeDiffArrangeMents(patternList)
    for p in patternList:
        print p
        OpenAnswer.WriteTupleToFile('./default_tuple_patterns.txt', p)
    for k in combinationDict.keys():
        if combinationDict[k] > 50:
            print k , ":" , combinationDict[k]
