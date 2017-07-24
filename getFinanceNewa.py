from pyquery import PyQuery as pq
import sys
def get_urls(max_page):

    # start_url = 'http://news.cnstock.com/news/sns_yw/'
    start_url = 'http://ggjd.cnstock.com/gglist/search/ggkx'
    urls = []

    for i in range(1, max_page + 1):

        spec_url = start_url + str(i) if i > 1 else start_url + 'index.html'

        source = pq(spec_url)

        urls += [item.attr('href') for item in source('.new-list li a').items()]

    return urls

def get_news(url):

    source = pq(url)

    title = source('h1.title').text()

    date = source('span.timer').text()

    content = source('#qmt_content_div.content').text()

    if content:

        return {'URL': url, 'Title': title, 'Date': date, 'Content': content}

def save_txt(res):
    import datetime
    import codecs
    reload(sys)

    sys.setdefaultencoding('utf-8')

    news_date = datetime.datetime.strptime(res['Date'],'%Y-%m-%d %H:%M:%S').strftime('%Y%m%d')

    f_name = news_date + '_' + res['Title']
    print 'will create file: ', f_name
    with codecs.open('./test/%s.txt'%f_name, 'w+', encoding='utf-8') as f:
        f.write('source:' + res['URL'] + '\n')

        f.write('title:' + res['Title'] + '\n')

        f.write('date:' + res['Date'] + '\n')

        f.write('content:' + res['Content'] + '\n')
        f.close()



url_list = get_urls(20)
for url in url_list:
    news = get_news(url)
    if news:
        save_txt(news)