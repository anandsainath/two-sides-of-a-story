import json
import urllib
import sys
import utils
import random

def get_social_counts(urlparam="http://www.google.com"):

	API_KEY = ["8ca7bc67af37fe0affd10a53c818e431b8d8bfba", "115a154ac6fe21c051c0346cbebf42d9a5a00c8d"]
	domain = "http://free.sharedcount.com/"
	params = { 'url' : urlparam, 'apikey' : random.choice(API_KEY)}

	url = domain + "?"+urllib.urlencode(params)
	return utils.get_json_response(url)