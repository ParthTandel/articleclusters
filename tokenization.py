import nltk
import spacy
from gensim import corpora, models
from collections import defaultdict
from pymongo import MongoClient
client = MongoClient()
db = client.test_database
collection = db.articles
nlp = spacy.load('en')
from stopword_rm import stopwords

documents = []
count = 0;
for article in collection.find():
    print article["type"]
    # texts = [word for word in article["text"].lower().split() if word not in stopwords]
    # documents.append(texts)

    # print article["count"]," ",article["link"]

    # print " ".join(texts)
    # tokens = nltk.word_tokenize(article["text"])
    doc = nlp(article["text"])
    # tagged = nltk.pos_tag(tokens)
    # entities = nltk.chunk.ne_chunk(tagged)
    # print tagged
    # spacy_tokens = []
    # print "********************************************************************"
    # for ent in doc.ents:
    #     if ent.label_ == "PERSON":
    #         # if ent.text not in spacy_tokens and ent.text.lower() not in stopwords:
    #         #     spacy_tokens.append(ent.text)
    #         spacy_tokens.append(ent.text)
    #         # print ent.text,article["text"].count(ent.text)
    #
    # print spacy_tokens
    #
    # documents.append(spacy_tokens)




    # texts = [word for word in article["text"].lower().split() if word not in stopwords]
    # documents.append(texts)



    # print "####################################################################"
    #
    # print "####################################################################"


        # print(ent.label_, ent.text)

    print "********************************************************************"
    # count = count + 1
    # if count == 10:
    #     break

# 
# frequency = defaultdict(int)
#
# for text in documents:
#     for token in text:
#         frequency[token] += 1
#
# texts = [[token for token in text if frequency[token] > 1]for text in documents]
#
# dictionary = corpora.Dictionary(texts)
# dictionary.save('deerwester.dict')
# print(dictionary.token2id)
# corpus = [dictionary.doc2bow(text) for text in texts]
# corpora.MmCorpus.serialize('deerwester.mm', corpus)
#
# print frequency
# print dictionary
