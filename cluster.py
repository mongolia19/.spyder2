# -*- coding: utf-8 -*-
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn import cluster
import numpy

# final = open('c:/test/final.dat', 'r')
#
# data = [line.strip().split('\t') for line in final]
# feature = [[float(x) for x in row[3:]] for row in data]
feature = [[1,3,4],[5,5,5],[3,4,5],[0,7,8],[9,5,7]]
print type(feature)
# 调用kmeans类
def KMeans_cluster(cluster_num, data_list):
    feature = data_list
    clf = KMeans(n_clusters=cluster_num)
    s = clf.fit(feature)
    print 's is ', s
    # 9个中心
    print 'centers '
    print clf.cluster_centers_
    # 每个样本所属的簇
    # print clf.labels_
    # 用来评估簇的个数是否合适，距离越小说明簇分的越好，选取临界点的簇个数
    # print clf.inertia_
    # 进行预测
    # print clf.predict(feature)

    # 保存模型
    joblib.dump(clf, './km.pkl')
    # 载入保存的模型
    clf = joblib.load('./km.pkl')
    return clf
def DBSCAN_cluster(eps=.2, min_num=10):
    dbscan = cluster.DBSCAN(eps=eps,min_samples=min_num)
    return dbscan
from sklearn.cluster import AgglomerativeClustering
def AgglomerativeClustering_loc(cluster_num, x_input):
# for linkage in ('ward', 'average', 'complete'):
    clustering = AgglomerativeClustering(linkage='average', n_clusters = 10)
    # t0 = time()
    clustering.fit(x_input)
    return clustering
    # plot_clustering(X_red, X, clustering.labels_, "%s linkage" % linkage)
'''
#用来评估簇的个数是否合适，距离越小说明簇分的越好，选取临界点的簇个数
for i in range(5,30,1):
    clf = KMeans(n_clusters=i)
    s = clf.fit(feature)
    print i , clf.inertia_
'''