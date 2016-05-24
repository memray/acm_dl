__author__ = 'Memray'
# -*- coding: utf-8 -*-

import sys;
import os;
import json;
import pymysql



if __name__ == '__main__':
    output_file = open('data/keyword_extract/sci_scie_computer_science.txt','w')

    # if(not os.path.exists(output_file)):
    #     os.makedirs(output_file)

    conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="123456", db="cs_academy")

    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = 'SELECT * FROM sci_scie_computer_paper'

    cur.execute(sql)
    print(cur.description)

    # print(len(articles))
    for doc in cur:
        print(doc)
        # print(json.dumps(doc))
        output_file.write(json.dumps(doc)+'\n')

    output_file.close()