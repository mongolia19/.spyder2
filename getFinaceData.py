# -*- coding: utf-8 -*-
import tushare as ts
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import AdaBoostClassifier
import pandas as pd
# d = ts.get_tick_data('601318',date='2017-06-26')
# print d
# GBDT(Gradient Boosting Decision Tree) Classifier
def gradient_boosting_classifier(train_x, train_y, tree_num):
    from sklearn.ensemble import GradientBoostingClassifier
    model = GradientBoostingClassifier(n_estimators=tree_num)
    model.fit(train_x, train_y)
    return model
def naive_bayes_classifier(train_x, train_y):
    from sklearn.naive_bayes import MultinomialNB
    model = MultinomialNB(alpha=0.01)
    model.fit(train_x, train_y)
    return model
# Logistic Regression Classifier
def logistic_regression_classifier(train_x, train_y):
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(penalty='l2')
    model.fit(train_x, train_y)
    return model
def get_data_and_label(stock_num, start_date, end_date):
    e = ts.get_hist_data(stock_num,start=start_date,end=end_date)
    data = list()
    for i in e.iterrows():
        # print( i)
        # print (i[-1].values)
        # data.append((i[-1].close,i[-1].high,i[-1].low,i[-1].open,i[-1].ma5,i[-1].ma10,i[-1].ma20))
        data.append((i[-1].close,i[-1].high,i[-1].low,i[-1].open))
    BIGUP = 2
    UP = 1
    DOWN = -1
    BIGDOWN = -2
    extended_list = list()
    result_list = list()
    for tup in data:
        extended_list.append(tup)
        result_list.append(tup[0])
    a_few_day_list = list()
    label_list = list()
    rim = 5
    for i in range(rim, len(extended_list)):
        total_one = list()
        for j in range(rim - 1):
            total_one.extend(list(extended_list[i - j]))
        total_one = tuple(total_one)
        a_few_day_list.append(total_one)
        label_list.append(UP if extended_list[i][0]>extended_list[i-1][0] else DOWN)
    if len(a_few_day_list) <= 1:
        return a_few_day_list, label_list
    a_few_day_list.pop()
    label_list.pop(0)
    del data, result_list, extended_list
    return a_few_day_list, label_list
    for d in range(len(data)):
        if d>1:
            print(type(data[d]))
            print(data[d])
            combined = np.append(data[d],data[d-1])
            combined = np.append(combined,data[d-2])
            extended_list.append(combined)
        else:
            combined = np.append(data[d],data[d])
            combined = np.append(combined,data[d])
            extended_list.append(combined)
        if d+1<len(data):
            if data[d+1][1]>data[d][1] and data[d+1][1]-data[d][1]:
                result_list.append(UP)
            else:
                result_list.append(DOWN)
        else:
            result_list.append(DOWN)
    del data
    print( len(extended_list))
    print (len(result_list))
    return extended_list, result_list
def get_data_and_label_for_regressor(stock_num, start_date, end_date):
    e = ts.get_hist_data(stock_num,start=start_date,end=end_date)
    data = list()
    for i in e.iterrows():
        # print( i)
        # print (i[-1].values)
        # data.append((i[-1].close,i[-1].high,i[-1].low,i[-1].open,i[-1].ma5,i[-1].ma10,i[-1].ma20))
        data.append((i[-1].close,i[-1].high,i[-1].low,i[-1].open,i[-1].volume))
    BIGUP = 2
    UP = 1
    DOWN = -1
    BIGDOWN = -2
    extended_list = list()
    result_list = list()
    for tup in data:
        extended_list.append(tup)
        result_list.append(tup[0])
    a_few_day_list = list()
    label_list = list()
    rim = 5
    for i in range(rim, len(extended_list)):
        total_one = list()
        for j in range(rim - 1):
            total_one.extend(list(extended_list[i - j]))
        total_one = tuple(total_one)
        a_few_day_list.append(total_one)
        # label_list.append(UP if extended_list[i][0]>extended_list[i-1][0] else DOWN)
        label_list.append(extended_list[i][0])
    if len(a_few_day_list) <= 1:
        return a_few_day_list, label_list
    a_few_day_list.pop()
    label_list.pop(0)
    del data, result_list, extended_list
    return a_few_day_list, label_list
    exit(-1)
    for d in range(len(data)):
        if d>1:
            print(type(data[d]))
            print(data[d])
            combined = np.append(data[d],data[d-1])
            combined = np.append(combined,data[d-2])
            extended_list.append(combined)
        else:
            combined = np.append(data[d],data[d])
            combined = np.append(combined,data[d])
            extended_list.append(combined)
        if d+1<len(data):
            if data[d+1][1]>data[d][1] and data[d+1][1]-data[d][1]:
                result_list.append(UP)
            else:
                result_list.append(DOWN)
        else:
            result_list.append(DOWN)
    del data
    print( len(extended_list))
    print (len(result_list))
    return extended_list, result_list
