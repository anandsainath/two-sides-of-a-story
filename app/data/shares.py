import json
import urllib
import sys
import utils

def get_social_counts(urlparam="http://www.google.com"):

	API_KEY = "8ca7bc67af37fe0affd10a53c818e431b8d8bfba"
	domain = "http://free.sharedcount.com/"
	params = { 'url' : urlparam, 'apikey' : API_KEY}

	url = domain + "?"+urllib.urlencode(params)
	return utils.get_json_response(url)