from bs4 import BeautifulSoup
import urllib
import feedparser
import csv
import re
import datetime
import pymongo
import os

client = pymongo.MongoClient()
db = client.projectdb   # database named test_database
collection = db.articles    # collection named articles

try:
    count = collection.find({}).sort([('$natural',pymongo.DESCENDING)]).limit(1)[0]["count"]
except Exception:
    count = 0

filename = os.path.join(os.path.dirname(__file__), 'rss.csv')

with open(filename, 'r') as csvfile:
    rssfeeds = csv.reader(csvfile, delimiter=',', quotechar='"')

    for row in rssfeeds:
        link = row[2]

        d = feedparser.parse(link)
        for newsitem in d['entries']:
            try:
                count = count + 1

                response = urllib.request.urlopen(newsitem['links'][0]['href'])
                html = response.read()

                soup = BeautifulSoup(html, 'html.parser')
                
                for script in soup.find_all('script'):
                    script.extract()

                for style in soup.find_all('style'):
                    style.extract()

                data_dict = {
                    "count" : count,
                    "date"  : datetime.datetime.now().strftime("%y-%m-%d"),
                    "text"  : soup.get_text(strip=True),
                    "type"  : row[1],
                    "link"  : newsitem['links'][0]['href']
                }

                print(count,collection.insert_one(data_dict).inserted_id,newsitem['links'][0]['href'])

            except pymongo.errors.DuplicateKeyError as e:
                print("duplicate key")
                count = count - 1
            except Exception as e:
                print(str(e))
