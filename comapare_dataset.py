import pymongo


client = pymongo.MongoClient()

# db = client.projectdb
# collection = db.articles

# new_db_2 = client.projectdb2
# new_collection = new_db_2.articles



new_db = client.projectdb1
new_collection = new_db.articles

data = new_collection.find({"type":"Entertainment"})
for article in data:
    print "********************************************************************"
    print "".join(article["text"])
    print "&&&&&&&&&&&"
    print "".join(article["text"]).lower().count("trump")
    print "********************************************************************"
