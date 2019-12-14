import pymongo

# connecting to local localhost
# client = pymongo.MongoClient()


# connecting to ec2

client = pymongo.MongoClient("ec2-18-223-123-230.us-east-2.compute.amazonaws.com")



db = client.projectdb
collection = db.articles


data = collection.find()

print(data.count())

for article in data:
    print(article["text"])
    break