def get_data_and_label_2day(stock_num, start_date, end_date):
    e = ts.get_hist_data(stock_num,start=start_date,end=end_date)
    data = list()
    for i in e.iterrows():
        # print i
        # print i[-1].values
        data.append(i[-1].values)

    UP = 1
    DOWN = -1
    extended_list = list()
    result_list = list()
    for d in range(len(data)):
        if d>0:
            combined = np.append(data[d],data[d-1])
            # combined = np.append(combined,data[d-2])
            extended_list.append(combined)
        else:
            combined = np.append(data[d],data[d])
            # combined = np.append(combined,data[d])
            extended_list.append(combined)
        if d+1<len(data):
            if data[d+1][1]>data[d][1]:
                result_list.append(UP)
            else:
                result_list.append(DOWN)
        else:
            result_list.append(DOWN)
    del data
    print( len(extended_list))
    print (len(result_list))
    return extended_list, result_list


def showTestWithLabel(test_result,test_label_list):
    """使用scatter()绘制散点图"""
    import matplotlib.pyplot as plt 
    x_values = range(len(test_result))
    y_values = test_result
    '''
    scatter() 
    x:横坐标 y:纵坐标 s:点的尺寸
    '''
    plt.scatter(x_values, y_values, marker = 'x', color = 'm', s=50)
    plt.scatter(x_values, test_label_list, marker = 'o', color = 'c', s=30)

    # f2 = plt.figure(2)  
    # idx_1 = find(label==1)  
    # p1 = plt.scatter(x[idx_1,1], x[idx_1,0], marker = 'x', color = 'm', label='1', s = 30)  
    # idx_2 = find(label==2)  
    # p2 = plt.scatter(x[idx_2,1], x[idx_2,0], marker = '+', color = 'c', label='2', s = 50)  
    # 设置图表标题并给坐标轴加上标签
    plt.title('Square Numbers', fontsize=24)
    plt.xlabel('Value', fontsize=14)
    plt.ylabel('Square of Value', fontsize=14)
    # 设置刻度标记的大小
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.show()

from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_blobs
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

stockindex = '000001'
extended_list, result_list = get_data_and_label_for_regressor(stockindex, '2001-06-23', '2016-07-30')
tot = len(result_list)
increaseCount = 0
for i in result_list:
    if i == 1:
        increaseCount += 1
print("total count is "+ str(tot )+ " increase count is " +str(increaseCount) + " rate is " + str(increaseCount/tot))
    # e = ts.get_hist_data('000002',start='2014-06-23',end='2017-07-30')
X, y = extended_list, result_list
X = StandardScaler().fit_transform(X)
# data set

test_list, test_label_list = get_data_and_label_for_regressor(stockindex, '2017-08-01', '2018-02-23')
test_list = StandardScaler().fit_transform(test_list)
    # e = ts.get_hist_data('000002',start='2014-06-23',end='2017-07-30')
# X, y = test_list, test_label_list
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier
from plot_report import main_plot
# fit a k-nearest neighbor model to the data
# model = KNeighborsClassifier()
# model.fit(X, y)
# clf = DecisionTreeClassifier(max_depth=None, min_samples_split=2,random_state = 0)
# scores = cross_val_score(clf, X, y)
# print "decision tree : ", scores.mean()
# test_result = model.predict(test_list)
# print ("KNeighborsClassifier on test: ", classification_report(test_label_list,test_result))
# score
# num_trees = 460
# clf = RandomForestClassifier(n_estimators=num_trees, max_depth=None,min_samples_split = 2, random_state = 0,max_features='sqrt', n_jobs=4)
# # 定义一个随机森林分类器
# scores = cross_val_score(clf, X, y)
# print "random forest : ", scores.mean()

# 这里是随机森林训练器的模型精确度得分
from sklearn import svm
parameters = {'kernel':('linear', 'rbf'), 'C':[1, 2, 4], 'gamma':[0.125, 0.25, 0.5 ,1, 2, 4]}

svr = svm.SVR()  # class
clf = GridSearchCV(svr, parameters, n_jobs=1)
clf.fit(X, y)  # training the svc model
cv_result = pd.DataFrame.from_dict(clf.cv_results_)
with open('cv_result.csv', 'w') as f:
    cv_result.to_csv(f)
print('The parameters of the best model are: ')
print(clf.best_params_)
# y_pred = clf.predict(iris.data)
# clf = ExtraTreesClassifier(n_estimators=num_trees, max_depth=None,min_samples_split = 2, random_state = 0)

scores = cross_val_score(clf, X, y)
print ("svm : ", scores.mean())
test_result = clf.predict(test_list)
# print ("svm on test: \r\n", classification_report(test_label_list,test_result))

showTestWithLabel(test_result, test_label_list)

exit(0)
# model = gradient_boosting_classifier(X,y,6000)
# test_result = model.predict(test_list)
# report = classification_report(test_label_list,test_result)
#
# print "gradient_boosting_classifier on test: \r\n", classification_report(test_label_list,test_result)
for i in range(10,100):
    print('ploting '+ str(i)+ " tree forest...")
    model = gradient_boosting_classifier(X, y, 20000)
    bdt = AdaBoostClassifier(model,
                             algorithm="SAMME",
                             n_estimators=i)

    bdt.fit(X, y)
    test_result = bdt.predict(test_list)
    report_str = str(classification_report(test_label_list, test_result))
    main_plot(report_str, './pics/'+ str(i) + 'tree.png')