import pymongo
from pymongo import MongoClient
from boilerpipe.extract import Extractor
client = MongoClient()

db = client.projectdb
collection = db.articles


new_db = client.projectdb1
new_collection = new_db.articles

data = collection.find({"type":"Entertainment"})
for article in data:
    extractor = Extractor(extractor='ArticleExtractor', url=article["link"])
    extracted_text = extractor.getText()
    article["text"] = extracted_text

    try:
        print new_collection.insert_one(article).inserted_id,article["link"]

    except pymongo.errors.DuplicateKeyError, e:
        print "duplicate key"
    except Exception:
        print "ERROR"
