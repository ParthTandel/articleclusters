import nltk
import spacy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from gensim import corpora, models
from collections import defaultdict
from pymongo import MongoClient
client = MongoClient()
db = client.projectdb1
collection = db.articles
nlp = spacy.load('en')
from stopword_rm import stopwords

documents = []
count = 1


frequency = defaultdict(int)

data = collection.find({"type":"Entertainment"})
data_len = collection.find({"type":"Entertainment"}).count()
print data_len
for article in data:
    print article
    # texts = [str(word) for word in article["text"].lower().split() if str(word) not in stopwords]
    # documents.append(texts)

    # print article["count"]," ",article["link"]

    # print " ".join(texts)
    # tokens = nltk.word_tokenize(article["text"])
    doc = nlp(article["text"])
    # tagged = nltk.pos_tag(tokens)
    # entities = nltk.chunk.ne_chunk(tagged)
    # print tagged
    spacy_tokens = []
    for ent in doc.ents:
        # if ent.label_ == "PERSON":
        if str(ent.text.lower()) not in stopwords:
            # spacy_tokens.append(ent.text.lower())
            frequency[ent.text.lower()] = frequency[ent.text.lower()] + (article["text"]).lower().count(ent.text.lower())
            spacy_tokens.append(ent.text.lower())

    documents.append(spacy_tokens)
    print count
    count = count + 1
    texts = [word for word in article["text"].lower().split() if str(word) not in stopwords]
    documents.append(texts)
    # print texts
    # count = count + 1
    # if count == 10:
    #     break


# frequency = defaultdict(int)
#
# for text in documents:
#     for token in text:
#         frequency[str(token).lower()] += 1
#
# texts = [[str(token).lower() for token in text if frequency[str(token).lower()] > 1]for text in documents]
texts = documents
#
print texts
#
dictionary = corpora.Dictionary(texts)
dictionary.save('deerwester.dict')
# print(dictionary.token2id)
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('deerwester.mm', corpus)

# print frequency
# print dictionary
