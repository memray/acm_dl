__author__ = 'Memray'

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim import corpora, models, similarities
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

STOPWORD_PATH = '../data/stopword/stopword_en.txt'
CORPUS_PATH = 'H:/Dropbox/PhD@Pittsburgh/1.Researh/NSF/20160125_analyzer_v1/textbook_analyzer/data/corpus_textbook+sigir.txt'

def load_stopword(path):
    stop_word = []
    try:
        stopword_file = open(path, 'r')
        stop_word = [line.strip() for line in stopword_file]
    except:
        print('Error occurs when loading STOPWORD')
    return stop_word

def load_documents(corpus_path):
    corpus_file = open(corpus_path, 'r')
    id2index = {} # dict, used for store the mapping pair of {doc_id, index}
    documents = []
    index = 0

    for line in corpus_file:
        id = line[0: line.index('\t')]
        document = line[line.index('\t'):]

        id2index[id] = index
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

    return dictionary, corpus

if __name__ == '__main__':
    # index = Similarity('/path/to/index', corpus, num_features=400)  # if corpus has 7 documents...
    dictionary, corpus = load_documents(CORPUS_PATH)
    # print(dictionary)
    # print(corpus)
    pass
