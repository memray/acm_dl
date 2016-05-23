# -*- coding: utf-8 -*-
__author__ = 'Memray'
import sys
import os
from gensim import corpora, models, similarities
reload(sys)
import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


from nltk.stem.porter import *

CORPUS_IR_TEXTBOOK = r'../../data/knowledge_predicting/ir_textbook.txt'
CORPUS_ALGEBRA_TEXTBOOK = r'../../data/knowledge_predicting/algebra_textbook.txt'
STOPWORD_PATH = r'../../data/stopword/stopword_en.txt'

PREREQUISITE_LINK_PATH = r'../../data/knowledge_predicting/ir.link'
REPRESENTATION_SVM_PATH = r'../../data/knowledge_predicting/'
DICTIONARY_PATH = r'../../data/knowledge_predicting/dict.txt'


# book_document_dict[document.bookname][doc_id] = document
book_document_dict = {}
# a list structure contains book documents(leaf document, sections or subsections)
book_document_list = []
book_names = ['iir','mir','foa','irv','issr']

class Document:
    def __init__(self, number, id, content):
        self.number = number
        self.id = id
        self.content = content
        strs = id.split('_')
        self.bookname = strs[0]
        self.section = None
        self.subsection = None
        self.subsubsection = None
        if(len(strs) > 1):
            self.section = int(strs[1])
        if(len(strs) > 2):
            self.subsection = int(strs[2])
        if(len(strs) > 3):
            self.subsubsection = int(strs[3])




def load_stopword(path):
    stop_word = []
    try:
        stopword_file = open(path, 'r')
        stop_word = [line.strip() for line in stopword_file]
    except:
        print('Error occurs when loading STOPWORD')
    return stop_word




def load_documents(corpus_path):
    '''
    Load corpus and convert to Dictionary and Corpus of gensim
    :param corpus_path
    :param num_feature, indicate how many terms you wanna retain, not useful now
    :return:
    '''
    corpus_file = open(corpus_path, 'r')
    doc_no = 0
    for line in corpus_file:
        doc_id = line[0: line.index('\t')]
        # print(doc_id)
        content = line[line.index('\t')+1:].lower()
        document = Document(doc_no, doc_id, content)
        # print(document.number)
        if(not book_document_dict.has_key(document.bookname)):
            book_document_dict[document.bookname]={}
        book_document_dict[document.bookname][doc_id]=document
        book_document_list.append(document)
        doc_no += 1
    return book_document_dict

def build_prerequisite(doc_list, output_path, method='window', window_size=1):
    output = open(output_path, 'w')

    count = 0
    for doc in doc_list:
        doc.number = count
        count += 1

    if (method=='fulllink'):
        for doc1 in doc_list:
            for doc2 in doc_list:
                if (doc1.number < doc2.number) and (doc1.bookname==doc2.bookname):
                    output.write('{0} {1}\n'.format(doc1.number, doc2.number))
    elif (method=='window'):
        for doc1 in doc_list:
            for doc2 in doc_list:
                if ((doc1.number < doc2.number) and (doc1.bookname==doc2.bookname) and (doc2.section-doc1.section<=window_size)):
                    output.write('{0} {1}\n'.format(doc1.number, doc2.number))
    output.close()

def build_representation():
    '''
    Load corpus and convert to Dictionary and Corpus of gensim
    :param corpus_path
    :param num_feature, indicate how many terms you wanna retain, not useful now
    :return:
    '''

    # tokenize and clean. Split non-word&number: re.sub(r'\W+|\d+', '', word.decode('utf-8')). Keep all words:r'\d+'
    for document in book_document_list:
        document.tokenlist = [re.sub(r'\W+|\d+', '', word.decode('utf-8')) for word in document.content.split()]

    # remove stop words and short tokens
    stoplist = load_stopword(STOPWORD_PATH)
    for document in book_document_list:
        document.tokenlist = [token for token in document.tokenlist if ((not token.strip()=='') and (not token in stoplist))]

    # remove words that appear only once
    from collections import defaultdict
    frequency = defaultdict(int)
    for document in book_document_list:
        for token in document.tokenlist:
            frequency[token] += 1

    for document in book_document_list:
        document.tokenlist = [token for token in document.tokenlist if (frequency[token] > 1)]

    # stemming, experiment shows that stemming works nothing...
    # if (stemming):
    #     stemmer = PorterStemmer()
    #     texts = [[ stemmer.stem(token) for token in text] for text in texts]

    texts = [[token for token in document.tokenlist] for document in book_document_list]
    dictionary = corpora.Dictionary(texts)
    # corpus = [dictionary.doc2bow(text) for text in texts]
    for document in book_document_list:
        document.bow = dictionary.doc2bow(document.tokenlist)

    print(len(dictionary))

    return dictionary

def convert_data():
    '''
    read and write the data after converting title from 'foa-0176  8.3' to 'foa_8_3'
    :return:
    '''
    corpus_file = open(CORPUS_IR_TEXTBOOK, 'r')
    output_file = open(r'../../data/knowledge_predicting/ir_textbook_good.txt', 'w')
    for line in corpus_file:
        if(line.startswith('irv') or line.startswith('iir')):
            output_file.write(line)
            continue
        doc_id = line[0: line.index('-')]
        doc_section = line[line.index('\t')+1: line.index(' ')].replace('.','_')
        new_doc_id = doc_id + '_' +doc_section
        # print(new_doc_id)
        document = line[line.index(' ')+1:].strip()+'\n'
        output_file.write(new_doc_id+'\t'+document)


def export_representation():
    '''
    export the data to libsvm format
    :return:
    '''

    # vocab.filter_extremes(no_below=3, no_above=0.4)
    # dictionary.save(DICTIONARY_PATH)
    dictionary.save_as_text(DICTIONARY_PATH)

    count = 0
    # outer loop specify which book is excluded for training
    for testing_book in book_names:
        count += 1
        # 1. export the testing data (prerequisite links and svm representation)
        testing_data = [document.bow for document in book_document_list if document.bookname==testing_book]
        testing_doc = [document for document in book_document_list if document.bookname==testing_book]
        build_prerequisite(testing_doc, REPRESENTATION_SVM_PATH+'testing'+'.link'+str(count) , 'window', 1)
        write_SVM_to_file(testing_data, REPRESENTATION_SVM_PATH+'testing'+'.lsvm'+str(count))

        # 2. export the training date
        training_data = [document.bow for document in book_document_list if not document.bookname==testing_book]
        training_doc = [document for document in book_document_list if not document.bookname==testing_book]
        build_prerequisite(training_doc, REPRESENTATION_SVM_PATH+'training'+'.link'+str(count), 'window', 1)
        write_SVM_to_file(training_data, REPRESENTATION_SVM_PATH+'training'+'.lsvm'+str(count))

def write_SVM_to_file(data, filepath):
    corpora.SvmLightCorpus.serialize(filepath+'.tmp', data)

    file = open(filepath+'.tmp', 'r')
    lines = []
    doc_no = 0
    for line in file:
        lines.append(str(doc_no)+line[line.index(' '):])
        # print(str(doc_no)+line[line.index(' '):])
        doc_no+=1
    file.close()
    os.remove(filepath+'.tmp')
    os.remove(filepath+'.tmp.index')

    file = open(filepath, 'w')
    for line in lines:
        file.write(line)
    file.close()


if __name__ == '__main__':
    load_documents(CORPUS_IR_TEXTBOOK)

    dictionary = build_representation()
    export_representation()