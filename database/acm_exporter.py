__author__ = 'Memray'
# -*- coding: utf-8 -*-

import sys;
import os;
import json;
import pymysql



if __name__ == '__main__':
    output_file = open('../data/keyword_extract/acm_computer_science.txt','w')

    # if(not os.path.exists(output_file)):
    #     os.makedirs(output_file)

    conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="123456", db="cs_academy")

    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = 'SELECT p.id AS id, p.title AS title, p.date AS date, p.doi AS doi, p.isbn AS isbn, p.categories AS category, k.keywords AS keyword ' \
          'FROM _acm_paper_tsinghua AS p, _acm_keywords AS k ' \
          'WHERE p.id=k.id ' \
          'AND k.keywords IS NOT NULL ' \
          'AND k.keywords <> \'\''

    cur.execute(sql)
    print(cur.description)

    # print(len(articles))
    for doc in cur:
        print(doc)
        # print(json.dumps(doc))
        output_file.write(json.dumps(doc).replace(';;',';')+'\n')

    output_file.close()