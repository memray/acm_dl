from textbook.metric.rank_metrics import ndcg_at_k

__author__ = 'Memray'

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora, models, similarities
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

STOPWORD_PATH = '../data/stopword/stopword_en.txt'
CORPUS_PATH = '/home/memray/Project/textbook_analyzer/data/corpus_textbook+sigir.txt'
CORPUS_PHRASED_PATH = '/home/memray/Project/textbook_analyzer/data/corpus_textbook+sigir_phrased.txt'
GROUNDTRUTH_PATH = '/home/memray/Project/textbook_analyzer/data/ir_groundtruth.txt'
groundtruth_dict = {}
docid2corpus_index = {}
corpus_index2docid = {}
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


def load_documents(corpus_path):
    '''
    Load corpus and convert to Dictionary and Corpus of gensim
    :param corpus_path:
    :return:
    '''
    global docid2corpus_index, corpus_index2docid, dictionary,corpus, groundtruth_dict
    corpus_file = open(corpus_path, 'r')
    docid2corpus_index = {} # dict, used for store the mapping pair of {doc_id, index}
    documents = []
    index = 0

    for line in corpus_file:
        id = line[0: line.index('\t')]
        document = line[line.index('\t')+1:]

        #filter files we don't care, decrease the training time
        if((not id.startswith('iir')) and (not id.startswith('mir'))):
            continue

        docid2corpus_index[id] = index
        corpus_index2docid[index] = id
        index += 1
        documents.append(document.lower())

    # remove common words and tokenize
    stoplist = load_stopword(STOPWORD_PATH)
    texts = [[word for word in document.lower().split() if word not in stoplist]
             for document in documents]

    # remove words that appear only once
    from collections import defaultdict

    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if frequency[token] > 1]
             for text in texts]

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    return docid2corpus_index, dictionary, corpus


def termbased_similarity(k):
    '''
    calc the similarity based on purely term
    :return:
    '''
    global docid2corpus_index, corpus_index2docid, dictionary,corpus, groundtruth_dict
    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    corpus_tfidf = tfidf[corpus] # step 2 -- use the model to transform vectors
    index = similarities.MatrixSimilarity(corpus_tfidf) # step 3 -- transform corpus to TFIDF space and index it

    ndcg_total = 0
    query_number = 0
    for id in docid2corpus_index:
        if (not id.startswith('iir')) or (not groundtruth_dict.has_key(id)):
            continue
        query_number += 1
        document = corpus[docid2corpus_index[id]]

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
            if corpus_index2docid[entry[0]].startswith('mir'):
                count += 1
                if(count > 12):
                    break
                if mapping_dict.has_key(corpus_index2docid[entry[0]]):
                    r_array.append(mapping_dict[corpus_index2docid[entry[0]]])
                else:
                    r_array.append(0)
                # print(entry[0], corpus_index2docid[entry[0]], entry[1])
        ndcg = ndcg_at_k(r_array, k)
        # print(r_array)
        # print(ndcg)
        ndcg_total += ndcg
    print('Average nDCG@{0}:{1}'.format(k, float(ndcg_total)/query_number))

def TopicModel_based_similarity(lam, k):
    '''
    calc the similarity based on merging term and topic model
    :return:
    '''
    global docid2corpus_index, corpus_index2docid, dictionary,corpus, groundtruth_dict
    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    corpus_tfidf = tfidf[corpus] # step 2 -- use the model to transform vectors
    index = similarities.MatrixSimilarity(corpus_tfidf) # step 3 -- transform corpus to TFIDF space and index it

    ndcg_total = 0
    query_number = 0

    term_similarity_dict = {}
    for id in docid2corpus_index:
        if (not id.startswith('iir')) or (not groundtruth_dict.has_key(id)):
            continue
        query_number += 1
        document = corpus[docid2corpus_index[id]]

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
            if corpus_index2docid[entry[0]].startswith('mir'):
                count += 1
                if(count > 12):
                    break
                if mapping_dict.has_key(corpus_index2docid[entry[0]]):
                    r_array.append(mapping_dict[corpus_index2docid[entry[0]]])
                else:
                    r_array.append(0)
                # print(entry[0], corpus_index2docid[entry[0]], entry[1])
        ndcg = ndcg_at_k(r_array, k)
        # print(r_array)
        # print(ndcg)
        ndcg_total += ndcg
    print('Average nDCG@{0}:{1}'.format(k, float(ndcg_total)/query_number))


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
    # index = Similarity('/path/to/index', corpus, num_features=400)  # if corpus has 7 documents...
    load_groundtruth(GROUNDTRUTH_PATH)
    load_documents(CORPUS_PATH)

    termbased_similarity(1)
    termbased_similarity(3)
    termbased_similarity(10)

    load_documents(CORPUS_PHRASED_PATH)
    termbased_similarity(1)
    termbased_similarity(3)
    termbased_similarity(10)