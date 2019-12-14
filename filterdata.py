import pymongo
import re
from newspaper import Article
from pymongo import MongoClient
from stopword_rm import stopwords

# connecting to ec2 mongodb
client = pymongo.MongoClient("ec2-18-223-123-230.us-east-2.compute.amazonaws.com")
db = client.projectdb   # database named test_database
collection = db.articles    # collection named articles


cleaned_db = client.projectclean_db   # database named test_database
final_collection = cleaned_db.articles    # collection named articles

try:
    count = final_collection.find({}).sort([('$natural',pymongo.DESCENDING)]).limit(1)[0]["count"]
except Exception:
    count = 1

data  = collection.find()

for article in data:
    try:
        print("********************************************************************")
        a = Article(article["link"])
        a.download()
        a.parse()
        text = a.text
        text_array = text.split("\n")
        new_arr = []

        for val in text_array:
            if val.count("Photos:") > 0 or val.count("Chat with us in Facebook Messenger") > 0 or val.count("Read or Share this story:") > 0 or \
            val.count("entertainment.news@bbc.co.uk") > 0 or val.count("newstips.usatoday.com") > 0:
                continue
            new_arr.append(val)

        text = " ".join(new_arr)
        text = re.sub("r'(https|http)*[:.]+\S+'", " ", text)
        text = re.sub("'s", " ", text)
        text = re.sub("CLOSE", " ", text)
        text = re.sub("USA TODAY", " ", text)
        text = re.sub("Post to Facebook", " ", text)
        text = re.sub("Image copyright Getty Images Image caption", " ", text)
        text = re.sub("Image copyright PA Image caption", " ", text)
        text = re.sub("Media playback is unsupported on your device Media caption This video has been removed for rights reasons", " ", text)
        text = re.sub("\(CNN\)", " ", text)
        text = re.sub("Story highlights", " ", text)
        article_text = re.sub("Read More", " ", text)

        article_tokens = [word for word in article_text.lower().split() if str(word.encode('utf-8')) not in stopwords]
        article["refinedtext"] = " ".join(article_tokens)
        article["count"] = count
        if len( article_tokens ) > 150:
            print (final_collection.insert_one(article).inserted_id,article["link"], count)
            count = count + 1
        print ("********************************************************************")
    except Exception as e:
        print("Error: ", str(e))