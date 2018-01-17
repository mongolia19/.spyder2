# -*- coding: utf-8 -*-
indexors = [
"CCI","KDJ","MOM","Obv","ROC","RSI","SLOWKD","VDL","W%R","BIAS","BIAS36","boll",\
"ASI","DMA","DMI","DPO","EMV","MACD","TRIX","VHF","VPT",\
"BRAR","CR","心理线","VR","MAD","放量","缩量"]
behaviors = ['金叉','死叉','买入信号','卖出信号',"超买","超卖"]
import itertools
indexer_comb_list = list(itertools.combinations(indexors,2))
behavior_arrange_list = list(itertools.permutations(behaviors,2))
file = open('stratergy.txt','a')
stratgy_list = list()
for index_comb in indexer_comb_list:
    for behavior_arrange in behavior_arrange_list:
        index0 = str(index_comb[0])
        index1 = str(index_comb[-1])
        if index_comb[0] == "放量"  or index_comb[0] == "缩量":
            action0 = ""
        else:
            action0 = str(behavior_arrange[0])
        if index_comb[-1] == "缩量" or index_comb[-1] == "放量":
            action1 = ""
        else:
            action1 = str(behavior_arrange[-1])
        outString = index0 + action0 + " " + index1 + action1 + "\r\n"
        print outString
        stratgy_list.append(outString)
file.writelines(stratgy_list)
file.close()

