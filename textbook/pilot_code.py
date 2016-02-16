import math
from scipy import spatial

from textbook.metric.rank_metrics import ndcg_at_k

__author__ = 'Memray'

import logging
import re
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora, models, similarities
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

from nltk.stem.porter import *


STOPWORD_PATH = '../data/stopword/stopword_en.txt'
CORPUS_TERM_PATH = '/home/memray/Project/textbook_analyzer/data/corpus_textbook+sigir.txt'
CORPUS_PHRASED_PATH = '/home/memray/Project/textbook_analyzer/data/corpus_textbook+sigir_phrased.txt'
CORPUS_TERMPHRASED_PATH = '/home/memray/Project/textbook_analyzer/data/corpus_textbook+sigir_term_phrase.txt'

LDA_sigir_PATH = '/home/memray/Project/textbook_analyzer/data/lda/lda_textbook+sigir/'
LDA_single_book_PATH = '/home/memray/Project/textbook_analyzer/data/lda/books-lda-twobooks/'
LDA_pure_theta_PATH = '/home/memray/Project/textbook_analyzer/data/lda/lda_pure-textbook/'
LDA_sigir_period_PATH = '/home/memray/Project/textbook_analyzer/data/lda/books-lda+sigir-periods/'
LDA_pure_phrase_PATH = '/home/memray/Project/textbook_analyzer/data/lda/books-lda-phrases/'
LDA_sigir_citation_PATH = '/home/memray/Project/textbook_analyzer/data/lda/books-lda-citation/'
GROUNDTRUTH_PATH = '/home/memray/Project/textbook_analyzer/data/ir_groundtruth.txt'
groundtruth_dict = {}
doc_id2gensim_index = {}
gensim_index2doc_id = {}
corpus_index2doc_id = {}
dictionary = None
corpus = None

def load_stopword(path):
    stop_word = []
    try:
        stopword_file = open(path, 'r')
        stop_word = [line.strip() for line in stopword_file]
    except:
        print('Error occurs when loading STOPWORD')
    return stop_word


def load_documents(corpus_path, num_feature = None):
    '''
    Load corpus and convert to Dictionary and Corpus of gensim
    :param corpus_path:
    :return:
    '''
    global doc_id2gensim_index, gensim_index2doc_id, dictionary,corpus, groundtruth_dict
    corpus_file = open(corpus_path, 'r')
    doc_id2gensim_index = {} # dict, used for store the mapping pair of {doc_id, index}
    documents = []
    index = 0
    corpus_index = 0

    for line in corpus_file:
        doc_id = line[0: line.index('\t')]
        document = line[line.index('\t')+1:]

        corpus_index += 1
        corpus_index2doc_id[corpus_index] = doc_id

        #filter files we don't care, decrease the training time
        if((not doc_id.startswith('iir')) and (not doc_id.startswith('mir'))):
            continue

        doc_id2gensim_index[doc_id] = index
        gensim_index2doc_id[index] = doc_id
        index += 1
        documents.append(document.lower())

    # tokenize and clean. Split non-word: re.sub(r'\W*$', '', re.sub(r'^\W*', '', word))
    texts = [[re.sub(r'\W*$', '', re.sub(r'^\W*', '', word)).decode('utf-8') for word in document.lower().split()]
             for document in documents]
    # remove stop words and short tokens
    stoplist = load_stopword(STOPWORD_PATH)
    texts = [[token for token in text if (token not in stoplist) & (len(token)>1)]
             for text in texts]
    # remove words that appear only once
    from collections import defaultdict

    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[ token for token in text if (frequency[token] > 1)]
             for text in texts]

    # stemming
    # stemmer = PorterStemmer()
    # texts = [[ stemmer.stem(token) for token in text if (frequency[token] > 1)]
    #          for text in texts]

    # create dictionary
    dictionary = corpora.Dictionary(texts)

    # if not num_feature==None:
    #     '''
    #     filtered by Term Frequency
    #     '''
    #     # dictionary.filter_extremes(keep_n=num_feature)
    #     '''
    #     filtered by Inversed Document Frequency
    #     '''
    #     idfs = {}
    #     for df in dictionary.dfs.items():
    #         idf = math.log(len(texts)/(df[1]+1))
    #         idfs[df[0]]=idf
    #     idfs = sorted(idfs.items(),key=lambda tup: tup[1],reverse=True)
    #     keep_tokens_id = [token[0] for token in idfs[0:num_feature]]
    #     dictionary.filter_tokens(good_ids=keep_tokens_id)
    print(len(dictionary))
    corpus = [dictionary.doc2bow(text) for text in texts]

    return doc_id2gensim_index, dictionary, corpus

