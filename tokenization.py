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
for article in data:
    article_text = article["text"].split(".")[3:]
    article_text = [str(word) for word in article_text if str(word) not in stopwords]
    article_text = "".join(article_text)
    # texts = [str(word) for word in article_text.lower().split() if str(word) not in stopwords]
    # documents.append(texts)

    # print article["count"]," ",article["link"]

    # print " ".join(texts)
    # tokens = nltk.word_tokenize(article["text"])

    doc = nlp(unicode(article_text))
    # tagged = nltk.pos_tag(tokens)
    # entities = nltk.chunk.ne_chunk(tagged)
    # print tagged
    spacy_tokens = []
    for ent in doc.ents:
        if ent.label_ == "PERSON" or ent.label_ == "GPE" or ent.label_ == "ORG":
            print (ent.text, ent.label_)
            if str(ent.text.lower()) not in stopwords:
                frequency[ent.text.lower()] = frequency[ent.text.lower()] + (article_text).lower().count(ent.text.lower())
                spacy_tokens.append(ent.text.lower())
    #
    documents.append(spacy_tokens)
    # print count
    # count = count + 1
    # print "***************************************************************************"
    # texts = [word for word in article_text.lower().split() if str(word) not in stopwords]

    # for word in spacy_tokens:
    #     print word

    # print "***************************************************************************"

    # documents.append(texts)
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
texts = [[str(token).lower() for token in text if frequency[str(token).lower()] > 1]for text in documents]

#
# will_count = 0
# trump_count = 0
# facebook_count = 0
# news_count = 0
#
#
# for data in texts:
#     print "***************************************************************************"
#
#     trump_true = False
#     facebook_true = False
#     will_true = False
#     news_true = False
#
#
#     for word in data:
#         print word
#
#         if word.lower() == "trump" and trump_true == False:
#             trump_count = trump_count + 1
#             trump_true = True
#
#         if word.lower() == "will" and will_true == False:
#             will_count = will_count + 1
#             will_true = True
#
#
#         if word.lower() == "facebook" and facebook_true == False:
#             facebook_count = facebook_count + 1
#             facebook_true = True
#
#         if word.lower() == "news" and news_true == False:
#             news_count = news_count + 1
#             news_true = True
#
#     print "***************************************************************************"
# #
# print trump_count
# print will_count
# print facebook_count
# print news_count

# texts = documents
# #
# print texts
# #
dictionary = corpora.Dictionary(texts)
dictionary.save('deerwester.dict')
# print(dictionary.token2id)
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('deerwester.mm', corpus)
#
# print frequency
# print dictionary
