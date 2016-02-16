__author__ = 'Memray'
# -*- coding: utf-8 -*-

import sys;
import os;
import pymysql;
from  MySQLConnector import *;

# Mysql Singleton CLass with pymysql
# class mysql_test(object):



if __name__ == '__main__':
    conference_name = "JCDL"
    outputDirectory = 'H:/Dropbox/PhD@Pittsburgh/1.Researh/NSF/20160125_analyzer_v1/textbook_analyzer/data/acm_paper/'+conference_name+'/'
    if(not os.path.exists(outputDirectory)):
        os.makedirs(outputDirectory)

    conn = MySQLConnector("localhost", "root", "123456", "acm", True)
    sql = "SELECT article_id, Acm_Article_Title, Acm_Article_Abstract " \
          "FROM acm_article AS a,acm_conference_name AS c " \
          "WHERE a.Acm_Conference_id=c.acm_conference_id " \
          "AND c.acm_conference_name IN ('"+ conference_name + "');"
    articles = conn.queryrows(sql)
    # print(len(articles))
    for article in articles:
        file = open(outputDirectory+article[0]+'.txt', 'w')
        file.write(article[1]+'\n'+article[2])
        file.close()