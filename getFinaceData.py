# -*- coding: utf-8 -*-
import tushare as ts
import numpy as np
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
        # print i
        # print i[-1].values
        data.append(i[-1].values)

    UP = 1
    DOWN = -1
    extended_list = list()
    result_list = list()
    for d in range(len(data)):
        if d>1:
            combined = np.append(data[d],data[d-1])
            combined = np.append(combined,data[d-2])
            extended_list.append(combined)
        else:
            combined = np.append(data[d],data[d])
            combined = np.append(combined,data[d])
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
# for e in extended_list:
#     print e
from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_blobs
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

extended_list, result_list = get_data_and_label('510300', '2010-06-23', '2016-07-30')
    # e = ts.get_hist_data('000002',start='2014-06-23',end='2017-07-30')
X, y = extended_list, result_list
X = StandardScaler().fit_transform(X)
# data set

test_list, test_label_list = get_data_and_label('510300', '2016-08-01', '2018-02-30')
test_list = StandardScaler().fit_transform(test_list)
    # e = ts.get_hist_data('000002',start='2014-06-23',end='2017-07-30')
# X, y = test_list, test_label_list
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier
from plot_report import main_plot
# fit a k-nearest neighbor model to the data
model = KNeighborsClassifier()
model.fit(X, y)
# clf = DecisionTreeClassifier(max_depth=None, min_samples_split=2,random_state = 0)
# scores = cross_val_score(clf, X, y)
# print "decision tree : ", scores.mean()
test_result = model.predict(test_list)
print ("KNeighborsClassifier on test: ", classification_report(test_label_list,test_result))
# score
# num_trees = 460
# clf = RandomForestClassifier(n_estimators=num_trees, max_depth=None,min_samples_split = 2, random_state = 0,max_features='sqrt', n_jobs=4)
# # 定义一个随机森林分类器
# scores = cross_val_score(clf, X, y)
# print "random forest : ", scores.mean()

# 这里是随机森林训练器的模型精确度得分
from sklearn import svm
clf = svm.SVC(degree=1)  # class
clf.fit(X, y)  # training the svc model

# clf = ExtraTreesClassifier(n_estimators=num_trees, max_depth=None,min_samples_split = 2, random_state = 0)

scores = cross_val_score(clf, X, y)
print ("svm : ", scores.mean())
test_result = clf.predict(test_list)
print ("svm on test: \r\n", classification_report(test_label_list,test_result))

# model = gradient_boosting_classifier(X,y,6000)
# test_result = model.predict(test_list)
# report = classification_report(test_label_list,test_result)
#
# print "gradient_boosting_classifier on test: \r\n", classification_report(test_label_list,test_result)
for i in range(1400,1460):
    print('ploting '+ str(i)+ " tree forest...")
    model = gradient_boosting_classifier(X, y, i)
    test_result = model.predict(test_list)
    report_str = str(classification_report(test_label_list, test_result))
    main_plot(report_str, './pics/'+ str(i) + 'tree.png')