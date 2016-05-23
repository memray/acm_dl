# -*- coding: utf-8 -*-
__author__ = 'Memray'

import numpy
from main import *
from sets import Set

TESTING_LINK_PATH = r'../../data/knowledge_predicting/testing.link'
TESTING_SVM_PATH = r'../../data/knowledge_predicting/testing.lsvm'
CHAPTER_GRAPH_PATH = r'../../data/knowledge_predicting/testing_chapter_graph.mat'
if __name__ == '__main__':
    load_documents(CORPUS_IR_TEXTBOOK)
    for file_count in range(1,6):
        book_name = book_names[file_count-1]

        document_list = book_document_dict[book_name].values()
        document_list = sorted(document_list, key=lambda d: d.number)

        graph_file = open(CHAPTER_GRAPH_PATH+str(file_count), 'r')
        lines = graph_file.readlines()
        chapter_number = len(lines)
        print(book_name+':'+str(chapter_number))

        graph_matrix = numpy.zeros((chapter_number, chapter_number))

        for i in range(len(lines)):
            ps = lines[i].split(',')
            # print(len(ps))
            for j in range(len(ps)):
                graph_matrix[i,j]=float(ps[j])
                # print('{0},{1}\t:\t{2}'.format(i,j,graph_matrix[i,j]))

        # predict all the section/subsection
        remaining = Set()
        for i in range(1, chapter_number):
            remaining.add(i)

        current_node = 0
        queue = [0]

        while len(remaining) > 0:
            max = -sys.maxint
            max_node = -1
            for i in remaining:
                if graph_matrix[i,current_node] > max:
                    max = graph_matrix[i,current_node]
                    max_node = i
            queue.append(max_node)
            remaining.remove(max_node)

        predict_section_seq = []
        for i in queue:
            predict_section_seq.append(document_list[i].id)

        print('All sections')
        print('->'.join(predict_section_seq))

        # predict chapters only
        remaining = Set()
        for i in range(1, chapter_number):
            if document_list[i].subsection==None:
                remaining.add(i)

        current_node = 0
        queue = [0]

        while len(remaining) > 0:
            max = -sys.maxint
            max_node = -1
            for i in remaining:
                if graph_matrix[i,current_node] > max:
                    max = graph_matrix[i,current_node]
                    max_node = i
            queue.append(max_node)
            remaining.remove(max_node)

        predict_section_seq = []
        for i in queue:
            predict_section_seq.append(document_list[i].id)

        print('Chapters only')
        print('->'.join(predict_section_seq))
        print('')
