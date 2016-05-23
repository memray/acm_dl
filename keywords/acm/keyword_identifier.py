# encoding: utf-8
import string

from nltk.stem.porter import *
__author__ = 'Memray'
import os
# os.chdir("/home/memray/Project/acm_dl/")
from functools import reduce
from gensim import corpora, models, similarities

KEYWORD_LIST_PATH = '/home/memray/Project/ACMParser/resource/data/phrases/'
ACL_KEYWORD_PATH = KEYWORD_LIST_PATH + 'acl_keywords.txt'
ACM_KEYWORD_PATH = KEYWORD_LIST_PATH + 'acm_keywords.txt'
MICROSOFT_KEYWORD_PATH = KEYWORD_LIST_PATH + 'microsoft_keywords.txt'

DO_STEM = True
stemmer = PorterStemmer()

TRIE_LOCAL_CACHE = 'data/keyword_extract/trie_dict.cache'

def load_stopwords():
    STOPWORD_PATH = 'data/stopword/stopword_en.txt'
    dict = set()
    file = open(STOPWORD_PATH, 'r')
    for line in file:
        dict.add(line.lower().strip())
    return dict

stopwords = load_stopwords()


class Trie:
    """
    Implement a trie with insert, search, and startsWith methods.
    """
    def __init__(self):
        self.is_end = False
        self.nodes = {}

    # Inserts a phrase into the trie.
    def insert(self, words):
        current_word = words[0]
        if DO_STEM:
            current_word = stemmer.stem(current_word)
        if not current_word in self.nodes:
            self.nodes[current_word]=Trie()
        if len(words)==1:
            self.nodes[current_word].is_end=True
            return
        elif len(words) > 1:
            self.nodes[current_word].insert(words[1:])

    # Returns if the word is in the trie.
    def search(self, words):
        current_word = words[0]
        if DO_STEM:
            current_word = stemmer.stem(current_word)

        if not current_word in self.nodes:
            return False

        if len(words) > 1:
            return self.nodes[current_word].search(words[1:])
        elif (len(words) == 1) and (self.nodes[current_word].is_end):
            return True
        else:
            return False

    # Scan a sentence and find any ngram that appears in the sentence
    def scan(self, sentence, min_length=1, max_length=3):
        keyword_list = []
        sentence = sentence.lower()
        original_tokens = sentence.split()
        tokens = sentence.split()

        transtable = str.maketrans('', '', string.punctuation)

        if DO_STEM:
            original_tokens = [token.translate(transtable) for token in original_tokens]
            tokens = [stemmer.stem(token).translate(transtable) for token in tokens]

        for i in range(len(tokens)):
            for j in range(min_length, max_length+1):
                if (i+j > len(sentence)):
                    break
                if (j==1) and (tokens[i:i+j][0] in stopwords):
                    continue
                # print(' '.join(tokens[i:i + j]))
                if self.search(tokens[i:i+j]):
                    keyword_list.append(' '.join(original_tokens[i:i+j]))
        return keyword_list


def ngram_stem(str):
    tokens = []
    for token in str.split():
        tokens.append(stemmer.stem(token))
    return ' '.join(tokens)

import pickle
def load_trie():
    '''
    Load a prebuilt tree from file or create a new one
    :return:
    '''
    trie = Trie()

    if os.path.isfile(TRIE_LOCAL_CACHE):
        with open(TRIE_LOCAL_CACHE, 'rb') as f:
            trie = pickle.load(f)
    else:
        count = 0
        transtable = str.maketrans('', '', string.punctuation)
        dict_files = [ACL_KEYWORD_PATH, ACM_KEYWORD_PATH]
        for dict_file in dict_files:
            file = open(dict_file, 'r')
            for line in file:
                count+=1
                if count % 10000==0:
                    print(count)
                # if is stopword, pass
                line = line.lower().strip()
                if (line in stopwords):
                    print(line)
                    continue
                tokens = line.lower().split()

                # do stemming and remove punctuations
                if DO_STEM:
                    tokens = [stemmer.stem(token).translate(transtable) for token in tokens]
                print(tokens)
                if(len(tokens)>0):
                    trie.insert(tokens)
        with open(TRIE_LOCAL_CACHE, 'wb') as f:
            pickle.dump(trie, f)
    return trie

class Document:
    def __init__(self, line):
        self.id = line[:line.index('\t')]
        self.text = line[line.index('\t')+1:].lower()

IR_CORPUS = 'data/keyword_extract/ir_textbook.txt'
def load_document(path):
    doc_list = []
    file = open(path, 'r')
    for line in file:
        doc = Document(line)
        doc_list.append(doc)
    return  doc_list

KEYWORD_ONLY = 'data/keyword_extract/keyword_only.txt'
TOP_TFIDF = 'data/keyword_extract/tfidf_100.txt'

def extract_author_keywords(keyword_trie, documents):
    output_file = open(KEYWORD_ONLY, 'w')
    for doc in documents:
        print(doc.id)
        keyword_list = keyword_trie.scan(doc.text)
        keyword_dict = {}
        for word in keyword_list:
            if word in keyword_dict:
                keyword_dict[word] += 1
            else:
                keyword_dict[word] = 1
        list = ['{0}:{1}'.format(item[0],item[1]) for item in sorted(keyword_dict.items(),key=lambda x:x[1], reverse=True)]

        output_file.write('{0}\t{1}\n'.format(doc.id, ','.join(list)))
    output_file.close()