def Term_based_similarity(k, feature_number):
    '''
    calc the similarity based on purely term
    :return:
    '''
    global doc_id2gensim_index, gensim_index2doc_id, dictionary,corpus, groundtruth_dict
    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    corpus_tfidf = tfidf[corpus] # step 2 -- use the model to transform vectors
    index = similarities.MatrixSimilarity(corpus_tfidf) # step 3 -- transform corpus to TFIDF space and index it

    ndcg_total = 0
    query_number = 0

    '''
    Get the final similarity rank
    '''
    for id in doc_id2gensim_index:
        if (not id.startswith('iir')) or (not groundtruth_dict.has_key(id)):
            continue
        query_number += 1
        document = corpus[doc_id2gensim_index[id]]

        # print(docid2corpus_index[id])
        # print(document)

        # restore the document by dictionary.__getitem__()
        # for text_index in document:
        #     print(dictionary.__getitem__(text_index[0])+' ')

        query = document
        sims = index[query] # perform a similarity query against the corpus
        sims = sorted(enumerate(sims), key=lambda item: -item[1]) # print sorted (document number, similarity score) 2-tuples
        count = 0
        mapping_dict = groundtruth_dict[id]
        # print(mapping_dict)
        r_array = [] # array used as input of nDCG
        for entry in sims:
            if gensim_index2doc_id[entry[0]].startswith('mir'):
                count += 1
                if(count > 12):
                    break
                if mapping_dict.has_key(gensim_index2doc_id[entry[0]]):
                    r_array.append(mapping_dict[gensim_index2doc_id[entry[0]]])
                else:
                    r_array.append(0)
                # print(entry[0], corpus_index2docid[entry[0]], entry[1])
        ndcg = ndcg_at_k(r_array, k)
        # print(r_array)
        # print(ndcg)
        ndcg_total += ndcg
    print('#Feature={0}, Average nDCG@{1}:{2}'.format(feature_number,k, float(ndcg_total)/query_number))
    return float(ndcg_total)/query_number

