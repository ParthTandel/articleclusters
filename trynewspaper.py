import pymongo
import re
import urllib2
import httplib
import spacy
from newspaper import Article
from pymongo import MongoClient
from boilerpipe.extract import Extractor
nlp = spacy.load('en')
from stopword_rm import stopwords
from collections import defaultdict
from gensim import corpora,models, similarities




client = MongoClient()

db = client.projectdb
collection = db.articles

new_db = client.projectdb1
new_collection = new_db.articles

new_db_np = client.projectdb_np
new_collectionnp = new_db_np.articles

data  = new_collectionnp.find({"type":"Entertainment"})
# data1 = new_collection.find({"type":"Entertainment"})
# data2 = new_collection2.find({"type":"Entertainment"})
documents = []
frequency = defaultdict(int)
test = []

for article in data:
    print "********************************************************************"
    a = Article(article["link"])
    a.download()
    a.parse()
    text = a.text
    text_array = text.split("\n")
    new_arr = []

    for val in text_array:
        if val.count("Photos:") > 0 or val.count("Chat with us in Facebook Messenger") > 0 or val.count("Read or Share this story:") > 0 or val.count("entertainment.news@bbc.co.uk") > 0 or val.count("newstips.usatoday.com") > 0:
            continue
        new_arr.append(val)

    text = " ".join(new_arr)
    text = re.sub("CLOSE", " ", text)
    text = re.sub("USA TODAY", " ", text)
    text = re.sub("Post to Facebook", " ", text)
    text = re.sub("Image copyright Getty Images Image caption", " ", text)
    text = re.sub("Image copyright PA Image caption", " ", text)
    text = re.sub("Media playback is unsupported on your device Media caption This video has been removed for rights reasons", " ", text)
    text = re.sub("\(CNN\)", " ", text)
    text = re.sub("Story highlights", " ", text)
    article_text = re.sub("Read More", " ", text)



    # article_text = join(article_text).encode('utf-8').strip()

    article_text = article["text"]
    doc = nlp(unicode(article_text))


    spacy_tokens = []
    # spacy_tokens = [word for word in article_text.lower().split() if word not in stopwords]

    for ent in doc.ents:
        if ent.label_ == "PERSON" or ent.label_ == "ORG":
            print (ent.text, ent.label_)
            if ent.text.lower() not in stopwords:
                frequency[ent.text.lower()] = frequency[ent.text.lower()] + (article_text).lower().count(ent.text.lower())
                spacy_tokens.append(ent.text.lower())
    documents.append(spacy_tokens)
    test.append({"spacy_tokens" : spacy_tokens,
                "count" : article["count"]})


    # article['text'] = article_text
    #
    #
    # print new_collectionnp.insert_one(article).inserted_id,article["link"]
    print article_text
    print "********************************************************************"

frequency = defaultdict(int)

for text in documents:
    for token in text:
        frequency[token.lower()] += 1

# texts = [[token.lower() for token in text if frequency[token.lower()] > 1]for text in documents]

texts = documents
dictionary = corpora.Dictionary(texts)
# # dictionary.save('deerwester.dict')
# # print(dictionary.token2id)
corpus = [dictionary.doc2bow(text) for text in texts]
model = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=12)

topics = model.print_topics(12)
for topic in topics:
    print topic

clusters = {}
for i in xrange(0,12):
    clusters[i] = []

# for data in model[corpus]:
#     print data


for data in test:
    spacy_tokens = data["spacy_tokens"]
    query = dictionary.doc2bow(spacy_tokens)
    print data['count'],model[query]
    similarity = model[query]
    for val in similarity:
        if val[1] > 0.9:
            clusters[val[0]].append({
                "id" : data["count"],
                "token" : spacy_tokens
            })



for value in clusters.keys():
    print "**********************************************************************"
    print topics[value]
    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    for data in clusters[value]:
        print data
    print "**********************************************************************"



# corpora.MmCorpus.serialize('deerwester.mm', corpus)
