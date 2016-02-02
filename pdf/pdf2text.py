# -*- coding: utf-8
from utils import pdftohtml, pdftohtmlDirectory, htmltotext, saveText, extractTitle, extractKeywords
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == '__main__':
    print(os.getcwd())

    # 处理单个pdf
    # 存放需要处理的单个pdf路径
    # filepath = 'Sample/P13.pdf'
    # htmlpathList = []
    # pdftohtml(filepath, htmlpathList)
    # for htmlpath in htmlpathList:
    #     print htmlpath
    #     saveText(htmltotext(htmlpath), htmlpath)

    # 处理目录
    conference_name = 'sigir'
    # 存放需要处理的pdf的目录路径
    pdfDirectoryPath = '/home/memray/Data/acm/pdf/'+conference_name+os.path.sep
    htmlDirectoryPath = '/home/memray/Data/acm/html/'+conference_name+os.path.sep
    textDirectoryPath = '/home/memray/Data/acm/text/'+conference_name+os.path.sep
    if not os.path.exists(pdfDirectoryPath):
        os.makedirs(pdfDirectoryPath)
    if not os.path.exists(htmlDirectoryPath):
        os.makedirs(htmlDirectoryPath)
    if not os.path.exists(textDirectoryPath):
        os.makedirs(textDirectoryPath)


    htmlpathList = []
    print '--------------start to handle------------'
    # Firstly, process pdf to html, the htmlpathList contains the htmls path and should be returned
    htmlpathList = pdftohtmlDirectory(pdfDirectoryPath, htmlDirectoryPath)
    print '--------------save all text--------------'
    # Secondly, for each processed html, convert to well-formatted txt
    for htmlpath in htmlpathList:
        article_id = htmlpath[htmlpath.rfind(os.path.sep)+1:-5]
        print(article_id)
        print(htmlpath)
        try:
            # extract text from layout text
            article_block,page_content_other = htmltotext(htmlpath)
            # save the converted text to file
            saveText(textDirectoryPath, article_block, article_id)
        except:
            print("ERROR HERE!!!")

    # print '--------------extract title and keywords--------------'
    # count = 0
    # for htmlpath in htmlpathList:
    #     count = count + 1
    #     print(count)
    #     if(count < 22):
    #         continue
    #     print(htmlpath)
    #     try:
    #         article_block,page_content_other = htmltotext(htmlpath)
    #         #extractTitle(page_content_other)
    #         extractKeywords(article_block)
    #     except Exception as e:
    #         print(e)
    #     pass