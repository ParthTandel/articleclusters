import os
import nltk
import spacy
from gensim import corpora,models, similarities

from pymongo import MongoClient
client = MongoClient()
db = client.projectdb1
collection = db.articles
nlp = spacy.load('en')
from stopword_rm import stopwords



if (os.path.exists("deerwester.dict")):
    dictionary = corpora.Dictionary.load('deerwester.dict')
    corpus = corpora.MmCorpus('deerwester.mm')
    model = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=20)
    topics = model.print_topics(20)

    for topic in topics:
        print topic

    clusters = {}
    for i in xrange(0,20):
        clusters[i] = []

    for article in collection.find({"type":"Entertainment"}):
        spacy_tokens = []
        doc = nlp(article["text"])
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                spacy_tokens.append(ent.text.lower())

        query = dictionary.doc2bow(spacy_tokens)
        print article['count'],model[query]
        similarity = model[query]
        for data in similarity:
            if data[1] > 0.9:
                clusters[data[0]].append({
                    "id" : article["count"],
                    "doc": spacy_tokens
                })


    # print clusters
    for value in clusters.keys():
        print "**********************************************************************"
        print topics[value]
        print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
        for data in clusters[value]:
            print data
        print "**********************************************************************"


   # index = similarities.MatrixSimilarity(model[corpus])
   # index.save('deerwester.index')
   # index = similarities.MatrixSimilarity.load('deerwester.index')
else:
   print("Please run first tutorial to generate data set")
