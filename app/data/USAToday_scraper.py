import urllib2
from bs4 import BeautifulSoup
from datetime import date,timedelta,datetime
import json
import time
from pymongo import MongoClient
import sys

client = MongoClient()

db = client.socomp

collection = db.gun_control_document_corpus

to_date = date(2014,12,1)

api_attempt = 0
article_count = 0
i = 0
while i < 365:
    try:
        time.sleep(2)
        to_date_string = to_date.strftime('%Y-%m-%d')
        from_date_string = (to_date - timedelta(days=1)).strftime('%Y-%m-%d')
        print 'parsing for dates between '+from_date_string+' and '+to_date_string
        api_call = 'http://api.usatoday.com/open/articles?section=politics&keyword=Gun%20Control&fromdate='+from_date_string+'&todate='+to_date_string+'&count=100&api_key=9acjxqsb78rwx576s5w8k3gq&encoding=json'
        to_date = to_date - timedelta(days=2)
        response = urllib2.urlopen(api_call)
        results = json.load(response)
        articles = results['stories']
        attempt = 0
        api_attempt = 0
        j = 0
        while j < len(articles):
            article = articles[j]
            opener = urllib2.build_opener()

            headers = {
                      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
                      }

            opener.addheaders = headers.items()
            try:
                response = opener.open(article['link'])
                html = response.read()

                soup = BeautifulSoup(html)

                article_body = soup.find(itemprop='articleBody').find_all('p',recursive=False)

                article_text = ''
                for paragraph in article_body:
                    article_text += paragraph.get_text()

                post = {}

                post['web_url'] = article['link']
                post['source'] = 'USA Today'
                post['headline'] = article['title']
                post['political_leaning'] = 'Unknown'
                post['pub_date'] = datetime.strptime(article['pubDate'],'%a, %d %b %Y %X GMT')
                post['content'] = article_text

                collection.insert(post)
                attempt = 0
                j += 1
            except:
                print 'Encountered error:', sys.exc_info()[0]
                if attempt < 5:
                    attempt += 1
                    print 'Will retry after sleeping for 5 seconds. Attempt',attempt
                    time.sleep(5)
                else:
                    print '5 attempts done. Will skip article'
                    attempt = 0
                    j += 1
                pass
        article_count += len(articles)
        print 'Number of articles inserted:',len(articles)
        i += 1
    except:
        print 'Encountered error in API call:', sys.exc_info()[0]
        if api_attempt < 5:
            api_attempt += 1
            print 'Will retry. Attempt',api_attempt
            print 'For URL',api_call
            time.sleep(3)
            to_date = to_date + timedelta(days=2)
        else:
            print '5 attempts done. Will skip day'
            api_attempt = 0
            i += 1
        pass
print 'Total articles parsed',article_count
