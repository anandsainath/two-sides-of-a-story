import json
import urllib2

def get_json_response (url):
    response = urllib2.urlopen (url)
    response_string = response.read()
    js_object =  json.loads (response_string)
    return js_object
