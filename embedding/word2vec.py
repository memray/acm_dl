__author__ = 'Memray'
from gensim.models import word2vec
from gensim.models import Word2Vec
import nltk
from nltk.corpus import stopwords
import os

def process_sentences(path):
    doc_list = os.listdir(path)
    sentences = []
    count = 0
    for doc_name in doc_list:
        count += 1
        print('{0}:{1}'.format(count, doc_name))
        file = open(path+doc_name,'r')
        text = ''.join(file.readlines()).decode('ascii','ignore')

        raw_sentences = tokenizer.tokenize(text.strip())
        for raw_sentence in raw_sentences:
            if len(raw_sentence) > 0:
                words = raw_sentence.lower().split()
                stops = set(stopwords.words("english"))
                words = [w for w in words if not w in stops]
                sentences.append(words)
    return sentences

action = "test"

input_dir_path = "E:\\acm_dl\\pdf\\ir\\phrase_extracted\\"
if action == "train":
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    print('Start to load corpus')
    sents = []
    sents += process_sentences(input_dir_path)

    num_features = 300    # Word vector dimensionality
    min_word_count = 40   # Minimum word count
    num_workers = 4       # Number of threads to run in parallel
    context = 10          # Context window size
    downsampling = 1e-3   # Downsample setting for frequent words
    print("training!")
    # Initialize and train the model (this will take some time)
    model = word2vec.Word2Vec(sents, workers=num_workers, \
                size=num_features, min_count = min_word_count, \
                window = context, sample = downsampling)

    # If you don't plan to train the model any further, calling
    # init_sims will make the model much more memory-efficient.
    model.init_sims(replace=True)

    # It can be helpful to create a meaningful model name and
    # save the model for later use. You can load it later using Word2Vec.load()
    model_name = "acm_fulltext_model"
    model.save(model_name)
else:
    model = Word2Vec.load("acm_fulltext_model")
    print(model.most_similar("information_retrieval"))
