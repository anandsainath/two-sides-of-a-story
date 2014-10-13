import json
import urllib
import sys
import utils

API_KEY = "8ca7bc67af37fe0affd10a53c818e431b8d8bfba"

domain = "http://free.sharedcount.com/"

urlparam = "http://www.google.com"				#Default url parameter
if len(sys.argv)>1:
	urlparam = sys.argv[1]

params = { 'url' : urlparam, 'apikey' : API_KEY}

url = domain + "?"+urllib.urlencode(params)
json_output = utils.get_json_response(url)

for word in json_output:
	if word.lower()!="facebook":
		print word,json_output[word]
	else:
		print "\n"+word+":"
		for word1 in json_output[word]:
			print word1,json_output[word][word1]
		print "\n"


