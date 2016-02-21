import math
import random

from scipy import spatial

from textbook.metric.rank_metrics import ndcg_at_k

__author__ = 'Memray'

import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora, models, similarities
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

from nltk.stem.porter import *


STOPWORD_PATH = '../data/stopword/stopword_en.txt'

GROUNDTRUTH_PATH = '/home/memray/Project/textbook_analyzer/data/algebra_groundtruth.txt'
EVALUATION_DATA_PATH = '/home/memray/Project/textbook_analyzer/data/evaluation_data/algebra/'
CORPUS_TERM_PATH = '/home/memray/Project/textbook_analyzer/data/corpus_algebra_five.txt'
CORPUS_TERM_TWOBOOK_PATH = '/home/memray/Project/textbook_analyzer/data/corpus_algebra_two.txt'

LDA_ALGEBRA = '/home/memray/Project/textbook_analyzer/data//lda/books-lda-algebra/'

groundtruth_dict = {}
# an array of dict, range from [0, iteration_number]. Each value is a dict, which key is query, value is list of relevant document ID
training_data_dict = []
testing_data_dict = []

doc_id2gensim_index = {}
gensim_index2doc_id = {} #gensim_index is the position in gensim model, as only documents in iir and mir are included in gensim
corpus_index2doc_id = {} #corpus_index is the position(line number) in CORPUS_FILE
# dictionary = None
# corpus = None

def load_stopword(path):
    stop_word = []
    try:
        stopword_file = open(path, 'r')
        stop_word = [line.strip() for line in stopword_file]
    except:
        print('Error occurs when loading STOPWORD')
    return stop_word


