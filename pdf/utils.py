# coding:utf-8
from layout import Page, Word
from layout import get_page_objs, words_to_lines
import os, sys

reload(sys)
sys.setdefaultencoding('utf-8')

exe_path = os.getcwd() + "\\poppler-0.36\\bin\\pdftotext.exe"


# 存储处理后的txt路径
# base_path = 'C:/Users/Roger/Desktop/Memary/txtData/'

# 利用pdftotext.exe转化为html，读取单个pdf
def pdftohtml(filePath, htmlpathList):
    if not str(filePath).lower().endswith('pdf'):
        return
    cmdStr = exe_path + " -bbox " + filePath
    print(cmdStr)
    dirpath = os.path.dirname(filePath)
    basename = os.path.basename(filePath)
    filename = basename[:len(basename) - 4]
    htmlpath = dirpath + '\\' + filename + '.html'
    if not os.path.exists(htmlpath):
        os.system(cmdStr)
    # print htmlpath
    htmlpathList.append(htmlpath)


# 利用pdftotext.exe转化为html，读取一个目录
def pdftohtmlDirectory(directoryPath, htmlpathList):
    fileNameList = os.listdir(directoryPath)
    fileList = []
    print 'fileNameList:', fileNameList
    for filename in fileNameList:
        fileAbsPath = directoryPath + '\\' + filename
        if os.path.isfile(fileAbsPath):
            fileList.append(fileAbsPath)
        elif os.path.isdir(fileAbsPath):
            # 路径是目录，需要继续读取
            fileList.extend(pdftohtmlDirectory(fileAbsPath, htmlpathList))
    for fileAbsPath in fileList:
        # print fileAbsPath
        pdftohtml(fileAbsPath, htmlpathList)


# 根据pdftohtml转化的坐标信息合并文本块， 按照中间、左栏、右栏以及从前到后的顺序合并成段落信息
def htmltotext(htmlpath):
    page_objs = get_page_objs(htmlpath)
    # 存放一篇pdf所有区块，即左边和右边两种区块
    article_block = []
    for page_obj_with_words in page_objs:
        # for word in page_obj_with_words.sub_obj_list:
        #     print word
        page_content_other = []
        page_content_left = []
        page_content_right = []
        line_obj_list = words_to_lines(page_obj_with_words)
        for line in line_obj_list:
            if line.xmin > 50 and line.xmin < 90 and line.xmax < 300:
                page_content_left.append(line)
            elif line.xmin > 315 and line.xmin < 334 and line.xmax < 560:
                page_content_right.append(line)
            else:
                page_content_other.append(line)

                # print line
        article_block.extend(page_content_left)
        article_block.extend(page_content_right)
    return article_block, page_content_other


# 存储转换后的内容article
def saveText(article_block, htmlpath):
    # saveName = os.path.basename(htmlpath) + '.txt'
    # fp = open(base_path + saveName, 'w')
    savePath = htmlpath[:len(htmlpath) - 5] + '.txt'
    fp = open(savePath, 'w')
    for line in article_block:
        fp.write(line.text)
        fp.write('\n')
    fp.flush()
    fp.close()
    print '[one text has been saved]'


# 提取title
def extractTitle(article_block):
    print(article_block[1])


# 提取Keywords
def extractKeywords(article_block):
    for block in article_block:
        if str(block.text).startswith("Keywords"):
            # 处理keyword和title出现在一行的情况
            keywords = ''
            if (len(block.text) > 10):
                keywords = block.text[9:]
            start_index = article_block.index(block)
            i = 1
            print('candidate0:' + str(block))
            while ((start_index + i < len(article_block)) & (i < 4)):
                current = article_block[start_index + i]
                last = article_block[start_index + i - 1]
                print("candidate" + str(i) + ':' + str(current))
                if (current.text.startswith('1.') | current.text.lower().startswith(
                        'categories') | current.text.lower().startswith('abstract') | current.text.lower().startswith(
                        'motivation') | current.text.lower().startswith('reference') | current.text.lower().startswith('permission')):
                    break
                if(current.ymin-last.ymax>10):
                    break
                if (keywords.endswith('-')):
                    keywords = (keywords[:-1] + current.text)
                else:
                    keywords = (keywords[:] + ' ' + current.text)
                i = i + 1

            print('\nKeyword:' + str(keywords).strip().lower() + '\n\n')
            return str(keywords).strip().lower()
