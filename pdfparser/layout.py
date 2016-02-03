# -*- coding: utf-8
from bs4 import BeautifulSoup
import collections
'''
Used for extracting the layout of pdf text, and organized text blocks in a logical way
'''
class Page(object):
    def __init__(self, height, width):
        self.height = float(height)
        self.width = float(width)
        self.sub_obj_list = []

    def _set_sub_obj_list(self, sub_obj_list):
        self.sub_obj_list = sub_obj_list
    
    def _add_sub_obj_to_list(self, sub_obj):
        self.sub_obj_list.append(sub_obj)

    def __str__(self):
        return "<page height=" + str(self.height) + " width=" + str(self.width) + ">" + " ".join([obj for obj in self.sub_obj_list]) + "</page>"

    def __repr__(self):
        return "<page height=" + str(self.height) + " width=" + str(self.width) + ">" + " ".join([obj for obj in self.sub_obj_list]) + "</page>" 


class Word(object):
    def __init__(self, xmin, ymin, xmax, ymax, text):
        self.xmin, self.ymin, self.xmax, self.ymax = float(xmin), float(ymin), float(xmax), float(ymax)
        self.text = text

    def __str__(self):
        return "<word ymin=" + str(self.ymin) + " ymax=" + str(self.ymax) + " xmin=" + str(self.xmin) + " xmax=" + str(self.xmax) + ">" + self.text + "</word>"

    def __repr__(self):
        return "<word ymin=" + str(self.ymin) + " ymax=" + str(self.ymax) + " xmin=" + str(self.xmin) + " xmax=" + str(self.xmax) + ">" + self.text + "</word>"


class Line(object):
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin, self.ymin, self.xmax, self.ymax = float(xmin), float(ymin), float(xmax), float(ymax)
        self.text = ""
        self.sub_obj_list = []

    def _add_text(self, text):
        if self.text == "":
            self.text = text
        else:
            self.text += " " + text

    def _set_sub_obj_list(self, sub_obj_list):
        self.sub_obj_list = sub_obj_list

    def _add_sub_obj_to_list(self, sub_obj):
        self.sub_obj_list.append(sub_obj)

    def __str__(self):
        return "<line ymin=" + str(self.ymin) + " ymax=" + str(self.ymax) + " xmin=" + str(self.xmin) + " xmax=" + str(self.xmax) + ">" + " ".join([obj.text for obj in self.sub_obj_list]) + "</line>"

    def __repr__(self):
        return "<line ymin=" + str(self.ymin) + " ymax=" + str(self.ymax) + " xmin=" + str(self.xmin) + " xmax=" + str(self.xmax) + ">" + " ".join([obj.text for obj in self.sub_obj_list]) + "</line>" 


# 获取页面中所有page对象，page对象包含words对象列表
def get_page_objs(tmp_html_path):
    soup = BeautifulSoup(open(tmp_html_path), "html.parser")
    page_objs = []
    pages = soup.doc.find_all('page')
    for page in pages:
        # 创建Page对象
        cur_page_obj = Page(page['height'], page['width'])
        page_objs.append(cur_page_obj)
        # 为Page对象添加word对象
        words = page.find_all('word')
        [cur_page_obj._add_sub_obj_to_list(Word(word['xmin'], word['ymin'], word['xmax'], word['ymax'], word.string)) for word in words]
    return page_objs


def words_to_lines(page_obj_with_words):
    line_obj_list = []
    words_in_page = page_obj_with_words.sub_obj_list
    if len(words_in_page) > 0:
        if len(words_in_page) == 1:
            new_line = Line(words_in_page[0].xmin, words_in_page[0].ymin, words_in_page[0].xmax, words_in_page[0].ymax)
            new_line._add_text(words_in_page[0].text)
            new_line._add_sub_obj_to_list(words_in_page[0])
            line_obj_list.append(new_line)
        else:
            start_index = 0;
            start_word = words_in_page[0]
            for i in range(1, len(words_in_page)):
                next_word = words_in_page[i]
                # 如果不是最后一个词
                if i != len(words_in_page)-1:
                    if next_word.ymin != start_word.ymin:
                        new_line_list = deep_words_to_lines(words_in_page[start_index:i])
                        line_obj_list.extend(new_line_list)

                        # new_line = merge_word_to_line(words_in_page[start_index:i])
                        # # print new_line
                        # line_obj_list.append(new_line)
                        start_index = i
                        start_word = words_in_page[start_index]
                else: #最后一个词
                    if next_word.ymin != start_word.ymin:
                        new_line_list = deep_words_to_lines(words_in_page[start_index:i])
                        line_obj_list.extend(new_line_list)

                        # new_line = merge_word_to_line(words_in_page[start_index:i])
                        # line_obj_list.append(new_line)
                        new_line = Line(words_in_page[i].xmin, words_in_page[i].ymin, words_in_page[i].xmax, words_in_page[i].ymax)
                        new_line._add_text(words_in_page[i].text)
                        new_line._add_sub_obj_to_list(words_in_page[i])
                        line_obj_list.append(new_line)
    return line_obj_list


# 为了把分属不同区块但是ymin相等的两行区分开，规则就是找寻break_index(词之间的突变点作为这两行的区分点)
# 绝大部分情况下没什么用
def deep_words_to_lines(words_equal_ymin):
    # print merge_word_to_line(words_equal_ymin)
    lines = []
    start_word = words_equal_ymin[0]
    break_index = 0
    for i in range(1,len(words_equal_ymin)):
        next_word = words_equal_ymin[i]
        if next_word.xmin - start_word.xmax > 20:
            # print break_index
            break_index = i
            break
        else:
            start_word = words_equal_ymin[i]
    if break_index > 0:
        lines.append(merge_word_to_line(words_equal_ymin[:break_index]))
        lines.append(merge_word_to_line(words_equal_ymin[break_index:]))
    else:
        lines.append(merge_word_to_line(words_equal_ymin))
    # print lines, '-------------'
    return lines

def merge_word_to_line(words):
    assert len(words) != 0
    # print words[0]
    new_line = Line(words[0].xmin, words[0].ymin, words[0].xmax, words[0].ymax)
    new_line._add_text(words[0].text)
    new_line._add_sub_obj_to_list(words[0])
    if len(words) != 1:
        for word in words[1:]:
            new_line._add_text(word.text)
            new_line._add_sub_obj_to_list(word)
            new_line.xmin = min(new_line.xmin, word.xmin)
            new_line.ymin = min(new_line.ymin, word.ymin)
            new_line.xmax = max(new_line.xmax, word.xmax)
            new_line.ymax = max(new_line.ymax, word.ymax)
    # print new_line
    return new_line