from bs4 import BeautifulSoup
import urllib2
import httplib
import feedparser
import csv
import re
import datetime
import pymongo

client = pymongo.MongoClient()
db = client.projectdb   # database named test_database
collection = db.articles    # collection named articles


try:
    count = collection.find({}).sort([('$natural',pymongo.DESCENDING)]).limit(1)[0]["count"]
except Exception:
    count = 0

with open('rss.csv', 'rb') as csvfile:
    rssfeeds = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in rssfeeds:
        link = row[2]
        d = feedparser.parse(link)
        for newsitem in d['entries']:
            try:
                count = count + 1
                response = urllib2.urlopen(newsitem['links'][0]['href'])
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')

                for script in soup.find_all('script'):
                    script.extract()
                for script in soup.find_all('style'):
                    script.extract()

                data_dict = {
                    "count" : count,
                    "date"  : datetime.datetime.now().strftime("%y-%m-%d"),
                    "text"  : soup.get_text(strip=True),
                    "type"  : row[1],
                    "link"  : newsitem['links'][0]['href']
                }

                print count,collection.insert_one(data_dict).inserted_id,newsitem['links'][0]['href']

            except urllib2.HTTPError, e:
                print 'HTTPError = ' + str(e.code)
            except urllib2.URLError, e:
                print 'URLError = ' + str(e.reason)
            except httplib.HTTPException, e:
                print 'HTTPException'
            except pymongo.errors.DuplicateKeyError, e:
                print "duplicate key"
                count = count - 1
            except Exception:
                print "ERROR"



        # print d['feed']['links']
        # news = newspaper.build(link,
        #                         language="en",
        #                         memoize_articles=False)
        # print len(news.articles)
        # print "***************************"
        # for article in news.articles:
        #     print article.url


#             response = urllib2.urlopen(article.url)
#             html = response.read()
#             print "*********************************************"
#             soup = BeautifulSoup(html, 'html.parser')
#             for script in soup.find_all('script'):
#                 script.extract()
#             soup.prettify()
#             # data = soup.find_all('div', attrs = {"class":"story-body"})
#             # for text in data:
#             tokens = nltk.word_tokenize(soup.get_text(strip=True))
#             doc = nlp(soup.get_text(strip=True))
#
#             # print tokens
#             for ent in doc.ents:
#                 print(ent.label_, ent.text)
#             print "*********************************************"
#
#
# # links = {
# # "nytimessports"     : "http://rss.nytimes.com/services/xml/rss/nyt/Sports.xml"
# # }
#
#
# # nlp = spacy.load('en')
# # for link in links.keys():
# #     news = newspaper.build(links[link],
# #                             language="en",
# #                             memoize_articles=False)
# #     for article in news.articles:
# #         response = urllib2.urlopen(article.url)
# #         html = response.read()
# #         print "*********************************************"
# #         soup = BeautifulSoup(html, 'html.parser')
# #         for script in soup.find_all('script'):
# #             script.extract()
# #         soup.prettify()
# #         data = soup.find_all('div', attrs = {"class":"story-body"})
# #         for text in data:
# #             # print text.get_text(strip=True)
# #             tokens = nltk.word_tokenize(text.get_text(strip=True))
# #             tagged = nltk.pos_tag(tokens)
# #             print tagged
# #             # doc = nlp(text.get_text(strip=True))
# #             # print(doc[0].text, doc[0].ent_iob, doc[0].ent_type_)
# #             #
# #             # print text.get_text(strip=True)
# #         print "*********************************************"
