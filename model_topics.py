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
    model = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=5)
    topics = model.print_topics(5)

    for topic in topics:
        print topic

    clusters = {}
    for i in xrange(0,10):
        clusters[i] = []

    data = collection.find({"type":"Entertainment"})
    for article in data:
        # article_text = article["text"].split(".")[3:]
        # article_text = [str(word) for word in article_text if str(word) not in stopwords]
        # article_text = u"".join(article_text).encode('utf-8')


        spacy_tokens = []
        # doc = nlp(unicode(article_text, errors='ignore'))
        doc = nlp(article["text"])
        for ent in doc.ents:
            if ent.label_ == "PERSON" or ent.label_ == "GPE" or ent.label_ == "ORG" and ent.text.lower() not in stopwords:
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
