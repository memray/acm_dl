__author__ = 'Memray'
from bs4 import BeautifulSoup
import urllib2
#url="http://dl.acm.org/results.cfm?h=1&cfid=551577098&cftoken=74539063"
url="http://dl.acm.org/results.cfm?h=1&source_query=Owner:ACM&&cfid=551577098&cftoken=74539063"
opener = urllib2.build_opener()
opener.addheaders = [
            ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                           'Windows NT 5.2; .NET CLR 1.1.4322)'))
        ]
response=opener.open(url)
html = BeautifulSoup (''.join(response.readlines()))
html.find_all("div",class_="abstract2")