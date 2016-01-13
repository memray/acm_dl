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
    # 存放需要处理的pdf的目录路径
    directoryPath = 'H:\\acm_dl\\pdf\\ir\\'
    htmlpathList = []
    print '--------------start to handle------------'
    pdftohtmlDirectory(directoryPath, htmlpathList)
    print '--------------save all text--------------'
    for htmlpath in htmlpathList:
        print htmlpath
        try:
            article_block,page_content_other = htmltotext(htmlpath)
            saveText(article_block, htmlpath)
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