def  TopicModel_based_similarity(lda_file_path, k, lambda_ratio):
    '''
    calc the similarity based on merging term and topic model
    :return:
    '''
    global doc_id2gensim_index, gensim_index2doc_id, dictionary,corpus, groundtruth_dict, corpus_index2doc_id
    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    corpus_tfidf = tfidf[corpus] # step 2 -- use the model to transform vectors
    matrix_similarity = similarities.MatrixSimilarity(corpus_tfidf) # step 3 -- transform corpus to TFIDF space and index it

    ndcg_total = 0
    query_number = 0

    '''
    Get the term_similarity
    '''
    print('Getting the term_similarity')
    term_similarity_dict = {}
    for doc_id in doc_id2gensim_index:
        if (not doc_id.startswith('iir')) or (not groundtruth_dict.has_key(doc_id)):
            continue
        query = corpus[doc_id2gensim_index[doc_id]]

        sims = matrix_similarity[query] # perform a similarity query against the corpus
        sims = sorted(enumerate(sims), key=lambda item: -item[1]) # print sorted (document number, similarity score) 2-tuples
        mir_sims = dict((gensim_index2doc_id[k], v) for k, v in [sim for sim in sims if gensim_index2doc_id[sim[0]].startswith('mir')])
        term_similarity_dict[doc_id] = mir_sims
    '''
    Get the topicmodel_similarity
    '''
    print('Getting the topicmodel_similarity')
    topicmodel_similarity_dict = {}
    lda_file = open(lda_file_path,'r')
    lines = lda_file.readlines()
    index_i = 0
    for line_i in lines:
        index_i += 1
        doc_id_i = corpus_index2doc_id[index_i]
        if not doc_id_i.startswith('iir'):
            continue
        # print(doc_id_i)
        dataSet_i = [float(i) for i in line_i.split('\t') if len(i.strip()) > 0]
        mir_sims = {}
        index_j = 0
        for line_j in lines:
            index_j += 1
            doc_id_j = corpus_index2doc_id[index_j]
            if not doc_id_j.startswith('mir'):
                continue
            # print(doc_id_j)
            dataSet_j = [float(j) for j in line_j.split('\t')  if len(j.strip()) > 0]
            cosine = 1 - spatial.distance.cosine(dataSet_i, dataSet_j)
            mir_sims[doc_id_j] = cosine
        topicmodel_similarity_dict[doc_id_i] = mir_sims
    '''
    Get the final similarity rank
    '''
    print('Getting the final similarity rank')
    query_number = 0
    for doc_id in doc_id2gensim_index:
        if (not doc_id.startswith('iir')) or (not groundtruth_dict.has_key(doc_id)):
            continue
        query_number += 1
        count = 0
        mapping_dict = groundtruth_dict[doc_id]

        weighted_similarities = {}
        for (doc_id_j,term_similarity) in term_similarity_dict[doc_id].items():
            if topicmodel_similarity_dict[doc_id].has_key(doc_id_j):
                weighted_similarities[doc_id_j] = term_similarity*lambda_ratio + topicmodel_similarity_dict[doc_id][doc_id_j]*(1-lambda_ratio)

        weighted_similarities = sorted(weighted_similarities.items(), key=lambda item: item[1],reverse=True)# print sorted (document number, similarity score) 2-tuples

        # print(mapping_dict)
        r_array = [] # array used as input of nDCG
        for entry in weighted_similarities:
            if entry[0].startswith('mir'):
                count += 1
                if(count > 12):
                    break
                if mapping_dict.has_key(entry[0]):
                    r_array.append(mapping_dict[entry[0]])
                else:
                    r_array.append(0)
                # print(entry[0], entry[0], entry[1])
        ndcg = ndcg_at_k(r_array, k)
        # print(r_array)
        # print(ndcg)
        ndcg_total += ndcg
    print('Average nDCG@{0}:{1}'.format(k, float(ndcg_total)/query_number))
    return float(ndcg_total)/query_number


def load_groundtruth(GROUNDTRUTH_PATH):
    '''
    Load the ground truth
    :param GROUNDTRUTH_PATH:
    :return:
    '''
    global groundtruth_dict
    file = open(GROUNDTRUTH_PATH, 'r')
    for line in file:
        doc_id = line[0: line.index('\t')].strip()
        mappings = line[line.index('\t')+1:].strip().split(',')
        mapping_dict = {}
        for mapping in mappings:
            mapping_dict[mapping.split(':')[0]]=float(mapping.split(':')[1])
        groundtruth_dict[doc_id] = mapping_dict


    # print(groundtruth_dict)

