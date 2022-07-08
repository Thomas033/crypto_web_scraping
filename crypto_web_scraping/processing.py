import nltk

def preprocessing(corpus):

    corpus = corpus.replace("\n","")
    stop_words = nltk.corpus.stopwords.words("english")
    words = [w for w in corpus if w.lower() not in stop_words]

    return words