def load_documents(corpus_path, num_feature = None, stemming=False):
    '''
    Load corpus and convert to Dictionary and Corpus of gensim
    :param corpus_path
    :param num_feature, indicate how many terms you wanna retain, not useful now
    :return:
    '''
    corpus_file = open(corpus_path, 'r')
    doc_id2gensim_index = {} # dict, used for store the mapping pair of {doc_id, index}
    documents = []
    index = 0
    corpus_index = 0

    for line in corpus_file:
        doc_id = line[0: line.index('\t')]
        document = line[line.index('\t')+1:]

        corpus_index += 1
        #filter files we don't care, decrease the training time
        if((not doc_id.startswith('book1')) and (not doc_id.startswith('book2'))):
            continue

        index += 1
        documents.append(document.lower())

    # tokenize and clean. Split non-word: re.sub(r'\W*$', '', re.sub(r'^\W*', '', word)) and numbers
    texts = [[re.sub(r'\W+|\d+', '', word.decode('utf-8')) for word in document.split()]
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

    # stemming, experiment shows that stemming works nothing...
    # if (stemming):
    #     stemmer = PorterStemmer()
    #     texts = [[ stemmer.stem(token) for token in text] for text in texts]

    dictionary = corpora.Dictionary(texts)

    # print(len(dictionary))
    corpus = [dictionary.doc2bow(text) for text in texts]

    two_book = texts[0:538]
    doc_lengths = [len(x) for x in two_book]
    avg_doc_length = reduce(lambda x,y:x+y, doc_lengths)/len(doc_lengths)
    print(avg_doc_length)

    # two_book = corpus[175:417]+corpus[636:920]
    # doc_lengths = [len(x) for x in two_book]
    # avg_doc_length = reduce(lambda x,y:x+y, doc_lengths)/len(doc_lengths)
    # print(avg_doc_length)

    return dictionary, corpus


def load_id_index_mapping(corpus_path):
    '''
    Read corpus and build mapping for doc_id2gensim_index, gensim_index2doc_id
    :param corpus_path
    :return:
    '''
    corpus_file = open(corpus_path, 'r')
    corpus_index2doc_id = {}
    doc_id2gensim_index = {} # dict, used for store the mapping pair of {doc_id, index}
    gensim_index2doc_id = {}
    index = 0
    corpus_index = 0

    for line in corpus_file:
        doc_id = line[0: line.index('\t')]

        corpus_index += 1
        corpus_index2doc_id[corpus_index] = doc_id

        #filter files we don't care, decrease the training time
        if((not doc_id.startswith('book1')) and (not doc_id.startswith('book2'))):
            continue

        doc_id2gensim_index[doc_id] = index
        gensim_index2doc_id[index] = doc_id
        index += 1

    return corpus_index2doc_id, doc_id2gensim_index, gensim_index2doc_id


def Term_based_similarity(corpus, doc_id2gensim_index, gensim_index2doc_id):
    '''
    calc the similarity based on tf-idf model
    :return: a dict which key is iir_id and value is subdict, which key is mir_id and value is term_similarity(iir_id, mir_id)
    '''
    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    corpus_tfidf = tfidf[corpus] # step 2 -- use the model to transform vectors
    matrix_similarity = similarities.MatrixSimilarity(corpus_tfidf) # step 3 -- transform corpus to TFIDF space and index it

    '''
    Get the term_similarity
    '''
    print('Getting the term_similarity')
    term_similarity_dict = {}
    # iterate all the iir documents and retrieve corresponding mir documents
    for doc_id in doc_id2gensim_index:
        # choose one iir document as query, and filter documents not belong to iir
        if (not doc_id.startswith('book1')) or (not groundtruth_dict.has_key(doc_id)):
            continue
        query = corpus[doc_id2gensim_index[doc_id]]

        sims = matrix_similarity[query] # perform a similarity query against the corpus (all documents)
        sims = sorted(enumerate(sims), key=lambda item: -item[1]) # print sorted (document number, similarity score) 2-tuples

        # return the list of mir documents, a dict which key is mir_id and value is similarity
        mir_sims = dict((gensim_index2doc_id[k], v) for k, v in [sim for sim in sims if gensim_index2doc_id[sim[0]].startswith('book2')])
        term_similarity_dict[doc_id] = mir_sims
    return term_similarity_dict

def Topic_Model_based_similarity(lda_file_path, corpus_index2doc_id):
    '''
    Get the topicmodel_similarity
    :return: a dict which key is iir_id and value is subdict, which key is mir_id and value is topic_similarity(iir_id, mir_id)
    '''
    print('Getting the topicmodel_similarity')
    print(lda_file_path)
    topicmodel_similarity_dict = {}
    lda_file = open(lda_file_path,'r')
    lines = lda_file.readlines()
    index_i = 0
    for line_i in lines:
        index_i += 1
        doc_id_i = corpus_index2doc_id[index_i]
        if not doc_id_i.startswith('book1'):
            continue
        # print(doc_id_i)
        dataSet_i = [float(i) for i in line_i.split('\t') if len(i.strip()) > 0]
        mir_sims = {}
        index_j = 0
        for line_j in lines:
            index_j += 1
            doc_id_j = corpus_index2doc_id[index_j]
            if not doc_id_j.startswith('book2'):
                continue
            # print(doc_id_j)
            dataSet_j = [float(j) for j in line_j.split('\t')  if len(j.strip()) > 0]
            cosine = 1 - spatial.distance.cosine(dataSet_i, dataSet_j)
            mir_sims[doc_id_j] = cosine
        topicmodel_similarity_dict[doc_id_i] = mir_sims
    lda_file.close()

    return topicmodel_similarity_dict


def evaluate_ndcg_at_k(testing_data, similarity_dict_1, similarity_dict_2, k, lambda_ratio, doc_id2gensim_index):
    '''
    calc the similarity based on merging term and topic model
    :param: k, top k results accounted for calculating NDCG
    :param: lambda_ratio, the ratio for blending, final_similarity = lambda*term_similarity + (1-lambda)*topic_model_similarity
            lambda_ratio = 0 means only topic_model_similarity.
            lambda_ratio = 1 means only term_similarity
    :return: return NDCG@k
    '''
    ndcg_total = 0
    query_number = 0

    '''
    Get the final similarity rank
    '''
    # print('Getting the final similarity rank')
    for doc_id in doc_id2gensim_index:
        if (not doc_id.startswith('book1')) or (not testing_data.has_key(doc_id)):
            continue
        query_number += 1
        count = 0
        mapping_dict = testing_data[doc_id]

        weighted_similarities = {}

        if (not similarity_dict_1 is None) and (lambda_ratio==1):
            weighted_similarities = similarity_dict_1[doc_id]
        elif (not similarity_dict_2 is None) and (lambda_ratio==0):
            weighted_similarities = similarity_dict_2[doc_id]
        elif (not similarity_dict_1 is None) and (not similarity_dict_2 is None):
            for (doc_id_j,term_similarity) in similarity_dict_1[doc_id].items():
                if similarity_dict_2[doc_id].has_key(doc_id_j):
                    weighted_similarities[doc_id_j] = term_similarity*lambda_ratio + similarity_dict_2[doc_id][doc_id_j] * (1 - lambda_ratio)
        else:
            print('At least one of the similarities is wrong')
        weighted_similarities = sorted(weighted_similarities.items(), key=lambda item: item[1],reverse=True)# print sorted (document number, similarity score) 2-tuples

        r_array = [] # array used as input of nDCG
        for entry in weighted_similarities:
            if entry[0].startswith('book2'):
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
    logger.info('lambda={0}, #query={1} ,nDCG@{2}:{3}'.format(lambda_ratio,len(testing_data), k, float(ndcg_total)/query_number))
    return float(ndcg_total)/query_number


def load_groundtruth():
    '''
    Load the ground truth and generate the training/testing data by shuffling
    :param GROUNDTRUTH_PATH:
    :return:
    '''
    file = open(GROUNDTRUTH_PATH, 'r')
    for line in file:
        doc_id = line[0: line.index('\t')].strip()
        mappings = line[line.index('\t')+1:].strip().split(',')
        mapping_dict = {}
        for mapping in mappings:
            mapping_dict[mapping.split(':')[0]]=float(mapping.split(':')[1])
        groundtruth_dict[doc_id] = mapping_dict


def generate_evaluation_data(N=100, fold_num=5):
    '''
    Generate training/testing data base on groundtruth
    :param N:
    :param fold_num:
    :return:
    '''
    evaluation_data = []
    file = open(GROUNDTRUTH_PATH, 'r')
    for line in file:
        evaluation_data.append(line.strip())

    query_num = len(evaluation_data)
    testing_num = query_num/fold_num+1
    for i in range(N):
        random.shuffle(evaluation_data)
        training_file = open(EVALUATION_DATA_PATH+'train_'+str(i)+'.txt','w')
        testing_file = open(EVALUATION_DATA_PATH+'test_'+str(i)+'.txt','w')
        # testing_data = []
        # training_data = []
        for line in evaluation_data[:testing_num]:
            testing_file.write(line+'\n')
            # testing_data.append(line)
        for line in evaluation_data[testing_num:]:
            training_file.write(line+'\n')
            # training_data.append(line)
        testing_file.close()
        training_file.close()


def load_evaluation_data():
    '''
    Load the ground truth and generate the training/testing data by shuffling
    :param GROUNDTRUTH_PATH:
    :return:
    '''
    file_num = len(os.listdir(EVALUATION_DATA_PATH))
    for i in range(file_num):
        testing_data_dict.append({})
        training_data_dict.append({})

    for file_name in os.listdir(EVALUATION_DATA_PATH):
        if file_name.startswith('train'):
            file_number = int(file_name[file_name.index('_')+1:-4])
            file = open(EVALUATION_DATA_PATH+file_name,'r')
            for line in file:
                doc_id = line[0: line.index('\t')].strip()
                mappings = line[line.index('\t')+1:].strip().split(',')
                mapping_dict = {}
                for mapping in mappings:
                    mapping_dict[mapping.split(':')[0]]=float(mapping.split(':')[1])
                training_data_dict[file_number][doc_id] = mapping_dict

    for file_name in os.listdir(EVALUATION_DATA_PATH):
        if file_name.startswith('test'):
            file_number = int(file_name[file_name.index('_')+1:-4])
            file = open(EVALUATION_DATA_PATH+file_name,'r')
            for line in file:
                doc_id = line[0: line.index('\t')].strip()
                mappings = line[line.index('\t')+1:].strip().split(',')
                mapping_dict = {}
                for mapping in mappings:
                    mapping_dict[mapping.split(':')[0]]=float(mapping.split(':')[1])
                testing_data_dict[file_number][doc_id] = mapping_dict


def experiment_cross_validation(iter_num = 100, fold_num=5):
    '''
    Run cross validation
    :return:
    '''
    # Similarity initialization,
    corpus_paths = [CORPUS_TERM_TWOBOOK_PATH, CORPUS_TERM_PATH]
    # dictionary, corpus_phrase = load_documents(corpus_paths[2])
    # dictionary, corpus_term_phrase = load_documents(corpus_paths[3])
    dictionary, corpus = load_documents(corpus_paths[0], stemming=False)

    # two_corpus_index2doc_id, two_doc_id2gensim_index, two_gensim_index2doc_id = load_id_index_mapping(corpus_paths[0])
    all_corpus_index2doc_id, all_doc_id2gensim_index, all_gensim_index2doc_id = load_id_index_mapping(corpus_paths[1])

    '''
    Term-based Similarity
    '''
    #0 is basic term-based similarity, 1 is phrase replaced, 2 is retaining both term and phrase
    term_similarity = {}
    term_similarity['Word_term-based'] = Term_based_similarity(corpus, all_doc_id2gensim_index, all_gensim_index2doc_id)
    # term_similarity['Word_phrase-replaced'] = Term_based_similarity(corpus_phrase, all_doc_id2gensim_index, all_gensim_index2doc_id)
    # term_similarity['Word_term-phrase-both'] = Term_based_similarity(corpus_term_phrase, all_doc_id2gensim_index, all_gensim_index2doc_id)
    '''
    Keyword-based Similarity
    '''
    # keyword_similarity = {}
    # # keyword_similarity['Keyword-phrase-decomposed'] = Term_based_similarity(keyword_corpus, all_doc_id2gensim_index, all_gensim_index2doc_id)
    # keyword_similarity['Keyword-only'] = Term_based_similarity(keyword_corpus, all_doc_id2gensim_index, all_gensim_index2doc_id)

    '''
    LDA-based Similarity
    '''
    # initialize the name mapping of LDA models
    topic_model_name_mapping = {}
    for topic_num in ['100','150','200']:
        topic_model_name_mapping['LDA_algebra_five_'+topic_num] = LDA_ALGEBRA + topic_num + '-final-five.theta'
        topic_model_name_mapping['LDA_algebra_two_'+topic_num] = LDA_ALGEBRA + topic_num + '-final-two.theta'

    # get LDA similarity
    topic_model_similarity = {}
    for model_name, model_path in topic_model_name_mapping.items():
        topic_model_similarity[model_name] = Topic_Model_based_similarity(model_path, all_corpus_index2doc_id)

    '''
    Cross-Validation
    '''
    # training/testing dataset initialization
    query_num = len(groundtruth_dict)
    testing_num = query_num/fold_num+1
    training_num = query_num-testing_num

    result_dict = {}
    # Prepare the output
    for k in [1,3]:
        for model_name in term_similarity.keys():
            result_dict[model_name+'@'+str(k)] = []

        '''
        for model_name in keyword_similarity.keys():
            result_dict['pure_'+model_name+'@'+str(k)] = []
            result_dict[model_name+'@'+str(k)] = []
        '''

        for model_name in topic_model_similarity.keys():
            # only do pure LDA experiments for these two
            # if(model_name.startswith('LDA_textbook_all+sigir_all_') or model_name.startswith('LDA_textbook_two_')):
            result_dict['pure_'+model_name+'@'+str(k)] = []
            result_dict[model_name+'@'+str(k)] = []

    # iter_num times random cross validation
    for iteration in range(iter_num):
        # randomize the training/testing data
        testing_data = testing_data_dict[iteration]
        training_data = training_data_dict[iteration]

        # run experiments
        for k in [1,3]:
            print('------------------------------------------------------------')
            print('Round '+str(iteration)+'@'+str(k))
            '''
            TFIDF-based similarity
            '''
            for model_name in term_similarity.keys():
                ndcg = evaluate_ndcg_at_k(testing_data, term_similarity[model_name], None, k, 1, all_doc_id2gensim_index)
                logger.info('[Testing@'+str(k)+':'+model_name+']'+str(ndcg)+'\n')
                result_dict[model_name+'@'+str(k)].append(ndcg)
                # output += ','+str(ndcg)

            """
            '''
            Keyword-based similarity
            '''
            for model_name in keyword_similarity.keys():

                # Pure-Keyword: testing with the lambda=0 (only LDA no TF-IDF) on testing set
                ndcg = evaluate_ndcg_at_k(testing_data, keyword_similarity[model_name], None, k, 1, all_doc_id2gensim_index)
                logger.info('[Testing@'+k+':'+model_name+']'+str(ndcg)+'\n')
                result_dict['pure_'+model_name+'@'+str(k)].append(ndcg)

                # Blending: find the best lambda on training set
                best_ndcg = 0
                best_lambda = 0
                for i in range(10):
                    ndcg = evaluate_ndcg_at_k(training_data, term_similarity['Word_term-based'], keyword_similarity[model_name], k, float(i) / float(10), all_doc_id2gensim_index)
                    if best_ndcg < ndcg:
                        best_ndcg = ndcg
                        best_lambda = float(i) / float(10)
                logger.info('[Training@'+k+':Blending *Word_term-based* and *'+model_name+'*]'+str(best_ndcg)+'(Best lambda:'+str(best_lambda)+')')

                # Blending: testing with the best lambda on testing set
                ndcg = evaluate_ndcg_at_k(testing_data, term_similarity['Word_term-based'], keyword_similarity[model_name], k, best_lambda, all_doc_id2gensim_index)
                logger.info('[Testing@'+k+':Blending *Word_term-based* and *'+model_name+'*]'+str(ndcg)+'(Best lambda:'+str(best_lambda)+')\n')
                result_dict[model_name+'@'+str(k)].append(ndcg)

            """
            '''
            LDA-based similarity
            '''
            for model_name in topic_model_name_mapping.keys():
                # Pure-LDA: testing with the lambda=0 (only LDA no TF-IDF) on testing set
                ndcg = evaluate_ndcg_at_k(testing_data, term_similarity['Word_term-based'], topic_model_similarity[model_name], k, 0, all_doc_id2gensim_index)
                logger.info('[Testing@'+str(k)+':pure_'+model_name+']'+str(ndcg)+'(lambda=0)\n')
                result_dict['pure_'+model_name+'@'+str(k)].append(ndcg)

                # Blending: find the best lambda on training set
                best_ndcg = 0
                best_lambda = 0
                for i in range(10):
                    ndcg = evaluate_ndcg_at_k(training_data, term_similarity['Word_term-based'], topic_model_similarity[model_name], k, float(i) / float(10), all_doc_id2gensim_index)
                    if best_ndcg < ndcg:
                        best_ndcg = ndcg
                        best_lambda = float(i) / float(10)
                logger.info('[Training@'+str(k)+':'+model_name+']'+str(best_ndcg)+'(Best lambda:'+str(best_lambda)+')')

                # Blending: testing with the best lambda on testing set
                ndcg = evaluate_ndcg_at_k(testing_data, term_similarity['Word_term-based'], topic_model_similarity[model_name], k, best_lambda, all_doc_id2gensim_index)
                logger.info('[Testing@'+str(k)+':'+model_name+']'+str(ndcg)+'(Best lambda:'+str(best_lambda)+')\n')
                result_dict[model_name+'@'+str(k)].append(ndcg)


    # output = model_name+'\t'+','.join(map(str, result_dict[model_name]))+'\n'
    output = ''
    for model_name in result_dict.keys():
        output += model_name+'\t'
        for v in result_dict[model_name]:
            output += str(v)+','
        output = output[:-1]+'\n'
    result_logger.info(output)

LOG_OUTPUT_PATH = '/home/memray/Desktop/algebra_log_file.txt'
RESULT_OUTPUT_PATH = '/home/memray/Desktop/algebra_result_file.txt'
logger = logging.getLogger('textbook_all_info_logger')
fh = logging.FileHandler(LOG_OUTPUT_PATH, mode='w')
ch=logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# ch.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.addHandler(ch)

result_logger = logging.getLogger('textbook_result_logger')
rfh = logging.FileHandler(RESULT_OUTPUT_PATH, mode='w')
result_logger.setLevel(logging.DEBUG)
result_logger.addHandler(rfh)

if __name__ == '__main__':

    load_groundtruth()
    # generate_evaluation_data()
    load_evaluation_data()
    try:
        experiment_cross_validation(iter_num=100, fold_num=5)
    except:
        logger.exception("message")

    # experiment_term_similarity()
    # experiment_term_lda_similarity()



