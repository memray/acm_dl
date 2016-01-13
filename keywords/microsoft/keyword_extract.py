__author__ = 'Memray'
from util.mysql_api import *
import sys
import traceback
"""
extract keywords from acm database
"""

host = '127.0.0.1:3306'
database = 'acm'
user = 'root'
password = '123456'
if __name__ == '__main__':
    conn = Connection(host, database, user, password)
    records = conn.query("SELECT keywords FROM keywords")

    count = 0
    keyword_set = set()
    for record in records:
        try:
            # print(record['keywords'])
            if record['keywords'] is None:
                continue
            # print(record)
            count += 1
            if count % 10000 == 0:
                print(count)
            keywords = str(record['keywords']).encode('utf-8','ignore').split(';;')
            for keyword in keywords:
                keyword_set.add(keyword)
        except Exception:
            sys.exc_clear()
    print(len(keyword_set))
    output_file = open('H:\\Dropbox\\PhD@Pittsburgh\\1.Researh\NSF\\20151115_QikaiCode\\keyword_data\\acm_keyword.txt','w')
    for keyword in keyword_set:
        print(str(keyword))
        output_file.write(str(keyword).encode('utf-8')+'\n')
    output_file.close()
