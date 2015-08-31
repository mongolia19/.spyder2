__author__ = 'idroid'
from pyh import *
page = PyH('My wonderful PyH page')
# page.addCSS('myStylesheet1.css', 'myStylesheet2.css')
# page.addJS('myJavascript1.js', 'myJavascript2.js')
page<<(h1(''))<<a('a hyper link', href ='http://baidu.com')
page<<h2('my small title', c1 = 'center')
page<<img(src = 'https://ss0.baidu.com/73x1bjeh1BF3odCf/it/u=138126325,1485620701&fm=96&s=7FAB2EC3909A35D01E299C1A030010D2')
# page << div(cl='myCSSclass1 myCSSclass2', id='myDiv1') << p(id='myP1', 'I love PyH!')
# mydiv2 = page << div(id='myDiv2')
# mydiv2 << h2('A smaller title') + p('Followed by a paragraph.')
# page << div(id='myDiv3')
# page.myDiv3.attributes['cl'] = 'myCSSclass3'
# page.myDiv3 << p('Another paragraph')
page.printOut('./testHtml.html')