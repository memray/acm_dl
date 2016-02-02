__author__ = 'Memray'
import urllib2
import os
from time import sleep
import random
# from util.mysql_api import *

'''
Code for crawling PDF files from ACM digital library. The id of article is needed.
'''
def download(id):
    # url="http://dl.acm.org/ft_gateway.cfm?id="+id+"&ftid=1610216&dwn=1&CFID=555984911&CFTOKEN=15328294"
    url="http://dl.acm.org/ft_gateway.cfm?id="+id+"&type=pdf"
    print(url)
    opener = urllib2.build_opener()
    opener.addheaders = [
                ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                               'Windows NT 5.2; .NET CLR 1.1.4322)'))
            ]
    response=opener.open(url)
    f_name = pdf_dir+id+'.pdf'
    f = open(f_name, 'wb')
    f.write(response.read())
    f.close()
    print('{0} downloaded successfully : {1}'.format(id, f_name))



pdf_dir = ""
conference_name = "uist"

if __name__ == "__main__":
    project_root_dir = os.path.dirname(__file__)
    project_root_dir = project_root_dir[:project_root_dir.rfind('/')]

    # check whether the given path exists
    pdf_dir = '/home/memray/Data/acm/pdf/'+conference_name+'/'
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)


    # db=Connection(host='127.0.0.1',database='acm',user='root',password='123456')
    # for row in db.query('select * from acm_article limit 0,100'):
    id_file = open(os.path.join(project_root_dir,'data/paperurls/'+conference_name+'.txt'),'r')
    fail_file = open(os.path.join(project_root_dir,'data/paperurls/fail.txt'),'w+')
    count = 0

    while True:
        count+=1
        id = id_file.readline().strip()
        if((id is None) or (len(id)==0)):
            break

        # check whether this pdf has been downloaded
        f_name = pdf_dir+id+'.pdf'
        if os.path.exists(f_name):
            print('{0}:{1} already exists'.format(count,id))
            continue
        else:
            print('{0}:{1} downloading...'.format(count,id))

        delay = random.gauss(3, 4)
        if delay <0:
            delay=0
        print('sleep for '+str(delay)+'s')
        sleep(delay)

        try:
            download(id)
        except:
            fail_file.write(id+'\n')

        if(count % 20 == 0):
            delay = random.gauss(120, 4)
            if delay <0:
                delay=0
            print('Long sleep for '+str(delay)+'s')
            sleep(delay)
    id_file.close()
    fail_file.close()