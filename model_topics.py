import os
import spacy
from gensim import corpora,models, similarities
from stopword_rm import stopwords
from pymongo import MongoClient

client = MongoClient("ec2-18-223-123-230.us-east-2.compute.amazonaws.com")
db = client.projectclean_db
collection = db.articles
nlp = spacy.load('en_core_web_sm')

if (os.path.exists("deerwester.dict")):
    dictionary = corpora.Dictionary.load('deerwester.dict')
    corpus = corpora.MmCorpus('deerwester.mm')
    model = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=100)
    topics = model.print_topics(100)

    for topic in topics:
        print(topic)

    clusters = {}
    for i in range(0,100):
        clusters[i] = []

    data = collection.find({"type":"Entertainment"})
    for article in data:
        article_text = article["text"].split(".")[3:]
        article_text = " ".join(article_text)
        article_text = article_text.split(" ")
        article_text = [str(word) for word in article_text if str(word) not in stopwords]
        article_text = " ".join(article_text)

        spacy_tokens = []
        doc = nlp(article["text"])
        for ent in doc.ents:
            if ent.label_ == "PERSON" or ent.label_ == "GPE" or ent.label_ == "ORG" and ent.text.lower() not in stopwords:
                spacy_tokens.append(ent.text.lower())

        query = dictionary.doc2bow(spacy_tokens)
        # print article['count'],model[query]        
        similarity = model[query]
        for data in similarity:
            if data[1] > 0.9:
                clusters[data[0]].append({
                    "id" : article["count"]
                    })


    # print clusters
    for value in clusters.keys():
        print ("**********************************************************************")
        print (topics[value])
        print ("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        for data in clusters[value]:
            print (data)
        print ("**********************************************************************")
