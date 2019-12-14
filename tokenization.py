import spacy
import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
from stopword_rm import stopwords
from gensim import corpora, models
from collections import defaultdict
from pymongo import MongoClient

# connecting to ec2 mongodb
client = MongoClient("ec2-18-223-123-230.us-east-2.compute.amazonaws.com")
db = client.projectclean_db
collection = db.articles
nlp = spacy.load('en_core_web_sm')

documents = []
count = 1

frequency = defaultdict(int)

data = collection.find()
data_len = collection.find().count()
for article in data:
    article_text = article["text"].split(".")[3:]
    article_text = " ".join(article_text)
    article_text = article_text.split(" ")
    article_text = [str(word) for word in article_text if str(word) not in stopwords]
    article_text = " ".join(article_text)
    
    doc = nlp(article_text)
    
    spacy_tokens = []
    for ent in doc.ents:
        if ent.label_ == "PERSON" or ent.label_ == "GPE" or ent.label_ == "ORG":
            print(ent.text.lower())
            if str(ent.text.lower()) not in stopwords:
                frequency[ent.text.lower()] = frequency[ent.text.lower()] + (article_text).lower().count(ent.text.lower())
                spacy_tokens.append(ent.text.lower())
    
    documents.append(spacy_tokens)
   
texts = [[str(token).lower() for token in text if frequency[str(token).lower()] > 1] for text in documents]

dictionary = corpora.Dictionary(texts)
dictionary.save('deerwester.dict')

corpus = [dictionary.doc2bow(text) for text in texts]
print(corpus[0])
corpora.MmCorpus.serialize('deerwester.mm', corpus)
