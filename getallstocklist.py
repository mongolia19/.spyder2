# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib2

# request = urllib2.Request('http://quote.eastmoney.com/stocklist.html')
# response = urllib2.urlopen(request)
# content = response.read().decode("gbk")
# url = 'http://quote.eastmoney.com/stocklist.html'
# headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
# request = urllib2.Request(url, headers)
# try:
#     print 'opening url'
#     urllib2.urlopen(url)
# except urllib2.URLError, e:
#     if hasattr(e,"code"):
#         print "fetch error reason",e.reason
# import re
# print 'will find pattern'
# pattern = re.compile('<li><a.*?href=.*?html">(.*?)(.∗?).*?</li>',re.S)
# items = re.findall(pattern,content)
# print 'write to file'
# f = open('stocklist.txt', 'w')
# for item in items:
#     f.write(item[1] + ',' + item[0] + '\n')
# f.close()
import tushare as ts
stock_info=ts.get_stock_basics()
def get_all_stock_id():
    #获取所有股票代码
    f = open('stocklist.txt', 'w')
    # for item in items:
    #     f.write(item[1] + ',' + item[0] + '\n')
    print len(stock_info.index)
    for i in stock_info.name:
        print i
        f.write(i + '\r\n')
    f.close()

get_all_stock_id()