if __name__ == '__main__':
    load_groundtruth(GROUNDTRUTH_PATH)

    '''
    Term-based similarity experiment
     the optional corpus: CORPUS_TERM_PATH, CORPUS_PHRASED_PATH, CORPUS_TERMPHRASED_PATH
    '''
    # corpus_paths = [CORPUS_TERMPHRASED_PATH]
    # for corpus_path in corpus_paths:
    #     output_writer = open('/home/memray/Desktop/Term-based_'+corpus_path[corpus_path.rindex('/')+1:-4]+'_stemmed.txt','w')
    #     output_writer.write(corpus_path[corpus_path.rindex('/')+1:-4]+'\n')
    #     for num_feature in [500,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000]:
    #         output = str(num_feature)
    #         load_documents(corpus_path, num_feature)
    #         for k in [1,3,5,10]:
    #             ndcg = Term_based_similarity(k,num_feature)
    #             output += ','+str(ndcg)
    #         output_writer.write(output+'\n')
    #     output_writer.close()


    '''
    Experiment: Single book(iir+mir) in LDA_single_book_PATH
    '''
    # load_documents(CORPUS_TERM_PATH)
    # input_directory = LDA_single_book_PATH
    # output_writer = open('/home/memray/Desktop/single-books-lda.txt','w')
    # for file_name in os.listdir(input_directory):
    #     if (not file_name.endswith('theta')):
    #         continue
    #     output_writer.write(file_name+'\n')
    #     for i in range(10):
    #         print('-------------------- lamdba='+str(float(i)/float(10))+' -------------------------')
    #         ndcg_1 = TopicModel_based_similarity(input_directory+file_name, 1, float(i)/float(10))
    #         ndcg_3 = TopicModel_based_similarity(input_directory+file_name, 3, float(i)/float(10))
    #         ndcg_5 = TopicModel_based_similarity(input_directory+file_name, 5, float(i)/float(10))
    #         ndcg_10 = TopicModel_based_similarity(input_directory+file_name, 10, float(i)/float(10))
    #         output_writer.write('{0},{1},{2},{3},{4}\n'.format(float(i)/float(10),ndcg_1,ndcg_3,ndcg_5,ndcg_10))
    # output_writer.close()

    '''
    Experiment: All books plus all sigir papers
    '''
    # load_documents(CORPUS_TERM_PATH)
    # output_writer = open('/home/memray/Desktop/LDA_textbook+sigir.txt','w')
    # input_directory = LDA_sigir_PATH
    # for file_name in os.listdir(input_directory):
    #     output_writer.write(file_name+'\n')
    #     for i in range(10):
    #         print('-------------------- lamdba='+str(float(i)/float(10))+' -------------------------')
    #         ndcg_1 = TopicModel_based_similarity(input_directory + file_name, 1, float(i) / float(10))
    #         ndcg_3 = TopicModel_based_similarity(input_directory + file_name, 3, float(i) / float(10))
    #         ndcg_5 = TopicModel_based_similarity(input_directory + file_name, 5, float(i) / float(10))
    #         output_writer.write('{0},{1},{2},{3}\n'.format(float(i)/float(10),ndcg_1,ndcg_3,ndcg_5))
    # output_writer.close()

    '''
    Experiment with different citations of sigir papers(LDA_sigir_citation_PATH)
    '''
    # load_documents(CORPUS_TERM_PATH)
    # input_directory = LDA_sigir_citation_PATH
    # output_writer = open('/home/memray/Desktop/books-lda+sigir-citations.txt','w')
    # for file_name in os.listdir(input_directory):
    #     if (not file_name.endswith('theta')):
    #         continue
    #     output_writer.write(file_name+'\n')
    #     print(file_name)
    #     for i in range(10):
    #         print('-------------------- lamdba='+str(float(i)/float(10))+' -------------------------')
    #         ndcg_1 = TopicModel_based_similarity(input_directory + file_name, 1, float(i) / float(10))
    #         ndcg_3 = TopicModel_based_similarity(input_directory + file_name, 3, float(i) / float(10))
    #         ndcg_5 = TopicModel_based_similarity(input_directory + file_name, 5, float(i) / float(10))
    #         ndcg_10 = TopicModel_based_similarity(input_directory + file_name, 10, float(i) / float(10))
    #         output_writer.write('{0},{1},{2},{3},{4}\n'.format(float(i)/float(10),ndcg_1,ndcg_3,ndcg_5,ndcg_10))
    # output_writer.close()

    '''
    Experiment with differen period of sigir papers
    '''
    load_documents(CORPUS_TERM_PATH)
    input_directory = LDA_sigir_period_PATH
    output_writer = open('/home/memray/Desktop/books-lda+sigir-periods.txt','w')
    for file_name in os.listdir(input_directory):
        if (not file_name.endswith('theta')):
            continue
        output_writer.write(file_name+'\n')
        print(file_name)
        for i in range(10):
            print('-------------------- lamdba='+str(float(i)/float(10))+' -------------------------')
            ndcg_1 = TopicModel_based_similarity(LDA_sigir_period_PATH + file_name, 1, float(i) / float(10))
            ndcg_3 = TopicModel_based_similarity(LDA_sigir_period_PATH + file_name, 3, float(i) / float(10))
            # ndcg_10 = TopicModel_based_similarity(LDA_sigir_period_PATH + file_name, 10, float(i) / float(10))
            output_writer.write('{0},{1},{2}\n'.format(float(i)/float(10),ndcg_1,ndcg_3))
    output_writer.close()




