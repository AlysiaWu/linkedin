import gensim
from gensim import corpora, models, similarities
import nltk
import json

def load_docs(name):
    """ Load documents
            Preprocessed: dictionary, corpus, index, lsi
            Archives: documents
    """
    #corpus = corpora.MmCorpus('data/%s-corpus.mm'% name)
    dictionary = corpora.Dictionary.load('%s.dict' % name)

    with open('%s-files.json' % name) as docs_file:
        documents = json.load(docs_file)

    lsi = models.LsiModel.load('%s-corpus.lsi' % name)

    index = similarities.Similarity.load('%s-corpus.index' % name)

    return documents, dictionary, lsi, index


def query_docs(texts, dictionary, lsi, index):
    """Input: a pile of text from the profile

    """
    vec_bow = dictionary.doc2bow(nltk.word_tokenize(texts.lower()))
    vec_lsi = lsi[vec_bow] # convert the query to LSI space

    s = sorted(vec_lsi, key=lambda item: -item[1])
    # print lsi.print_topic(s[0][0])

    # perform query
    sims = index[vec_lsi] # perform a similarity query against the corpus

    # sort similarities in descending order
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

def preprocess(name, num_topics=512):
    """ 
        Generate corpus, dictionary, lsi, index
    """

    with open('%s-files.json' % name) as docs_file:
        documents = json.load(docs_file)

    dictionary = corpora.Dictionary(nltk.word_tokenize(doc.lower()) for doc in 
        get_profiles(documents))

    # remove stopwords for each corpus and tokenize
    garbage = ['summary', 'experience', 'languages', 'skills', 'education', 'honors']
    stopwords = nltk.corpus.stopwords.words('english') + garbage
    stop_ids = [dictionary.token2id[stopword] for stopword in stopwords
             if stopword in dictionary.token2id]
    once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]

    dictionary.filter_tokens(stop_ids + once_ids) # remove stop words and words that appear only once
    dictionary.compactify()

    dictionary.save('%s.dict' % name) # store the dictionary

    corpus0 = LinkedCorpus()
    tfidf = models.TfidfModel(corpus0)
    corpus = tfidf[corpus0]

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics)
    lsi.save('%s-corpus.lsi' % name)

    corpora.MmCorpus.serialize('%s.mm' % name, corpus)
    corpus = corpora.MmCorpus('%s.mm' % name)

    index = similarities.Similarity('%s.index' % name, lsi[corpus], 
        num_features=corpus.num_terms)

    index.save('%s-corpus.index' % name)

class LinkedCorpus(object):
     def __iter__(self):
        for f in filelist[:10]:
            with open(f, 'r') as openf:        
                x = json.load(openf) 
                for profile in x['profiles']:
                    t = nltk.word_tokenize(profile.lower())
                    yield dictionary.doc2bow(t)

def get_profiles(files):
    for f in files:
        with open(f, 'r') as openf:        
            x = json.load(openf) 
            for profile in x['profiles']:
                yield profile