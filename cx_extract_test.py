from wordNet import raw_html_download

html_url = "http://math.ucr.edu/home/baez/physics/General/BlueSky/blue_sky.html"
html_url = "http://math.ucr.edu/home/baez/physics/index.html"
html_url = "https://www.bing.com/search?q=why+is+the+sky+blue&qs=n&form=QBRE&sp=-1&pq=why+is+the+sky+blue&sc=0-0&sk=&cvid=A6C6BEBF85474D739301203B984BCB39"
html_url = 'http://www.sciencemadesimple.com/sky_blue.html'

raw_html_download(html_url, "test.html")
from CxExtractor import CxExtractor
cx = CxExtractor(threshold=186)
html = cx.getHtml(html_url)
# html = cx.readHtml("test.html",'utf-8')
content = cx.filter_tags(html)
text = cx.getText(content)
textfile = open("./text/new_text.txt",'w')
textfile.write(text)
textfile.close()
from OpenAnswer import getRelatedSentencesListFromWeb
sent_list = getRelatedSentencesListFromWeb("who is the father of USA")
print(sent_list)