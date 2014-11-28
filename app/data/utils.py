import json
import urllib2
import random
import cookielib
from bs4 import BeautifulSoup
import pickle
import re
from HTMLParser import HTMLParser
import requests

def get_json_response (url):
    response = urllib2.urlopen (url)
    response_string = response.read()
    js_object =  json.loads (response_string)
    return js_object

def get_nyt_article_search_url(params):
	url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?api-key="
	ARTICLE_SEARCH_API_KEY = ["318a69b2af97848f66071cb4c1fdc831:15:69992102", "353424482f2911b68847901e257ce797:18:69992139"]
	url += random.choice(ARTICLE_SEARCH_API_KEY)
	url += "&q="+params
	return url

def getData(url):
	html = ""
	try:
		response = urllib2.urlopen(url)
		html = response.read()
	except Exception:
		#cj = cookielib.CookieJar()
		#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		#request = urllib2.Request(url)
		#response = opener.open(request)
		#html = response.read()
		html = None
	return html

def getDataAsABrowserRequest(url):
	data = None
	header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
	try:
		data = requests.get(url, headers=header)
	except Exception:
		pass
	return data

def unpickle(filename):
	f = open(filename,"rb") 
	heroes = pickle.load(f)
	return heroes

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip(html):
    s = MLStripper()
    s.feed(html)
    t = s.get_data()
    t = re.sub('[^a-zA-Z ]+', '', t.lower())
    return t