def extract_high_tfidf_words(keyword_trie, documents, top_k=100):
    '''
    Load corpus and convert to Dictionary and Corpus of gensim
    :param corpus_path
    :param num_feature, indicate how many terms you wanna retain, not useful now
    :return:
    '''
    texts = [[word for word in document.text.split()]
             for document in documents]

    doc_lengths = [len(x) for x in texts]
    avg_doc_length = reduce(lambda x, y: x + y, doc_lengths) / len(doc_lengths)
    print('#tokens before any preprocessing:' + str(avg_doc_length))

    # tokenize and clean. Split non-word&number: re.sub(r'\W+|\d+', '', word.decode('utf-8'))
    texts = [[re.sub(r'\W+|\d+', '', word) for word in document.text.split()]
             for document in documents]

    doc_lengths = [len(x) for x in texts]
    avg_doc_length = reduce(lambda x, y: x + y, doc_lengths) / len(doc_lengths)
    print('#tokens after removing \d+:' + str(avg_doc_length))

    # remove stop words and short tokens
    texts = [[token for token in text if (token not in stopwords)]
             for text in texts]

    doc_lengths = [len(x) for x in texts]
    avg_doc_length = reduce(lambda x, y: x + y, doc_lengths) / len(doc_lengths)
    print('#tokens after removing stopwords:' + str(avg_doc_length))

    # remove words that appear only once
    from collections import defaultdict
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if (frequency[token] > 1)]
             for text in texts]

    doc_lengths = [len(x) for x in texts]
    avg_doc_length = reduce(lambda x, y: x + y, doc_lengths) / len(doc_lengths)
    print('#tokens after removing #freq=1:' + str(avg_doc_length))

    # stemming, experiment shows that stemming works nothing...
    # if (stemming):
    #     stemmer = PorterStemmer()
    #     texts = [[ stemmer.stem(token) for token in text] for text in texts]

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # print(len(dictionary))

    doc_lengths = [len(x) for x in texts]
    avg_doc_length = reduce(lambda x, y: x + y, doc_lengths) / len(doc_lengths)
    print('#tokens after all preprocessing(unique tokens):' + str(avg_doc_length))

    # ---------------------------------Done: building gensem dictionary, corpus-----------------------------------------------------
    for k,v in dictionary.token2id.items():
        dictionary.id2token[v]=k
    tfidf = models.TfidfModel(corpus, dictionary=dictionary) # step 1 -- initialize a model
    corpus_tfidf = tfidf[corpus] # step 2 -- use the model to transform vectors

    for i, doc in enumerate(documents):
        doc.tfidf = corpus_tfidf[i]

    output_file = open(TOP_TFIDF, 'w')
    for doc in documents:
        doc.tfidf = sorted(doc.tfidf, key=lambda item: item[1], reverse=True)
        if top_k>len(doc.tfidf):
            i = len(doc.tfidf)
        else:
            i = top_k
        top_k_list = [dictionary.id2token[tuple[0]] for tuple in doc.tfidf[:i]]
        print(','.join(top_k_list))
        output_file.write('{0}\t{1}\n'.format(doc.id, ','.join(top_k_list)))
    output_file.close()


LLDA_INPUT_PATH = '/home/memray/Project/acm_xiaozhong/LLDA/data/ir_textbook/input/'
LLDA_RESULT_PATH = '/home/memray/Project/acm_xiaozhong/LLDA/data/ir_textbook/result/inference.theta.dat'
LLDA_KEYWORD_PATH = '/home/memray/Project/acm_xiaozhong/LLDA/file/acm_keywords.dat'

LLDA_LABEL_OUTPUT = 'data/keyword_extract/llda_label.txt'
def export_to_files(documents):
    '''
    Xiaozhong's Labeled LDA needs one document one file
    :return:
    '''
    for doc in documents:
        file = open(LLDA_INPUT_PATH+doc.id, 'w')
        file.write(doc.text)
        file.close()


def extract_high_labeled_lda(documents, top_k=100):
    # export_to_files(documents)
    id2word = {}
    with open(LLDA_KEYWORD_PATH, 'r') as keyword_file:
        for line in keyword_file:
            tokens = line.lower().strip().split(',')
            id2word[tokens[0]] = tokens[1]

    output_file = open(LLDA_LABEL_OUTPUT, 'w')
    with open(LLDA_RESULT_PATH, 'r') as result_file:
        for i, line in enumerate(result_file):
            doc = documents[i]
            labels = [token.split(':')[0] for token in line.split(' ')]
            probabilities = [float(token.split(':')[1]) for token in line.split(' ')]
            k = 0
            while (k<top_k) and (probabilities[k]>0.0001):
                k += 1
            print(doc.id)
            keyword_list = [id2word[label] for label in labels[:k]]
            output_file.write('{0}\t{1}\n'.format(doc.id, ','.join(keyword_list)))
    output_file.close()


if __name__=='__main__':
    keyword_trie = load_trie()
    documents = load_document(IR_CORPUS)

    extract_author_keywords(keyword_trie, documents)
    # extract_high_tfidf_words(documents, 100)
    # extract_high_labeled_lda(documents, 100)
